# test_predictor.py
import sys
sys.path.append('src')

from predictor import forecast_city

print("Testing forecast for 'Angul...")
forecast = forecast_city('Angul')
print(forecast)