from decimal import Decimal
import os
import random

from faker import Faker
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "builder_hub.settings")
django.setup()

from django.utils import timezone

from auth.models import User
from order.models import Order, OrderItems
from product.models import ProductVariant
from user.models import UserAddress

fake = Faker()

# -------------------------------------------------------------------
# PRELOAD DATA (avoid querying inside loops)
# -------------------------------------------------------------------

users = list(
    User.objects.only("id", "date_joined")
)

variants = list(
    ProductVariant.objects.only("id", "price", "compare_price")
)

addresses = list(
    UserAddress.objects.select_related("user").only(
        "id",
        "user_id",
        "city"
    )
)

# Group addresses by user_id for fast lookup
user_addresses_map = {}

for address in addresses:
    user_addresses_map.setdefault(address.user_id, []).append(address)

# Filter users who actually have addresses
valid_users = [user for user in users if user.id in user_addresses_map]

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

ORDER_COUNT = 9000

statuses = [
    Order.OrderStatus.DELIVERED,
    Order.OrderStatus.FAILED,
    Order.OrderStatus.CANCELLED,
]

status_probabilities = [0.994, 0.001, 0.005]

orders_to_create = []
order_items_to_create = []

fake = Faker()


def generate_order_number(city_prefix, aware_datetime, max_attempts=10):
    """
    Generate a unique order number.

    Format:
    SU2605271234

    Structure:
    [CITY][YY][MM][DD][4_RANDOM_DIGITS]
    """

    for _ in range(max_attempts):

        order_number = (
            f"{city_prefix}"
            f"{aware_datetime.year % 100:02d}"
            f"{aware_datetime.month:02d}"
            f"{aware_datetime.day:02d}"
            f"{fake.random_number(digits=4, fix_len=True)}"
        )

        if not Order.objects.filter(order_number=order_number).exists():
            return order_number

    raise ValueError(
        "Unable to generate unique order number "
        f"after {max_attempts} attempts."
    )
# -------------------------------------------------------------------
# GENERATE ORDERS
# -------------------------------------------------------------------

for _ in range(ORDER_COUNT):

    # ---------------------------------------------------------------
    # Random user + address
    # ---------------------------------------------------------------

    user = random.choice(valid_users)
    user_addresses = user_addresses_map[user.id]
    delivery_address = random.choice(user_addresses)

    # ---------------------------------------------------------------
    # Generate order datetime
    # ---------------------------------------------------------------

    naive_datetime = fake.date_time_this_decade()
    aware_datetime = timezone.make_aware(naive_datetime)

    if aware_datetime < user.date_joined:
        aware_datetime = user.date_joined + timezone.timedelta(
            days=random.randint(1, 365)
        )

    # ---------------------------------------------------------------
    # Order status
    # ---------------------------------------------------------------

    status_ = random.choices(
        statuses,
        weights=status_probabilities,
        k=1
    )[0]

    payment_status_map = {
        Order.OrderStatus.DELIVERED: Order.PaymentStatus.SUCCESS,
        Order.OrderStatus.CANCELLED: Order.PaymentStatus.REFUNDED,
        Order.OrderStatus.FAILED: Order.PaymentStatus.FAILED,
    }

    payment_status = payment_status_map[status_]

    # ---------------------------------------------------------------
    # Order items
    # ---------------------------------------------------------------

    order_items_count = random.randint(1, 5)

    subtotal = Decimal("0")
    discount_amount = Decimal("0")

    selected_variants = random.sample(
    variants,
    k=min(order_items_count, len(variants))
)

    item_payloads = []

    for variant in selected_variants:

        quantity = random.randint(1, 3)

        compare_price = variant.compare_price or variant.price
        actual_price = variant.price

        unit_discount = compare_price - actual_price

        subtotal += quantity * compare_price
        discount_amount += quantity * unit_discount

        item_payloads.append({
            "variant": variant,
            "quantity": quantity,
            "unit_price": actual_price,
            "total_price": quantity * actual_price,
        })

    # ---------------------------------------------------------------
    # Charges
    # ---------------------------------------------------------------

    shipping_charge = Decimal(
        str(round(random.uniform(10, 30), 2))
    )

    tax_amount = round((subtotal - discount_amount) * Decimal("0.05"), 2)

    if (subtotal - discount_amount) > 499:
        shipping_charge = Decimal("0")

    grand_total = round(
        subtotal +
        tax_amount +
        shipping_charge -
        discount_amount,
        2
    )

    # ---------------------------------------------------------------
    # Order number
    # ---------------------------------------------------------------

    city_prefix = (delivery_address.city or "XX")[:2].upper()

  

    # ---------------------------------------------------------------
    # Create Order instance (not saved yet)
    # ---------------------------------------------------------------

    order = Order(
        customer=user,
        order_number=generate_order_number(city_prefix,aware_datetime),
        status=status_,
        payment_status=payment_status,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_charge=shipping_charge,
        discount_amount=discount_amount,
        grand_total=grand_total,
        created_at=aware_datetime,
        updated_at=aware_datetime,
        delivery_address=delivery_address,
        special_instructions=(
            fake.sentence(nb_words=10)
            if random.random() < 0.3
            else ""
        ),
    )

    orders_to_create.append((order, item_payloads))

# -------------------------------------------------------------------
# BULK CREATE ORDERS
# -------------------------------------------------------------------

created_orders = Order.objects.bulk_create(
    [o[0] for o in orders_to_create],
    batch_size=1000
)

# -------------------------------------------------------------------
# PREPARE ORDER ITEMS
# -------------------------------------------------------------------

for order, (_, item_payloads) in zip(created_orders, orders_to_create):

    for item in item_payloads:

        order_items_to_create.append(
            OrderItems(
                order=order,
                variant=item["variant"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
        )

# -------------------------------------------------------------------
# BULK CREATE ORDER ITEMS
# -------------------------------------------------------------------

OrderItems.objects.bulk_create(
    order_items_to_create,
    batch_size=5000
)

print(f"Created {len(created_orders)} orders")
print(f"Created {len(order_items_to_create)} order items")