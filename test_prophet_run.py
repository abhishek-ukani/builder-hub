import os
import sys
sys.path.append('/home/logicrays/abhishek_workspace/python/demo/foodIQ/scripts')

from forecasting import load_daily_demand, forecast_prophet

df = load_daily_demand("c8125591-b02c-4fe5-a511-c27f1b471e5f")
predictions = forecast_prophet(df, 14)
print("Prophet predictions for Kathiyavadi Thali:")
print(predictions)
