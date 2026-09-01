import os
import sys
import django

sys.path.append('/home/logicrays/abhishek_workspace/python/demo/builder_hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT EXTRACT(year FROM order_created_at) AS year, COUNT(*), SUM(quantity)
        FROM ml.analytics_view
        WHERE item_label = 'Kathiyavadi Thali'
        GROUP BY year
        ORDER BY year;
    """)
    rows = cursor.fetchall()
    print("Kathiyavadi Thali orders per year:")
    for r in rows:
        print(f"Year: {r[0]}, Count: {r[1]}, Qty: {r[2]}")
