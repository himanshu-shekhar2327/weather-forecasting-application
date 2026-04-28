import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))

import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
from sklearn.preprocessing import MinMaxScaler

from database import load_from_db ,get_zone_models
from fetch_data import fetch_recent_weather, get_coordinates
from features import create_features, create_sequences
from zones import get_zone_from_coordinates, get_city_info, CITY_DATA

VARIABLES = ['temperature', 'precipitation', 
             'windspeed', 'humidity']


def load_zone_models(zone):
    df = get_zone_models(zone)

    models = {}
    for _, row in df.iterrows():
        variable   = row['variable']
        model_type = row['model_type']
        model_path = row['model_path']
        
        if model_type == 'LSTM':
            model = tf.keras.models.load_model(model_path)
        else:
            model = joblib.load(model_path)
        
        models[variable] = (model, model_type)

    # load scalers only if LSTM exists in this zone
    scaler_path = f'saved_models/{zone}/scalers.pkl'
    
    if os.path.exists(scaler_path):
        scalers = joblib.load(scaler_path)
    else:
        scalers = None

    return models, scalers

def forecast_city(city_name, days=8, lat=None, lon=None, alt=None):


    """
    Main Function - takes city name, return 7 day forecast DataFrame
    """
    # if coordinates provided directly — use them
    if lat and lon:
        zone = get_zone_from_coordinates(lat, lon)
        if zone is None:
            zone = "india"
    else:
        # fall back to existing logic
        city_info = get_city_info(city_name)
        if city_info:
            zone = city_info['zone']
            lat  = city_info['lat']
            lon  = city_info['lon']
            alt  = city_info['alt']
        else:
            data = get_coordinates(city_name)
            lat  = data['latitude']
            lon  = data['longitude']
            alt  = data['elevation']
            zone = get_zone_from_coordinates(lat, lon)
            if zone is None:
                zone = "india"

    
    recent_weather = fetch_recent_weather(lat,lon)
    models, scalers = load_zone_models(zone)

    recent_df = recent_weather.copy()
    recent_df['latitude']  = lat
    recent_df['longitude'] = lon
    recent_df['altitude']  = alt

    forecast_rows = []

    for day in range(days):
        
        predictions = {}
        
        for variable in VARIABLES:
            model, model_type = models[variable]
            
            if model_type == 'LSTM':
                # get last 14 days of 4 variables as numpy array
                last14 = recent_df[VARIABLES].values[-14:]
                
                # scale — use saved scaler or fit on recent data
                if scalers is not None:
                    first_city = list(scalers.keys())[0]
                    scaler = scalers[first_city]
                else:
                    scaler = MinMaxScaler()
                    scaler.fit(recent_df[VARIABLES].values)
                    
                last14_scaled = scaler.transform(last14)
                
                # reshape to (1, 14, 4) for LSTM
                X = last14_scaled.reshape(1, 14, 4)
                
                # predict and inverse transform
                pred_scaled = model.predict(X, verbose=0)
                pred_real   = scaler.inverse_transform(pred_scaled)
                
                # get this variable's value
                var_index = VARIABLES.index(variable)
                value = pred_real[0][var_index]
                
            else:
                if model_type == 'VAR':
                    # VAR needs last 5 days as input
                    last5 = recent_df[VARIABLES].values[-5:]
                    forecast = model.forecast(last5, steps=1)
                    var_index = VARIABLES.index(variable)
                    value = forecast[0][var_index]
                else:
                    # RF, XGBoost, LightGBM
                    feat = create_features(recent_df)
                    feat = feat.dropna()
                    last_row = feat.iloc[[-1]]
                    value = model.predict(last_row)[0]
                
            
            predictions[variable] = value
        # build new row with predictions + location
        new_row = pd.DataFrame([{
            'temperature':   predictions['temperature'],
            'precipitation': predictions['precipitation'],
            'windspeed':     predictions['windspeed'],
            'humidity':      predictions['humidity'],
            'latitude':      lat,
            'longitude':     lon,
            'altitude':      alt
        }], index=[recent_df.index[-1] + pd.Timedelta(days=1)])

        recent_df = pd.concat([recent_df, new_row])
        
        
        forecast_rows.append(predictions)

    forecast_df = pd.DataFrame(forecast_rows)
    return forecast_df