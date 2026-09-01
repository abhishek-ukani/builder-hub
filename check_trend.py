import os
import sys
import django

sys.path.append('/home/logicrays/abhishek_workspace/python/demo/builder_hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT DATE_TRUNC('month', order_created_at) AS month, SUM(quantity)
        FROM ml.analytics_view
        WHERE item_label = 'Kathiyavadi Thali'
        GROUP BY month
        ORDER BY month;
    """)
    rows = cursor.fetchall()
    print("Monthly sums for Kathiyavadi Thali:")
    for r in rows[-24:]:
        print(f"Month: {r[0].strftime('%Y-%m')}, Qty: {r[1]}")
