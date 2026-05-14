from django.db import models
from core.models import BaseModel, phone_validation
from inventory.models import Warehouse
from product.models import ProductVariant
from django.core.exceptions import ValidationError


class Suppliers(BaseModel):
    class SupplierStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        BLOCKED = "BLOCKED", "Blocked"

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[phone_validation])
    address = models.TextField()
    gst_number = models.CharField(max_length=15, unique=True)
    status = models.CharField(
        max_length=20, choices=SupplierStatus.choices, default=SupplierStatus.ACTIVE
    )

    class Meta:
        ordering = ["name"]

        indexes = [models.Index(fields=["name"]), models.Index(fields=["email"])]

    def __str__(self):
        return self.name


class PurchaseOrder(BaseModel):
    class OrderStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ORDERED = "ORDERED", "Ordered"
        PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED", "Partially Received"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    supplier = models.ForeignKey(
        Suppliers, on_delete=models.PROTECT, related_name="purchase_orders"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="purchase_orders"
    )
    po_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT
    )
    ordered_at = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["po_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.po_number


class PurchaseOrderItem(BaseModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="purchase_order_items"
    )
    ordered_quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["purchase_order", "variant"],
                name="unique_purchase_variant",
            )
        ]

    def clean(self):
        if self.received_quantity != self.ordered_quantity:
            raise ValidationError("Received quantity and ordered quantity is not same.")

    def __str__(self):
        return
