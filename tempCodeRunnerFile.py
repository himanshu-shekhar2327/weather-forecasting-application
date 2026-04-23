import requests
import pandas as pd

# One city first — we'll add more once this works
city = "Mumbai"
lat  = 19.08
lon  = 72.88

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude":   lat,
    "longitude":  lon,
    "start_date": "2020-01-01",
    "end_date":   "2024-12-31",
    "daily": "temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max",
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data["daily"])
df.rename(columns={"time": "date"}, inplace=True)
df["date"] = pd.to_datetime(df["date"])

print(df.head(10))
print("\nShape:", df.shape)
print("\nMissing values:\n", df.isnull().sum())