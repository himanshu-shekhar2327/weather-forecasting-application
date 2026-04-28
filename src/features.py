import pandas as pd
import numpy as np


# creating features

def create_features(df, lag_days = 14) :

    features =  pd.DataFrame(index = df.index)

    for key in ['temperature','precipitation','windspeed','humidity']:
        for j in range(1,15):
            features[f'{key}_lag{j}'] = df[key].shift(j)
        
        features[f'{key}_rolling7_mean'] = df[key].shift(1).rolling(7).mean()
        features[f'{key}_rolling14_mean'] = df[key].shift(1).rolling(14).mean()
        features[f'{key}_rolling7_std'] = df[key].shift(1).rolling(7).std()

    features['month']  = df.index.month
    features['dayofyear']  = df.index.dayofyear
    features['dayofweek']   = df.index.dayofweek


    features['latitude'] = df['latitude']
    features['longitude'] = df['longitude']
    features['altitude'] = df['altitude'] 

    return features


# creating zone features

def create_zone_features(zone_df, lag_days = 14):

    all_features = []
    all_targets  = []

    for city in zone_df['city'].unique():

        city_df = zone_df[zone_df['city']  ==  city].copy()
        city_df = city_df.set_index('date')
        city_df = city_df.asfreq('D')
        city_df = city_df.ffill()
        
        feat = create_features(city_df)

        feat  = feat.dropna()
        targ = city_df.loc[feat.index][['temperature',
                                 'precipitation',
                                 'windspeed',
                                 'humidity']]

        all_features.append(feat)
        all_targets.append(targ)
    
    X = pd.concat(all_features)
    y = pd.concat(all_targets)
    return X , y


# creating sequences for LSTM
def create_sequences(data, window_size = 14):
    X , y = [] , []
    for i in range(window_size , len(data)):
        X.append(data[i-window_size:i])
        y.append(data[i])
    
    return np.array(X), np.array(y)
