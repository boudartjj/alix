"""
Memory module for managing vector database with Redis.
Provides tools for storing, retrieving, and searching embeddings.
"""

import redis
import json
import numpy as np
from typing import Optional, Dict, Any, List
import hashlib


class MemoryManager:
    """Manages vector embeddings in Redis for agent memory."""
    
    # Default provider configurations for OpenAI-compatible endpoints
    DEFAULT_PROVIDERS = {
        'openai': {
            'url': 'https://api.openai.com/v1/embeddings',
            'headers': {'Authorization': 'Bearer {api_key}'},
            'env_key': 'OPENAI_API_KEY',
            'default_model': 'text-embedding-ada-002',
            'dimension': 1536
        },
        'mistral': {
            'url': 'https://api.mistral.ai/v1/embeddings',
            'headers': {'Authorization': 'Bearer {api_key}'},
            'env_key': 'MISTRAL_API_KEY',
            'default_model': 'mistral-embedding',
            'dimension': 384
        }
    }
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, 
                 embedding_config=None, embedding_model=None, api_key=None):
        """
        Initialize the memory manager.
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            embedding_config: Embedding configuration. Can be:
                - String: predefined provider name ('openai', 'mistral')
                - Dict: custom configuration with keys:
                    * url: API endpoint URL
                    * headers: dict of headers (use {api_key} for key placeholder)
                    * env_key: environment variable name for API key
                    * default_model: default model name
                    * dimension: embedding dimension size
            embedding_model: Embedding model to use (overrides config default)
            api_key: API key for the embedding provider
        """
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        
        # Set up embedding configuration
        self.embedding_config = self._resolve_embedding_config(embedding_config)
        
        # Use provided model or fall back to config default
        self.embedding_model = embedding_model or self.embedding_config.get('default_model', 'text-embedding-ada-002')
        self.api_key = api_key
        self.embedding_dim = self.embedding_config.get('dimension', 1536)
    
    def _resolve_embedding_config(self, config):
        """Resolve embedding configuration from string or dict."""
        if config is None:
            # Default to OpenAI
            return self.DEFAULT_PROVIDERS['openai'].copy()
        
        if isinstance(config, str):
            # Look up predefined provider
            if config not in self.DEFAULT_PROVIDERS:
                raise ValueError(f"Unknown provider: {config}. "
                               f"Predefined: {list(self.DEFAULT_PROVIDERS.keys())}")
            return self.DEFAULT_PROVIDERS[config].copy()
        
        if isinstance(config, dict):
            # Custom configuration - validate required fields
            required = ['url']
            missing = [f for f in required if f not in config]
            if missing:
                raise ValueError(f"Embedding config missing required fields: {missing}")
            # Set defaults for optional fields
            defaults = {
                'headers': {'Authorization': 'Bearer {api_key}'},
                'env_key': 'EMBEDDING_API_KEY',
                'default_model': 'text-embedding-ada-002',
                'dimension': 1536
            }
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            return config
        
        raise ValueError(f"Invalid embedding_config type: {type(config)}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using the configured embedding API."""
        import requests
        import os
        
        config = self.embedding_config
        
        # Get API key from instance, environment, or raise error
        api_key = self.api_key or os.getenv(config.get('env_key', 'EMBEDDING_API_KEY'))
        if not api_key:
            raise ValueError(f"API key is required. Set {config.get('env_key', 'EMBEDDING_API_KEY')} "
                           f"environment variable or pass api_key parameter.")
        
        # Build headers - replace {api_key} placeholder
        headers = {}
        for header_name, header_value in config.get('headers', {}).items():
            headers[header_name] = header_value.format(api_key=api_key)
        headers["Content-Type"] = "application/json"
        
        # Build data payload - standard OpenAI-compatible format
        data = {
            "model": self.embedding_model,
            "input": text
        }
        
        # Make request to the configured endpoint
        response = requests.post(config['url'], headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        # Parse response - standard OpenAI format
        response_data = response.json()
        embedding = response_data["data"][0]["embedding"]
        
        return embedding
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for the text using hash."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None, 
                  custom_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a text memory to the vector database.
        
        Args:
            text: The text content to store
            metadata: Optional metadata dictionary
            custom_id: Optional custom ID (if not provided, generated from text)
            
        Returns:
            Dictionary with id, text, metadata, and status
        """
        try:
            embedding = self._generate_embedding(text)
            memory_id = custom_id or self._generate_id(text)
            
            # Store the embedding vector
            vector_key = f"vec:{memory_id}"
            self.redis_client.set(vector_key, json.dumps(embedding))
            
            # Store metadata
            meta_key = f"meta:{memory_id}"
            metadata = metadata or {}
            metadata['text'] = text
            self.redis_client.set(meta_key, json.dumps(metadata))
            
            # Add to index for searching
            self.redis_client.sadd("memory_index", memory_id)
            
            return {
                "status": "success",
                "id": memory_id,
                "text": text,
                "metadata": metadata
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def search_memory(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory by similarity to the query.
        
        Args:
            query: The search query text
            k: Number of results to return
            
        Returns:
            List of matching memories with scores
        """
        try:
            query_embedding = self._generate_embedding(query)
            query_vector = np.array(query_embedding)
            
            # Get all memory IDs
            memory_ids = self.redis_client.smembers("memory_index")
            
            results = []
            for mem_id in memory_ids:
                mem_id = mem_id.decode()
                vec_key = f"vec:{mem_id}"
                vector_data = self.redis_client.get(vec_key)
                if vector_data:
                    stored_embedding = json.loads(vector_data)
                    stored_vector = np.array(stored_embedding)
                    
                    # Calculate cosine similarity
                    dot_product = np.dot(query_vector, stored_vector)
                    norm_q = np.linalg.norm(query_vector)
                    norm_s = np.linalg.norm(stored_vector)
                    similarity = dot_product / (norm_q * norm_s)
                    
                    # Get metadata
                    meta_key = f"meta:{mem_id}"
                    metadata = json.loads(self.redis_client.get(meta_key) or '{}')
                    
                    results.append({
                        "id": mem_id,
                        "text": metadata.get('text', ''),
                        "metadata": metadata,
                        "score": float(similarity)
                    })
            
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            return [{"status": "error", "error": str(e)}]
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: The memory ID
            
        Returns:
            Memory data or None if not found
        """
        try:
            meta_key = f"meta:{memory_id}"
            metadata = self.redis_client.get(meta_key)
            if metadata:
                return json.loads(metadata)
            return None
        except Exception:
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from the database.
        
        Args:
            memory_id: The memory ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis_client.delete(f"vec:{memory_id}")
            self.redis_client.delete(f"meta:{memory_id}")
            self.redis_client.srem("memory_index", memory_id)
            return True
        except Exception:
            return False
    
    def update_memory(self, memory_id: str, new_text: str, 
                      new_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing memory entry.
        
        Args:
            memory_id: The memory ID to update
            new_text: New text content
            new_metadata: Optional new metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete old embedding
            self.redis_client.delete(f"vec:{memory_id}")
            
            # Add new embedding
            embedding = self._generate_embedding(new_text)
            self.redis_client.set(f"vec:{memory_id}", json.dumps(embedding))
            
            # Update metadata
            metadata = new_metadata or {}
            metadata['text'] = new_text
            self.redis_client.set(f"meta:{memory_id}", json.dumps(metadata))
            
            return True
        except Exception:
            return False


# Global memory manager instance (lazy initialization)
_memory_manager = None


def get_memory_manager(redis_host='localhost', redis_port=6379, redis_db=0,
                      embedding_config=None, embedding_model=None, 
                      api_key=None):
    """Get or create the global memory manager instance.
    
    Args:
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        embedding_config: Embedding configuration. Can be:
            - String: predefined provider name ('openai', 'mistral')
            - Dict: custom OpenAI-compatible configuration
        embedding_model: Embedding model to use (overrides config default)
        api_key: API key for the embedding provider
        
    Returns:
        MemoryManager instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db,
            embedding_config=embedding_config,
            embedding_model=embedding_model,
            api_key=api_key
        )
    return _memory_manager


def add_memory(text: str, metadata: Optional[Dict[str, Any]] = None, 
               custom_id: Optional[str] = None, redis_host='localhost', 
               redis_port=6379, redis_db=0, embedding_config=None,
               embedding_model=None, api_key=None) -> Dict[str, Any]:
    """
    Add a text memory to the vector database.
    
    Args:
        text: The text content to store
        metadata: Optional metadata dictionary
        custom_id: Optional custom ID
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        embedding_config: Embedding configuration (string provider name or dict)
        embedding_model: Embedding model to use (overrides config default)
        api_key: API key for the embedding provider
        
    Returns:
        Dictionary with status, id, text, and metadata
    """
    manager = get_memory_manager(redis_host, redis_port, redis_db, 
                                embedding_config, embedding_model, api_key)
    return manager.add_memory(text, metadata, custom_id)


def search_memory(query: str, k: int = 5, redis_host='localhost', 
                redis_port=6379, redis_db=0, embedding_config=None,
                embedding_model=None, api_key=None) -> List[Dict[str, Any]]:
    """
    Search memory by similarity to the query.
    
    Args:
        query: The search query text
        k: Number of results to return
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        embedding_config: Embedding configuration (string provider name or dict)
        embedding_model: Embedding model to use (overrides config default)
        api_key: API key for the embedding provider
        
    Returns:
        List of matching memories with scores
    """
    manager = get_memory_manager(redis_host, redis_port, redis_db, 
                                embedding_config, embedding_model, api_key)
    return manager.search_memory(query, k)


def get_memory_entry(memory_id: str, redis_host='localhost', 
                    redis_port=6379, redis_db=0) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific memory by ID.
    
    Args:
        memory_id: The memory ID
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        
    Returns:
        Memory data or None if not found
    """
    manager = get_memory_manager(redis_host, redis_port, redis_db)
    return manager.get_memory(memory_id)


def delete_memory_entry(memory_id: str, redis_host='localhost', 
                       redis_port=6379, redis_db=0) -> bool:
    """
    Delete a memory from the database.
    
    Args:
        memory_id: The memory ID to delete
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        
    Returns:
        True if successful, False otherwise
    """
    manager = get_memory_manager(redis_host, redis_port, redis_db)
    return manager.delete_memory(memory_id)


def update_memory_entry(memory_id: str, new_text: str, 
                       new_metadata: Optional[Dict[str, Any]] = None, 
                       redis_host='localhost', redis_port=6379, 
                       redis_db=0, embedding_config=None,
                       embedding_model=None, api_key=None) -> bool:
    """
    Update an existing memory entry.
    
    Args:
        memory_id: The memory ID to update
        new_text: New text content
        new_metadata: Optional new metadata
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        embedding_config: Embedding configuration (string provider name or dict)
        embedding_model: Embedding model to use (overrides config default)
        api_key: API key for the embedding provider
        
    Returns:
        True if successful, False otherwise
    """
    manager = get_memory_manager(redis_host, redis_port, redis_db, 
                                embedding_config, embedding_model, api_key)
    return manager.update_memory(memory_id, new_text, new_metadata)
