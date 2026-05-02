import sys
sys.path.append('src')

from zones import CITY_DATA
from database import save_to_db
from fetch_data import fetch_recent_weather
from datetime import datetime

print(f"Update started: {datetime.now()}")

for city, info in CITY_DATA.items():
    try:
        weather = fetch_recent_weather(
            info['lat'], info['lon'], days=5
        )
        if weather is not None:
            weather = weather.reset_index()
            weather['time'] = weather['time'].astype(str)
            weather = weather.rename(columns={
                'temperature':   'temperature_2m_mean',
                'precipitation': 'precipitation_sum',
                'windspeed':     'windspeed_10m_max',
                'humidity':      'relative_humidity_2m_max'
            })
            save_to_db(weather, city, info['zone'],
                      info['lat'], info['lon'], info['alt'])
        else:
            print(f"{city} — fetch failed")

    except Exception as e:
        print(f"{city} error: {e}")
        continue

print(f"Update complete: {datetime.now()}")