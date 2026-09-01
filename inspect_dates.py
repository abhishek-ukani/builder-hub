import os
import sys
import django

sys.path.append('/home/logicrays/abhishek_workspace/python/demo/builder_hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()

from django.db import connection
import pandas as pd

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT MIN(order_created_at), MAX(order_created_at), COUNT(*), SUM(quantity)
        FROM ml.analytics_view
        WHERE item_label = 'Kathiyavadi Thali';
    """)
    row = cursor.fetchone()
    print("Kathiyavadi Thali overall statistics:")
    print("Min created:", row[0])
    print("Max created:", row[1])
    print("Count:", row[2])
    print("Sum of quantity:", row[3])

    # Check daily data for the last 15 days in the database
    cursor.execute("""
        SELECT order_created_at::date, SUM(quantity)
        FROM ml.analytics_view
        WHERE item_label = 'Kathiyavadi Thali'
        GROUP BY order_created_at::date
        ORDER BY order_created_at::date DESC
        LIMIT 15;
    """)
    rows = cursor.fetchall()
    print("Last 15 days daily quantities:")
    for r in rows:
        print(f"Date: {r[0]}, Qty: {r[1]}")
