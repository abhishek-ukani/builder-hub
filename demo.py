from decimal import Decimal
import os
import random

from faker import Faker
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "builder_hub.settings")
django.setup()

from django.utils import timezone

from auth.models import User
from order.models import Order, OrderItems, OrderItemThaliOption
from product.models import Thali, ThaliComponentGroup, ThaliComponentOption
from rating.models import Rating
from user.models import UserAddress

fake = Faker()

# -------------------------------------------------------------------
# PRELOAD DATA (avoid querying inside loops)
# -------------------------------------------------------------------

users = list(User.objects.only("id", "date_joined"))

thali = Thali.objects.get(name="Kathiyavadi Thali")

# Preload component groups and their options
component_groups = list(thali.component_groups.all())
group_options_map = {}
for opt in ThaliComponentOption.objects.filter(group__in=component_groups).select_related("group", "product_variant__product"):
    group_options_map.setdefault(opt.group_id, []).append(opt)

addresses = list(
    UserAddress.objects.select_related("user").only("id", "user_id", "city")
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

ORDER_COUNT = 3000

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
        f"Unable to generate unique order number after {max_attempts} attempts."
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

    status_ = random.choices(statuses, weights=status_probabilities, k=1)[0]

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

    item_payloads = []
    quantity = random.randint(1, 3)

    # Select thali options
    selected_options = []
    options_charge = Decimal("0.00")
    for group in component_groups:
        opts = group_options_map.get(group.id, [])
        if opts:
            min_sel = group.min_selections if group.is_required else 0
            max_sel = max(min_sel, group.max_selections)
            num_sel = random.randint(min_sel, max_sel)
            if num_sel > 0:
                selected = random.sample(opts, k=min(num_sel, len(opts)))
                selected_options.extend(selected)
                options_charge += sum(opt.extra_charge for opt in selected)

    compare_price = (thali.compare_price or thali.price) + options_charge
    actual_price = thali.price + options_charge

    unit_discount = compare_price - actual_price

    subtotal += quantity * compare_price
    discount_amount += quantity * unit_discount

    item_payloads.append(
        {
            "variant": thali,
            "quantity": quantity,
            "unit_price": actual_price,
            "total_price": quantity * actual_price,
            "thali_options": selected_options,
        }
    )

    # ---------------------------------------------------------------
    # Charges
    # ---------------------------------------------------------------

    shipping_charge = Decimal(str(round(random.uniform(10, 30), 2)))

    tax_amount = round((subtotal - discount_amount) * Decimal("0.05"), 2)

    if (subtotal - discount_amount) > 499:
        shipping_charge = Decimal("0")

    grand_total = round(subtotal + tax_amount + shipping_charge - discount_amount, 2)

    # ---------------------------------------------------------------
    # Order number
    # ---------------------------------------------------------------

    city_prefix = (delivery_address.city or "XX")[:2].upper()

    # ---------------------------------------------------------------
    # Create Order instance (not saved yet)
    # ---------------------------------------------------------------

    order = Order(
        customer=user,
        order_number=generate_order_number(city_prefix, aware_datetime),
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
            fake.sentence(nb_words=10) if random.random() < 0.3 else ""
        ),
    )

    orders_to_create.append((order, item_payloads))

# -------------------------------------------------------------------
# BULK CREATE ORDERS
# -------------------------------------------------------------------

created_orders = Order.objects.bulk_create(
    [o[0] for o in orders_to_create], batch_size=1000
)

# -------------------------------------------------------------------
# PREPARE ORDER ITEMS
# -------------------------------------------------------------------

order_item_options_data = []
order_options_map = {}

for order, (_, item_payloads) in zip(created_orders, orders_to_create):
    item = item_payloads[0]
    order_items_to_create.append(
        OrderItems(
            order=order,
            thali=item["variant"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            total_price=item["total_price"],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    )
    order_item_options_data.append(item["thali_options"])
    order_options_map[order.id] = item["thali_options"]

# -------------------------------------------------------------------
# BULK CREATE ORDER ITEMS
# -------------------------------------------------------------------

created_items = OrderItems.objects.bulk_create(order_items_to_create, batch_size=5000)

# -------------------------------------------------------------------
# PREPARE & BULK CREATE THALI OPTIONS
# -------------------------------------------------------------------

thali_options_to_create = []
for order_item, options in zip(created_items, order_item_options_data):
    for opt in options:
        thali_options_to_create.append(
            OrderItemThaliOption(
                order_item=order_item,
                option=opt,
                created_at=order_item.created_at,
                updated_at=order_item.updated_at,
            )
        )

OrderItemThaliOption.objects.bulk_create(thali_options_to_create, batch_size=5000)

# -------------------------------------------------------------------
# GENERATE RATINGS / REVIEWS FOR THALI
# -------------------------------------------------------------------

num_rated_orders = int(len(created_orders) * 0.8)
if num_rated_orders == 0 and len(created_orders) > 0:
    num_rated_orders = 1

rated_orders = random.sample(created_orders, num_rated_orders)

num_reviewed_orders = int(len(rated_orders) * 0.4)
if num_reviewed_orders == 0 and len(rated_orders) > 0:
    num_reviewed_orders = 1

reviewed_orders_set = set(o.id for o in random.sample(rated_orders, num_reviewed_orders))

rating_value = [1, 2, 3, 4, 5]
rating_probabilities = [0.010, 0.015, 0.020, 0.025, 0.030]

ratings_to_create = []

for order in rated_orders:
    user = order.customer
    rating_val = random.choices(rating_value, weights=rating_probabilities, k=1)[0]
    rating_obj = Rating(
        thali=thali,
        user=user,
        rating=rating_val,
        order=order,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
    if order.id in reviewed_orders_set:
        options = order_options_map.get(order.id, [])
        sabjis = []
        breads = []
        farshans = []
        sweets = []
        for opt in options:
            group_name = opt.group.name.lower()
            title = opt.product_variant.product.title
            if "shabji" in group_name or "sabji" in group_name:
                sabjis.append(title)
            elif "bread" in group_name:
                breads.append(title)
            elif "farshan" in group_name:
                farshans.append(title)
            elif "sweet" in group_name:
                sweets.append(title)
                
        components_desc = []
        if sabjis:
            components_desc.append(f"the {', '.join(sabjis)}")
        if breads:
            components_desc.append(f"the {', '.join(breads)}")
        if sweets:
            components_desc.append(f"the {', '.join(sweets)}")
        
        items_str = ", ".join(components_desc[:-1]) + f", and {components_desc[-1]}" if len(components_desc) > 1 else components_desc[0] if components_desc else ""
        
        if rating_val == 5:
            review_text = f"Incredible Thali! Every component was packed with flavor, especially {items_str}. Highly recommended!"
        elif rating_val == 4:
            review_text = f"Really tasty food and great portion sizes. The {items_str} were excellent, though the service was a bit slow."
        elif rating_val == 3:
            review_text = f"It was an okay meal. The {items_str} were fine, but the overall flavor was a bit bland."
        elif rating_val == 2:
            review_text = f"Sadly, this missed the mark. The {items_str} arrived lukewarm and underseasoned."
        else:
            review_text = f"Terrible experience. The {items_str} tasted greasy and old. Won't order again."
            
        rating_obj.review = review_text
    ratings_to_create.append(rating_obj)

Rating.objects.bulk_create(ratings_to_create, batch_size=5000)

print(f"Created {len(created_orders)} orders")
print(f"Created {len(order_items_to_create)} order items")
print(f"Created {len(ratings_to_create)} ratings")
