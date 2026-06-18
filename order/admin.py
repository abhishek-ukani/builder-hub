from django.contrib import admin
from order.models import (
    Order,
    OrderItems,
    Return,
    ReturnItem,
    Delivery,
    OrderItemThaliOption,
)
from rating.models import Rating


class OrderItemThaliOptionInline(admin.TabularInline):
    model = OrderItemThaliOption
    extra = 0
    raw_id_fields = ("option",)
    verbose_name = "Thali Component"
    verbose_name_plural = "Thali Components"
    fields = ("option", "get_component_group", "get_product_variant", "get_extra_charge")
    readonly_fields = ("get_component_group", "get_product_variant", "get_extra_charge")
    
    def get_component_group(self, obj):
        return obj.option.group.name
    get_component_group.short_description = "Component Group"
    
    def get_product_variant(self, obj):
        return f"{obj.option.product_variant.product.title} ({obj.option.product_variant.sku})"
    get_product_variant.short_description = "Product Variant"
    
    def get_extra_charge(self, obj):
        return f"₹{obj.option.extra_charge}"
    get_extra_charge.short_description = "Extra Charge"


class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0
    readonly_fields = ("total_price", "get_thali_details")
    raw_id_fields = ("variant", "thali")
    exclude = ("created_at", "updated_at")
    fields = ("variant", "thali", "quantity", "unit_price", "total_price", "get_thali_details")
    
    def get_thali_details(self, obj):
        if obj.thali:
            thali_options = OrderItemThaliOption.objects.filter(order_item=obj).select_related('option__group', 'option__product_variant')
            if thali_options.exists():
                details = []
                for thali_opt in thali_options:
                    details.append(f"• {thali_opt.option.group.name}: {thali_opt.option.product_variant.sku}")
                return "\n".join(details)
            return "(No components selected)"
        return "-"
    get_thali_details.short_description = "Thali Components"


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0
    raw_id_fields = ("variant",)


class DeliveryInline(admin.TabularInline):
    model = Delivery
    extra = 0
    raw_id_fields = ("order",)

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0  # Prevents Django from adding empty blank rows automatically
    readonly_fields = ('user', 'order', 'product') # Make fields read-only if you don't want admins changing them manually
    fields = ('user', 'rating', 'review', 'order')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "status",
        "payment_status",
        "get_items_summary",
        "grand_total",
        "created_at",
    )
    readonly_fields = ('created_at', 'updated_at', 'get_detailed_items_summary') 
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "customer__username", "customer__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("customer",)
    inlines = (OrderItemsInline, DeliveryInline, RatingInline)
    fields = ("order_number", "customer", "status", "payment_status", "subtotal", "tax_amount", 
              "shipping_charge", "discount_amount", "grand_total", "meal_slot", "scheduled_delivery_time",
              "delivery_address", "special_instructions", "get_detailed_items_summary", "created_at", "updated_at")
    
    def get_items_summary(self, obj):
        items = obj.items.all()
        thali_count = items.filter(thali__isnull=False).count()
        variant_count = items.filter(variant__isnull=False).count()
        summary_parts = []
        if thali_count > 0:
            summary_parts.append(f"{thali_count} Thali(s)")
        if variant_count > 0:
            summary_parts.append(f"{variant_count} Item(s)")
        return ", ".join(summary_parts) if summary_parts else "No items"
    get_items_summary.short_description = "Items"
    
    def get_detailed_items_summary(self, obj):
        items = obj.items.select_related('variant__product', 'thali').prefetch_related('thali_options__option__group', 'thali_options__option__product_variant')
        if not items.exists():
            return "No items in this order"
        
        details = []
        for item in items:
            if item.thali:
                details.append(f"\n<b>Thali: {item.thali.name}</b> (Qty: {item.quantity}) - ₹{item.unit_price}")
                thali_options = item.thali_options.all()
                if thali_options.exists():
                    for opt in thali_options:
                        details.append(f"  • {opt.option.group.name}: {opt.option.product_variant.product.title}")
                        if opt.option.extra_charge:
                            details.append(f"    (Extra: ₹{opt.option.extra_charge})")
                else:
                    details.append("  (No components selected)")
            else:
                product_title = item.variant.product.title if item.variant else "Unknown"
                details.append(f"<b>{product_title}</b> ({item.variant.sku if item.variant else 'N/A'}) - Qty: {item.quantity} @ ₹{item.unit_price}")
        
        return "<br>".join(details)
    get_detailed_items_summary.short_description = "Order Items Details"
    
    def get_detailed_items_summary_allow_tags(self, obj):
        return True


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "variant",
        "thali",
        "quantity",
        "unit_price",
        "total_price",
        "get_thali_options_count",
        "created_at",
    )
    readonly_fields = ('created_at', 'updated_at', 'get_thali_components') 
    list_filter = ("variant", "thali")
    search_fields = ("order__order_number", "variant__sku", "thali__name")
    raw_id_fields = ("order", "variant", "thali")
    inlines = (OrderItemThaliOptionInline,)
    fields = ("order", "variant", "thali", "quantity", "unit_price", "total_price", "get_thali_components", "created_at", "updated_at")
    
    def get_thali_options_count(self, obj):
        count = obj.thali_options.count()
        return f"{count} components" if count > 0 else "-"
    get_thali_options_count.short_description = "Thali Components"
    
    def get_thali_components(self, obj):
        if obj.thali:
            thali_options = obj.thali_options.select_related('option__group', 'option__product_variant')
            if thali_options.exists():
                details = []
                for thali_opt in thali_options:
                    details.append(f"• {thali_opt.option.group.name}: {thali_opt.option.product_variant.sku} (₹{thali_opt.option.extra_charge})")
                return "\n".join(details)
            return "(No components selected)"
        return "Not a thali item"
    get_thali_components.short_description = "Selected Thali Components"


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


@admin.register(OrderItemThaliOption)
class OrderItemThaliOptionAdmin(admin.ModelAdmin):
    list_display = ("order_item", "option", "created_at")
    raw_id_fields = ("order_item", "option")

