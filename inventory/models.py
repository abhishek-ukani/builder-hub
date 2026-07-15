from django.db import models
from core.models import BaseModel
from product.models import ProductVariant
from django.core.exceptions import ValidationError


class Warehouse(BaseModel):
    name = models.CharField(max_length=225)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.code}"


class Inventory(BaseModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="inventories"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="inventories"
    )
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)
    incoming_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "warehouse"], name="unique_variant_warehouse"
            ),
        ]
        indexes = [models.Index(fields=["variant", "warehouse"])]

    def clean(self):
        quantities = [
            self.available_quantity,
            self.reserved_quantity,
            self.damaged_quantity,
            self.incoming_quantity,
        ]

        if any(q < 0 for q in quantities):
            raise ValidationError("Quantities cannot be negative.")

    def __str__(self):
        return f"{self.variant.sku} = {self.warehouse.code}"


class InventoryTransaction(BaseModel):
    class TransactionType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sale"
        RETURN = "RETURN", "Return"
        CANCEL = "CANCEL", "Cancel"
        DAMAGE = "DAMAGE", "Damage"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        TRANSFER_IN = "TRANSFER_IN", "Transfer In"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer Out"

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="inventoy_transactions"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="invenroty_transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.PositiveIntegerField()
    refernce_id = models.UUIDField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["variant"]),
            models.Index(fields=["warehouse"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.variant.sku} - {self.transaction_type}"


class StockTransfer(BaseModel):
    class TransferStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SHIPPED = "SHIPPED", "Shipped"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    from_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="outgoing_transfers"
    )
    to_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="incoming_transfers"
    )
    status = models.CharField(max_length=20, choices=TransferStatus.choices)
    shipped_at = models.DateTimeField(null=True, blank=True)
    receiced_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):

        if self.from_warehouse == self.to_warehouse:
            raise ValidationError("Source and destination warehouse cannot be same.")

    def __str__(self):
        return f"{self.from_warehouse.name} - {self.to_warehouse}"


class StockTransferItems(BaseModel):
    transfer = models.ForeignKey(
        StockTransfer, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="transfer_items"
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["transfer", "variant"],
                name="unique_transfer_variant",
            )
        ]

    def __str__(self):
        return f"{self.variant.sku} - {self.quantity}"
