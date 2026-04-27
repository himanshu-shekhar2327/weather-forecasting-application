import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor


def train_rf(X_train , X_test , y_train ,y_test, variable):
    
    # training rf
    rf = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train[variable])

    # predict on X_Test
    y_pred = rf.predict(X_test)

    # calculating rmse
    rmse = np.sqrt(mean_squared_error(y_test[variable], y_pred))


    return rf , rmse


def train_xgb(X_train, X_test, y_train, y_test, variable):
    
    xgb = XGBRegressor(n_estimators = 100 , random_state = 42 , verbosity=0) 

    xgb.fit(X_train, y_train[variable])

    y_pred = xgb.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test[variable], y_pred))

    return xgb , rmse 

def train_lgbm(X_train, X_test, y_train, y_test, variable):

    lgb = LGBMRegressor(n_estimators = 100 , random_state = 42 , verbosity=-1) 

    lgb.fit(X_train, y_train[variable])

    y_pred = lgb.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test[variable], y_pred))

    return lgb , rmse