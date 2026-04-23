import sqlite3
import pandas as pd

def create_database():

    # connect to database file
    conn = sqlite3.connect('data/weather.db')

    # SQL is a STRING in Python

    conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_daily(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 city TEXT,
                 date TEXT,
                 temperature REAL,
                 precipitation REAL,
                 windspeed REAL,
                 humidity REAL,
                 UNIQUE(city,date)
                 )
                 """)
    conn.commit()   # saving changes to dist
    conn.close()
    print('Database ready')


def save_to_db(df, city_name):
    conn = sqlite3.connect('data/weather.db')

    for index , row in df.iterrows():
        conn.execute("""
                INSERT or IGNORE INTO weather_daily
                     (city, date, temperature, precipitation, windspeed, humidity)
                     VALUES(?, ?, ?, ?, ?, ?)
                     """,(
                         city_name,
                         row['time'],
                         row['temperature_2m_mean'],
                         row['precipitation_sum'],
                         row['windspeed_10m_max'],
                         row['relative_humidity_2m_max']
                     ))
    conn.commit()
    conn.close()
    print('Data Saved Successfully')
        
def df_summary():
    conn = sqlite3.connect('data/weather.db')

    df = pd.read_sql("""
        SELECT city,
                COUNT(*) as total_days,
                MIN(date) as from_date,
                MAX(date) as to_date
        FROM weather_daily
        GROUP BY city
         """,conn)
    conn.close()
    print(df)

def location_exists(city_name):
    """
    Checking if we already have data for this city.
    Returns True if city is in database, False if not.
    """

    with sqlite3.connect('data/weather.db') as conn :
        cnt = conn.execute("""SELECT COUNT(*) FROM weather_daily WHERE city = ?""",(city_name,)).fetchone()[0]

        if cnt > 0 :
            return True
        else:
            return False


def load_from_db(city_name):
    with sqlite3.connect('data/weather.db') as conn :
        df = pd.read_sql("""SELECT date, temperature, precipitation, windspeed, humidity FROM weather_daily WHERE city = ?
            """,conn, params=(city_name,))
        df['date'] = pd.to_datetime(df['date'])
        return df


if __name__ == '__main__':
    
    # from fetch_data import get_coordinates, fetch_weather

    # # create database
    # create_database()

    # # get coordinates
    # location = get_coordinates('Mumbai')
    # print(location['name'], location['latitude'], location['longitude'])

    # # fetch weather
    # df = fetch_weather(location['latitude'], location['longitude'])
    # print(df.shape)

    # # save to database
    # save_to_db(df, location['name'])

    df_summary()
    # print(location_exists('Mumbai'))
    # print(location_exists('Leh'))

    # df = load_from_db('Mumbai')
    # print(df.shape)
    # print(df.head())
    # print(df.dtypes)
    
    
