import sys
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def get_coordinates(address, country_code=None, count=10, language='en'):
    """Return a list of coordinates for a given address using Open-Meteo geocoding."""
    params = {
        'name': address,
        'count': count,
        'language': language,
        'format': 'json',
    }
    if country_code:
        params['countryCode'] = country_code.upper()

    url = 'https://geocoding-api.open-meteo.com/v1/search?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'python-urllib/3'})

    with urlopen(request, timeout=10) as response:
        data = json.load(response)

    results = data.get('results') or []

    return [
        {
            'name': item.get('name'),
            'latitude': item.get('latitude'),
            'longitude': item.get('longitude'),
            'country': item.get('country'),
            'admin1': item.get('admin1'),
            'admin2': item.get('admin2'),
            'timezone': item.get('timezone'),
        }
        for item in results
    ]


def get_weather(latitude=52.52, longitude=13.41, parameters='temperature_2m,precipitation_probability'):
    """Return weather forecast from Open-Meteo for the given coordinates."""
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': parameters
    }
    url = 'https://api.open-meteo.com/v1/forecast?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'python-urllib/3'})

    with urlopen(request, timeout=10) as response:
        data = json.load(response)

    return data

def get_weather_forecast(location_name, country_code, language_code='en'):
    """Get weather forecast for a given address."""
    coordinates_list = get_coordinates(location_name, country_code, language=language_code.lower())
    if not coordinates_list:
        print(f'No coordinates found for location: {location_name}')
        return None

    # Use the first result for weather forecast
    first_result = coordinates_list[0]
    latitude = first_result['latitude']
    longitude = first_result['longitude']

    weather_data = get_weather(latitude, longitude)
    return {
        'location': first_result,
        'weather': weather_data
    }

if __name__ == "__main__":
    func_name = sys.argv[1]
    args = sys.argv[2:]
    globals()[func_name](*args)