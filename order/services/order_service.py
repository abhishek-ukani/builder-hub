from order.models import Order
from faker import Faker

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
        print(f"Generated order number: {order_number}")  # Debug statement
        if not Order.objects.filter(order_number=order_number).exists():
            return order_number

    raise ValueError(
        "Unable to generate unique order number "
        f"after {max_attempts} attempts."
    )