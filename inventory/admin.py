from django.contrib import admin
from inventory.models import (
    Warehouse,
    Inventory,
    InventoryTransaction,
    StockTransfer,
    StockTransferItems,
)


class StockTransferItemsInline(admin.TabularInline):
    model = StockTransferItems
    extra = 1
    raw_id_fields = ("variant",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "state", "is_active", "created_at")
    list_filter = ("is_active", "city", "state")
    search_fields = ("name", "code", "city", "state")
    ordering = ("name",)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "warehouse",
        "available_quantity",
        "reserved_quantity",
        "damaged_quantity",
        "incoming_quantity",
    )
    list_filter = ("warehouse",)
    search_fields = ("variant__sku", "warehouse__name")
    raw_id_fields = ("variant", "warehouse")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "warehouse",
        "transaction_type",
        "quantity",
        "created_at",
    )
    list_filter = ("transaction_type", "warehouse")
    search_fields = ("variant__sku", "warehouse__name")
    raw_id_fields = ("variant", "warehouse")
    date_hierarchy = "created_at"


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = (
        "from_warehouse",
        "to_warehouse",
        "status",
        "shipped_at",
        "receiced_at",
    )
    list_filter = ("status", "from_warehouse", "to_warehouse")
    search_fields = ("from_warehouse__name", "to_warehouse__name")
    raw_id_fields = ("from_warehouse", "to_warehouse")
    inlines = (StockTransferItemsInline,)
    date_hierarchy = "created_at"


@admin.register(StockTransferItems)
class StockTransferItemsAdmin(admin.ModelAdmin):
    list_display = ("transfer", "variant", "quantity")
    search_fields = ("transfer__id", "variant__sku")
    raw_id_fields = ("transfer", "variant")
