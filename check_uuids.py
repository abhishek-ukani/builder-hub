import os
import sys
import django

sys.path.append('/home/logicrays/abhishek_workspace/python/demo/builder_hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT DISTINCT item_id::text, item_label
        FROM ml.analytics_view
        WHERE item_label = 'Kathiyavadi Thali';
    """)
    rows = cursor.fetchall()
    print("Kathiyavadi Thali item_id in analytics_view:")
    for r in rows:
        print(r)
