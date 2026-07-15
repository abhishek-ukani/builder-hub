from decimal import Decimal
import os
import random

from faker import Faker
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "builder_hub.settings")
django.setup()

from django.utils import timezone

fake = Faker()
from order.models import Order
from rating.models import Rating

orders = list(
    Order.objects.prefetch_related("items__variant__product").only("id", "customer")
)

order_with_ratings = random.sample(orders, 75000)
order_with_full_review = random.sample(order_with_ratings, 30000)

full_review_set = set(order.id for order in order_with_full_review)
naive_datetime = fake.date_time_this_decade()
rating_value = [1, 2, 3, 4, 5]
rating_probabilities = [0.010, 0.015, 0.020, 0.025, 0.030]
review = [
    "Incredible food! Every single dish was packed with flavor, beautifully presented, and arrived piping hot. The service was fantastic too. This has officially become my new favorite spot!",
    "Really tasty food and great portion sizes. The flavors were spot on. The only minor downside was that the service was a bit slow since they were busy, but the meal itself was well worth the wait.",
    "It was just okay. The appetizer was good, but the main entree was pretty bland and underseasoned. It’s fine if you need a quick bite, but nothing I’d go out of my way to order again.",
    "Sadly, this missed the mark. The food arrived lukewarm, the meat was incredibly dry, and it felt way overpriced for the quality we received. Won't be ordering from here again.",
    "Terrible experience. The order was completely wrong, the food tasted old and greasy, and it was practically cold when it arrived. Save your money and eat somewhere else.",
]

ratings_to_create = []

for order in order_with_ratings:
    aware_datetime = timezone.make_aware(naive_datetime)
    user = order.customer
    processed_products = set()
    for item in order.items.all():
        product = item.variant.product
        if product.id in processed_products:
            continue
            
        processed_products.add(product.id)
        rating = Rating(
            product=product,
            user=user,
            rating=random.choices(rating_value, weights=rating_probabilities, k=1)[0],
            order=order,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        if order.id in full_review_set:
            rating.review = review[rating.rating - 1]
        ratings_to_create.append(rating)


create_ratings = Rating.objects.bulk_create(ratings_to_create, batch_size=5000)
