import sys
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def get_coordinates(address, country_code=None, count=10, language='en'):
    """Return a list of coordinates for a given address using Open-Meteo geocoding.

    Args:
        address (str): The address or location name to search for
        country_code (str, optional): ISO country code to filter results (e.g., 'FR', 'US')
        count (int, optional): Maximum number of results to return. Defaults to 10.
        language (str, optional): Language for result names. Defaults to 'en'.

    Returns:
        list: List of dictionaries containing location details (name, lat/long, country, etc.)
    """
    # Build query parameters for the geocoding API
    params = {
        'name': address,
        'count': count,
        'language': language,
        'format': 'json',
    }
    if country_code:
        params['countryCode'] = country_code.upper()
        # Ensure uppercase for country codes

    # Construct the API URL and create a request with User-Agent header
    url = 'https://geocoding-api.open-meteo.com/v1/search?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'python-urllib/3'})

    # Fetch and parse the JSON response
    with urlopen(request, timeout=10) as response:
        data = json.load(response)

    results = data.get('results') or []
    # Handle empty/None results gracefully

    # Extract relevant fields from each result and return as a simplified list
    return [
        {
            'name': item.get('name'),
            'latitude': item.get('latitude'),
            'longitude': item.get('longitude'),
            'country': item.get('country'),
            'admin1': item.get('admin1'),  # Region/state level
            'admin2': item.get('admin2'),  # County/district level
            'timezone': item.get('timezone'),
        }
        for item in results
    ]


def get_weather(latitude=52.52, longitude=13.41, parameters='temperature_2m,precipitation_probability'):
    """Return weather forecast from Open-Meteo for the given coordinates.

    Args:
        latitude (float, optional): Latitude coordinate. Defaults to 52.52 (Berlin).
        longitude (float, optional): Longitude coordinate. Defaults to 13.41 (Berlin).
        parameters (str, optional): Comma-separated list of weather parameters.
            See Open-Meteo docs for available options. Defaults to temperature and precipitation.

    Returns:
        dict: Raw weather data from the Open-Meteo API
    """
    # Build API parameters
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': parameters  # Request hourly data for specified parameters
    }
    url = 'https://api.open-meteo.com/v1/forecast?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'python-urllib/3'})

    # Fetch and return the full weather data response
    with urlopen(request, timeout=10) as response:
        data = json.load(response)

    return data

def get_weather_forecast(location_name, country_code, language_code='en'):
    """This is a convenience function that combines geocoding and weather lookup.

    Args:
        location_name (str): Name of the location to search for
        country_code (str): ISO country code to narrow down the search
        language_code (str, optional): Language for location names. Defaults to 'en'.

    Returns:
        dict: Combined result with location details and weather data, or None if not found
            Structure: {
                'location': { ... },  # First geocoding result
                'weather': { ... }     # Full weather data for that location
            }
    """
    # Step 1: Convert location name to coordinates
    coordinates_list = get_coordinates(location_name, country_code, language=language_code.lower())
    if not coordinates_list:
        print(f'No coordinates found for location: {location_name}')
        return location_name + " (" + country_code + ") not found"

    # Step 2: Use the first (most relevant) result for weather lookup
    first_result = coordinates_list[0]
    latitude = first_result['latitude']
    longitude = first_result['longitude']

    # Step 3: Fetch weather data for the coordinates
    weather_data = get_weather(latitude, longitude)
    return {
        'location': first_result,
        'weather': weather_data
    }

# Allow this module to be run as a script for testing purposes
# Usage: python weather.py <function_name> [args...]
# Example: python weather.py get_weather_forecast "Paris" FR
if __name__ == "__main__":
    func_name = sys.argv[1]
    args = sys.argv[2:]
    globals()[func_name](*args)