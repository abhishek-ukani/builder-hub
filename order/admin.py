from django.contrib import admin
from order.models import (
    Order,
    OrderItems,
    Return,
    ReturnItem,
    Delivery,
)


class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0
    readonly_fields = ("total_price",)
    raw_id_fields = ("variant",)


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0
    raw_id_fields = ("variant",)


class DeliveryInline(admin.TabularInline):
    model = Delivery
    extra = 0
    raw_id_fields = ("order",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "status",
        "payment_status",
        "grand_total",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "customer__username", "customer__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("customer",)
    inlines = (OrderItemsInline, DeliveryInline)


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "variant",
        "qunatity",
        "unit_price",
        "total_price",
    )
    list_filter = ("order", "variant")
    search_fields = ("order__order_number", "variant__sku")
    raw_id_fields = ("order", "variant")


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "refund_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order__order_number", "order__customer__username")
    raw_id_fields = ("order",)
    inlines = (ReturnItemInline,)


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ("order_return", "variant", "quantity", "condition_type")
    list_filter = ("condition_type",)
    search_fields = ("order_return__order__order_number", "variant__sku")
    raw_id_fields = ("order_return", "variant")


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "status",
        "delivery_type",
        "tracking_number",
        "estimated_delivery_at",
        "actual_delivery_at",
    )
    list_filter = ("status", "delivery_type")
    search_fields = ("order__order_number", "tracking_number")
    raw_id_fields = ("order",)
    date_hierarchy = "estimated_delivery_at"
