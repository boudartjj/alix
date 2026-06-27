import requests
import os


def get_news(query=None, language="fr", country=None, category=None, sources=None, page_size=20, api_key=None):
    """Fetch news articles using NewsAPI.

    Args:
        query (str, optional): Keywords or phrases to search for in article content
        language (str, optional): Language of the articles (ISO 639-1 code). Defaults to "en".
        country (str, optional): Country code (ISO 3166-1 alpha-2) to filter by country
        category (str, optional): News category - "business", "entertainment", "general", "health", "science", "sports", "technology"
        sources (str, optional): Comma-separated list of news sources to filter by
        page_size (int, optional): Number of results to return (max 100). Defaults to 5.
        api_key (str, optional): NewsAPI key. If not provided, will try to get it from NEWS_API_KEY environment variable.

    Returns:
        dict: News articles containing:
            - status: API response status
            - total_results: Total number of results available
            - articles: List of articles with:
                - source: News source information
                - author: Article author
                - title: Article title
                - description: Article description
                - url: Article URL
                - url_to_image: URL of article image
                - published_at: Publication date
                - content: Article content
            Or None if the request failed
    """
    # API endpoint
    url = "https://newsapi.org/v2/everything"

    # Get API key
    if api_key is None:
        api_key = os.getenv("NEWSAPI_KEY")
        if api_key is None:
            raise ValueError("NewsAPI key is required. Pass it as parameter or set NEWSAPI_KEY environment variable.")

    # Build query parameters
    params = {
        "apiKey": api_key,
        "pageSize": min(page_size, 100),  # NewsAPI max is 100
        "language": language
    }

    # Add optional parameters if provided
    if query is not None:
        params["q"] = query
    if country is not None:
        params["country"] = country
    if category is not None:
        params["category"] = category
    if sources is not None:
        params["sources"] = sources

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling NewsAPI: {str(e)}")
        return None
