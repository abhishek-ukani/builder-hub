from django.contrib import admin
from supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    raw_id_fields = ("variant",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "email", "phone", "gst_number")
    ordering = ("name",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_number",
        "supplier",
        "warehouse",
        "status",
        "ordered_at",
        "expected_delivery_date",
        "received_at",
    )
    list_filter = ("status", "supplier", "warehouse", "ordered_at")
    search_fields = ("po_number", "supplier__name", "warehouse__name")
    ordering = ("-created_at",)
    date_hierarchy = "ordered_at"
    raw_id_fields = ("supplier", "warehouse")
    inlines = (PurchaseOrderItemInline,)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_order",
        "variant",
        "ordered_quantity",
        "received_quantity",
        "unit_cost",
    )
    list_filter = ("purchase_order", "variant")
    search_fields = ("purchase_order__po_number", "variant__sku")
    raw_id_fields = ("purchase_order", "variant")
