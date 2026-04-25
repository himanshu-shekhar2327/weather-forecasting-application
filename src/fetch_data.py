import requests
import pandas as pd
from datetime import datetime


def fetch_weather(lat, lon):
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': '1990-01-01',
        'end_date':   datetime.today().strftime('%Y-%m-%d'),
        'daily':      'temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max',
        'timezone':   'Asia/Kolkata'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'daily' not in data:
            reason = data.get('reason', 'unknown error')
            print(f"  API error: {reason}")
            return None

        df = pd.DataFrame(data['daily'])
        return df

    except requests.exceptions.Timeout:
        print(f"  Request timed out")
        return None

    except requests.exceptions.ConnectionError:
        print(f"  Connection error")
        return None

    except Exception as e:
        print(f"  Unexpected error: {e}")
        return None


def fetch_recent_weather(lat, lon, days=30):
    """
    Fetches only recent N days of weather.
    Used at runtime for unknown cities —
    builds lag features without historical data.
    """
    from datetime import timedelta
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=days)

    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date':   end_date.strftime('%Y-%m-%d'),
        'daily':      'temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max',
        'timezone':   'Asia/Kolkata'
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if 'daily' not in data:
        print(f"API error: {data.get('reason', 'unknown error')}")
        return None

    df = pd.DataFrame(data['daily'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    return df


def get_coordinates(place_name):
    """
    Used at runtime when user types unknown city.
    Returns lat, lon, elevation, and display name.
    """
    search_query = f'{place_name}, india'
    url = 'https://geocoding-api.open-meteo.com/v1/search'
    params = {
        'name':     search_query,
        'count':    10,
        'language': 'en',
        'format':   'json',
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if 'results' not in data:
        return None

    for r in data['results']:
        if r.get('country_code') == 'IN':
            return {
                'name':      r.get('name'),
                'latitude':  r.get('latitude'),
                'longitude': r.get('longitude'),
                'elevation': r.get('elevation', 0),
                'state':     r.get('admin1', ''),
            }

    return None