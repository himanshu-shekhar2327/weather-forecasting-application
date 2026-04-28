import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..', 'data', 'weather.db'
)

def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_daily (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                city          TEXT,
                zone          TEXT,
                latitude      REAL,
                longitude     REAL,
                altitude      REAL,
                date          TEXT,
                temperature   REAL,
                precipitation REAL,
                windspeed     REAL,
                humidity      REAL,
                UNIQUE(city, date)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS zone_models (
                zone        TEXT,
                variable    TEXT,
                model_type  TEXT,
                rmse        REAL,
                model_path  TEXT,
                trained_on  TEXT,
                UNIQUE(zone, variable)
            )
        """)
        conn.commit()
        print("Database ready")


def save_to_db(df, city_name, zone, lat, lon, altitude):
    with sqlite3.connect(DB_PATH) as conn:
        for index, row in df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO weather_daily
                    (city, zone, latitude, longitude, altitude,
                     date, temperature, precipitation, 
                     windspeed, humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                city_name, zone, lat, lon, altitude,
                row['time'],
                row['temperature_2m_mean'],
                row['precipitation_sum'],
                row['windspeed_10m_max'],
                row['relative_humidity_2m_max']
            ))
        conn.commit()
    print(f"{city_name} saved successfully")


def load_from_db(city_name):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT date, temperature, precipitation, 
                   windspeed, humidity,
                   latitude, longitude, altitude
            FROM weather_daily 
            WHERE city = ?
            ORDER BY date
        """, conn, params=(city_name,))
        df['date'] = pd.to_datetime(df['date'])
        return df


def load_zone_data(zone_name):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT date, temperature, precipitation,
                   windspeed, humidity,
                   latitude, longitude, altitude,
                   city
            FROM weather_daily
            WHERE zone = ?
            ORDER BY city, date
        """, conn, params=(zone_name,))
        df['date'] = pd.to_datetime(df['date'])
        return df


def save_zone_model(zone, variable, model_type, 
                    rmse, model_path):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO zone_models
                (zone, variable, model_type, rmse, 
                 model_path, trained_on)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
            ON CONFLICT(zone, variable) DO UPDATE SET
                model_type = excluded.model_type,
                rmse       = excluded.rmse,
                model_path = excluded.model_path,
                trained_on = excluded.trained_on
        """, (zone, variable, model_type, rmse, model_path))
        conn.commit()

def get_zone_models(zone):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT variable, model_type, rmse, model_path
            FROM zone_models
            WHERE zone = ?
        """, conn, params=(zone,))
        return df

def location_exists(city_name):
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute("""
            SELECT COUNT(*) FROM weather_daily 
            WHERE city = ?
        """, (city_name,)).fetchone()[0]
        return count > 0


def df_summary():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT city, zone,
                   COUNT(*) as total_days,
                   MIN(date) as from_date,
                   MAX(date) as to_date
            FROM weather_daily
            GROUP BY city, zone
        """, conn)
        print(df)


if __name__ == '__main__':
    create_database()
    df_summary()



# create_database()     → creates both tables 
#                         (weather_daily, zone_models)
#                         run once at start

# save_to_db()          → saves weather rows for a city
#                         now includes zone/lat/lon/altitude

# load_from_db()        → loads one city's data for notebook

# load_zone_data()      → loads ALL cities in a zone
#                         used during model training

# save_zone_model()     → after training, records which 
#                         model won for zone+variable

# location_exists()     → checks if city already in DB
#                         used in setup.py to skip duplicates

# df_summary()          → quick check — what cities exist,
                        # how many rows, which zone