import time
from database import create_database, location_exists, save_to_db
from fetch_data import fetch_weather
from zones import CITY_DATA


import sys
sys.path.append('src')

create_database()

for city, info in CITY_DATA.items():
    try:
        if location_exists(city):
            print(f"{city} already exists, skipping...")
            continue

        print(f"Fetching {city} ({info['zone']})...")

        # retry up to 3 times if API fails
        df = None
        for attempt in range(3):
            df = fetch_weather(info['lat'], info['lon'])
            if df is not None:
                break
            print(f"  Attempt {attempt + 1} failed. Waiting 60 seconds...")
            time.sleep(60)

        if df is None:
            print(f"Could not fetch {city} after 3 attempts, skipping...")
            continue

        save_to_db(
            df, city,
            zone     = info['zone'],
            lat      = info['lat'],
            lon      = info['lon'],
            altitude = info['alt']
        )
        print(f"{city} saved — zone: {info['zone']}")

    except Exception as e:
        print(f"Error for {city}: {e}")
        print("Waiting 60 seconds before next city...")
        time.sleep(60)
        continue

    time.sleep(5)  # 5 seconds between successful requests