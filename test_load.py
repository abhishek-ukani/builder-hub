import os
import sys
sys.path.append('/home/logicrays/abhishek_workspace/python/demo/foodIQ/scripts')

from forecasting import load_daily_demand

df = load_daily_demand("c8125591-b02c-4fe5-a511-c27f1b471e5f")
print("DataFrame shape:", df.shape)
print("Describe:\n", df.describe())
print("Non-zero rows:", (df['y'] > 0).sum())
print("Head:\n", df.head())
print("Tail:\n", df.tail(15))
