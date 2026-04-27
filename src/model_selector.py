import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..', 'src'))

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from database import load_zone_data, save_zone_model
from features import (create_zone_features, create_sequences)

from model_ml import train_rf, train_xgb, train_lgbm
from model_statistical import train_var
from model_dl import train_lstm


ZONES = ['zone1_arid', 'zone2_coastal_west',
         'zone3_coastal_east', 'zone4_deccan',
         'zone5_north',        'zone6_highland']

VARIABLES = ['temperature', 'precipitation',
             'windspeed',   'humidity']
WINDOW = 14


def prepare_var_data(zone_df):
    all_train = []
    all_test  = []

    for city in zone_df['city'].unique():
        city_df = zone_df[zone_df['city'] == city].copy()
        city_df = city_df.set_index('date')
        city_df = city_df.asfreq('D')
        city_df = city_df.fillna(method='ffill')
        city_df = city_df[VARIABLES]

        train_size = int(len(city_df) * 0.80)
        all_train.append(city_df.iloc[:train_size])
        all_test.append(city_df.iloc[train_size:])

    train_df = pd.concat(all_train)
    test_df  = pd.concat(all_test)
    return train_df, test_df



def prepare_ml_data(zone_df):

    X, y = create_zone_features(zone_df)

    train_size = int(len(X) * 0.80)

    X_train = X.iloc[:train_size]
    X_test  = X.iloc[train_size:]
    y_train = y.iloc[:train_size]
    y_test  = y.iloc[train_size:]

    return X_train, X_test, y_train, y_test

def prepare_lstm_data(zone_df):

    all_X = []
    all_y = []

    scalers = {}  # one scaler per city — remember to inverse transform later

    for city in zone_df['city'].unique():
        
        # get city data
        city_df = zone_df[zone_df['city'] == city].copy()
        city_df = city_df.set_index('date')
        city_df = city_df.asfreq('D')
        city_df = city_df.fillna(method='ffill')
        
        # keep only 4 weather variables
        data = city_df[VARIABLES].values
        
        # scale to 0-1
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        scalers[city] = scaler
        
        # create sequences
        X, y = create_sequences(data_scaled, WINDOW)
        
        all_X.append(X)
        all_y.append(y)
    
    X_all = np.concatenate(all_X, axis=0)
    y_all = np.concatenate(all_y, axis=0)

    train_size  = int(len(X_all) * 0.80)

    X_train = X_all[:train_size]
    X_test  = X_all[train_size:]
    y_train = y_all[:train_size]
    y_test  = y_all[train_size:]

    return X_train, X_test, y_train, y_test, scalers



def run_selector():

    for zone in ZONES:

        print(f'\n Processing {zone}...')

        # loading zone data
        zone_df = load_zone_data(zone)

        # prepare data 3 ways
        train_df , test_df = prepare_var_data(zone_df)
        X_train, X_test, y_train , y_test = prepare_ml_data(zone_df)
        X_tr_l, X_te_l, y_tr_l, y_te_l, scalers = prepare_lstm_data(zone_df)

        # create save directory
        save_dir = f'saved_models/{zone}'
        os.makedirs(save_dir, exist_ok=True)

        # for each variable , trrain all models and pick winner
        for variable in VARIABLES:
            print(f'  {variable}...')

            var_index  = VARIABLES.index(variable)
            first_city = list(scalers.keys())[0]
            scaler     = scalers[first_city]

            results = {}

            results['VAR']      = train_var(train_df, test_df, variable)
            results['RF']       = train_rf(X_train, X_test, y_train, y_test, variable)
            results['XGBoost']  = train_xgb(X_train, X_test, y_train, y_test, variable)
            results['LightGBM'] = train_lgbm(X_train, X_test, y_train, y_test, variable)
            results['LSTM']     = train_lstm(X_tr_l, X_te_l, y_tr_l, y_te_l,
                                             variable, scaler, var_index)

            
            winner_name  = min(results, key=lambda x: results[x][1])
            winner_model = results[winner_name][0]
            winner_rmse  = results[winner_name][1]

            if winner_name == 'LSTM':
                path = f'{save_dir}/{variable}.keras'
                winner_model.save(path)
            else:
                path = f'{save_dir}/{variable}.pkl'
                joblib.dump(winner_model, path)

            save_zone_model(zone, variable, winner_name, winner_rmse, path)
            print(f"    → {winner_name} wins (RMSE: {winner_rmse:.3f})")


if __name__ == '__main__':
    run_selector()


