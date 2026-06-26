import requests
import json


def search(query, api_key=None, search_depth="basic", include_domains=[], exclude_domains=[], max_results=5):
    """Search the web using Tavily Search API.

    Args:
        query (str): The search query string
        api_key (str, optional): Tavily API key. If not provided, will try to get it from environment variables.
        search_depth (str, optional): Search depth - "basic" or "advanced". Defaults to "basic".
        include_domains (list, optional): List of domains to include in search results
        exclude_domains (list, optional): List of domains to exclude from search results
        max_results (int, optional): Maximum number of results to return. Defaults to 5.

    Returns:
        dict: Search results containing:
            - query: The search query
            - results: List of result items with title, url, content, score, etc.
            - answer: AI-generated answer (if available)
            - response_time: Time taken for the search
            Or None if the request failed
    """
    # API endpoint
    url = "https://api.tavily.com/search"

    # Get API key
    if api_key is None:
        import os
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key is None:
            raise ValueError("Tavily API key is required. Pass it as parameter or set TAVILY_API_KEY environment variable.")

    # Build request payload
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
        "max_results": max_results
    }

    # Build headers
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send POST request to Tavily API
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Tavily Search API: {str(e)}")
        return None

