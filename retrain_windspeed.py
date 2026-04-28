import sys
sys.path.append('src')

import joblib
from database import load_zone_data, save_zone_model
from features import create_zone_features
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import os

zone     = 'zone6_highland'
variable = 'windspeed'

print(f"Retraining {variable} for {zone} with LightGBM...")

# load data
zone_df = load_zone_data(zone)

# build features
X, y = create_zone_features(zone_df)

# split
train_size = int(len(X) * 0.80)
X_train = X.iloc[:train_size]
X_test  = X.iloc[train_size:]
y_train = y.iloc[:train_size]
y_test  = y.iloc[train_size:]

# train LightGBM
model = LGBMRegressor(
    n_estimators = 100,
    random_state = 42,
    verbose      = -1
)
model.fit(X_train, y_train[variable])

# evaluate
y_pred = model.predict(X_test)
rmse   = np.sqrt(mean_squared_error(y_test[variable], y_pred))
print(f"LightGBM RMSE: {rmse:.3f}")

# save — overwrites the large RF file
path = f'saved_models/{zone}/{variable}.pkl'
joblib.dump(model, path)
print(f"Saved to {path}")

# update database
save_zone_model(zone, variable, 'LightGBM', rmse, path)
print(f"Database updated")

# verify size
size = os.path.getsize(path) / (1024*1024)
print(f"New file size: {size:.2f} MB")