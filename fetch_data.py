import requests
import pandas as pd

def get_coordinates(place_name):
    search_query = f"{place_name}, India"
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name":     search_query,
        "count":    10,
        "language": "en",
        "format":   "json"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return None

    india_results = [
        r for r in data["results"]
        if r.get("country_code") == "IN"
    ]

    if not india_results:
        return None

    return india_results[0]  # best match


def fetch_weather(lat, lon, start_year=1990):
    """Fetch all historical data year by year."""
    import time
    all_data = []

    for year in range(start_year, 2025):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude":   lat,
            "longitude":  lon,
            "start_date": f"{year}-01-01",
            "end_date":   f"{year}-12-31",
            "daily": "temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max",
            "timezone": "Asia/Kolkata"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "daily" in data:
            df = pd.DataFrame(data["daily"])
            all_data.append(df)

        time.sleep(0.3)

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.rename(columns={"time": "date"}, inplace=True)
    return final_df


# ── TEST THE FULL FLOW ──────────────────────────

place = "Majuli"   # try any Indian location!

print(f"🔍 Searching for '{place}'...")
location = get_coordinates(place)

if location:
    print(f"📍 Found: {location['name']}, {location.get('admin1','')}, India")
    print(f"   Coordinates: lat={location['latitude']}, lon={location['longitude']}")
    print(f"\n📡 Fetching weather data from 1990...")

    df = fetch_weather(location["latitude"], location["longitude"])

    print(f"\n✅ Done!")
    print(f"   Total rows : {len(df)}")
    print(f"   Date range : {df['date'].min()} → {df['date'].max()}")
    print(f"\nSample data:")
    print(df.tail(5).to_string(index=False))