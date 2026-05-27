from faker import Faker
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'builder_hub.settings')
django.setup()
from auth.models import User
from django.utils import timezone


fake = Faker()

    
    # 2. Make it timezone-aware

for _ in range(1000):
    naive_datetime = fake.date_time_this_decade()
    aware_datetime = timezone.make_aware(naive_datetime)
    User.objects.create_user(
        username=fake.user_name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        password="test123",
        user_type=User.UserType.CUSTOMER,
        is_email_verified=True,
        date_joined=aware_datetime,
    )