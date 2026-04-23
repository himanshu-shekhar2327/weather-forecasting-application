import time

from database import location_exists ,save_to_db
from fetch_data import get_coordinates , fetch_weather

INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Surat"]


for city in INDIAN_CITIES:
     
    try:
        location = get_coordinates(city)

        if location is None:
            print(f'{city} not found, skipping...')
            continue
    
        official_name = location['name']

        if location_exists(official_name) :
            print(f'{official_name} already exists, skipping...')
            continue

        df = fetch_weather(location['latitude'],location['longitude'])
        if df is None:
            print(f'Could Not fetch data for {official_name}, skipping ....')
            continue

        save_to_db(df,location['name'])

        print(f'{official_name} saved successfully')
    
    except Exception as e :
        print(f'Error for {city}: {e}')
        print(f'Waiting 60 seconds...')
        continue

    time.sleep(2)  # wait 2 second between cities