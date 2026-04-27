import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..', 'src'))

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import mean_squared_error

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL']  = '3'
def train_lstm(X_train, X_test, y_train, y_test,
               variable, scaler, var_index):

    # build model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(14, 4)),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(4)
    ])
    model.compile(optimizer='adam', loss='mse')

    # train
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )
    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=0
    )

    # predict and inverse transform
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred_real   = scaler.inverse_transform(y_pred_scaled)
    y_test_real   = scaler.inverse_transform(y_test)

    # rmse for specific variable only
    rmse = np.sqrt(mean_squared_error(
        y_test_real[:, var_index],
        y_pred_real[:, var_index]
    ))

    return model, rmse