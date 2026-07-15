from django.db import models
from core.models import BaseModel
from auth.models import User
from product.models import ProductVariant, MealSlot, Thali, ThaliComponentOption
from user.models import UserAddress

# Create your models here.
class Order(BaseModel):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    shipping_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    meal_slot = models.ForeignKey(
        MealSlot, on_delete=models.PROTECT, null=True, blank=True, related_name="orders"
    )
    scheduled_delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_address = models.ForeignKey(
        UserAddress, on_delete=models.PROTECT,   # or inline fields
        null=True, blank=True
    )
    special_instructions = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        return self.order_number


class OrderItems(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="order_items", null=True, blank=True
    )
    thali = models.ForeignKey(
        Thali, on_delete=models.PROTECT, related_name="order_items", null=True, blank=True
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "variant"],
                condition=models.Q(variant__isnull=False),
                name="unique_order_variant",
            ),
        ]

    def __str__(self):
        item_name = self.variant.sku if self.variant else f"Thali-{self.thali.name}"
        return f"{self.order.order_number}-{item_name}"


class OrderItemThaliOption(BaseModel):
    order_item = models.ForeignKey(
        OrderItems, on_delete=models.CASCADE, related_name="thali_options"
    )
    option = models.ForeignKey(
        ThaliComponentOption, on_delete=models.PROTECT, related_name="order_thali_options"
    )

    class Meta:
        verbose_name = "Order Item Thali Option"
        verbose_name_plural = "Order Item Thali Options"
        unique_together = ("order_item", "option")

    def __str__(self):
        component_group = self.option.group.name
        product_name = self.option.product_variant.product.title
        return f"{self.order_item.order.order_number} - {component_group}: {product_name}"



class Return(BaseModel):
    class ReturnStatus(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        PICKED_UP = "PICKED_UP", "Picked Up"
        RECEIVED = "RECEIVED", "Received"
        COMPLETED = "COMPLETED", "Completed"
        REJECTED = "REJECTED", "Rejected"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="returns")
    status = models.CharField(
        max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.REQUESTED
    )
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Return {self.order.order_number}"


class ReturnItem(BaseModel):
    class ConditionType(models.TextChoices):
        GOOD = "GOOD", "Good"
        DAMAGED = "DAMAGED", "Damaged"
        MISSING = "MISSING", "Missing"

    order_return = models.ForeignKey(
        Return, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="return_items"
    )
    quantity = models.PositiveSmallIntegerField()
    condition_type = models.CharField(max_length=20, choices=ConditionType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order_return", "variant"],
                name="unique_return_variant",
            ),
        ]

    def __str__(self):
        return f"{self.variant.sku} ({self.quantity})"


class Delivery(BaseModel):
    class DeliveryStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PICKED_UP = "PICKED_UP", "Picked Up"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class DeliveryType(models.TextChoices):
        DIRECT_FROM_FARMER = "DIRECT", "Direct from Farmer"
        FROM_WAREHOUSE = "WAREHOUSE", "From Warehouse"

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="deliveries"
    )
    status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING
    )
    delivery_type = models.CharField(max_length=20, choices=DeliveryType.choices)
    tracking_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance in km",
    )
    estimated_delivery_at = models.DateTimeField(null=True, blank=True)
    actual_delivery_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for {self.order.order_number} - {self.get_status_display()}"
