# test_predictor.py
import sys
sys.path.append('src')

from predictor import forecast_city

print("Testing forecast for Aurangabad...")
forecast = forecast_city('Aurangabad')
print(forecast)