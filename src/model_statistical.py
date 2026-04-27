import sys
import os 
sys.path.append(os.path.join(os.getcwd(), '..', 'src'))

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from statsmodels.tsa.vector_ar.var_model import VAR
from sklearn.metrics import mean_squared_error


def train_var(train_df, test_df , variable):

    var_model = VAR(train_df)
    var_result = var_model.fit(5)
    forecast_input = train_df.values[-5:]  # Last 5 days (= lag order p)

    forecast  = var_result.forecast(forecast_input, steps = len(test_df))
    forecast_df = pd.DataFrame(forecast , index = test_df.index, columns=test_df.columns)


    rmse = np.sqrt(mean_squared_error(test_df[variable], forecast_df[variable]))

    return var_result , rmse