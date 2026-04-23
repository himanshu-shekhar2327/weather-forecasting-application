import requests
import pandas as pd
from datetime import datetime
def fetch_weather(lat, lon):
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude':lat,
        'longitude':lon,
        'start_date':'1990-01-01',
        'end_date':   datetime.today().strftime('%Y-%m-%d'),
        'daily':'temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max',
        'timezone':'Asia/Kolkata'
        
    }
    response = requests.get(url , params=params, timeout=10)

    data = response.json()

    if 'daily' not in data:
        print(f"⚠️  API error: {data.get('reason', 'unknown error')}")
        return None

    df = pd.DataFrame(data['daily'])



    return df


def get_coordinates(place_name):
    search_query = f'{place_name}, india'
    url = 'https://geocoding-api.open-meteo.com/v1/search'


    params = {
        'name' : search_query,
        'count':10,
        'language': 'en',
        'format': 'json',

    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'results' not in data:
        return None
    for r in data['results']:
        if r.get('country_code') == 'IN':
            return r
    
