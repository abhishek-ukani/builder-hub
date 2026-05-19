from django.contrib import admin
from product.models import (
    Product,
    Thali,
    ProductVariant,
    ProductMedia,
    Attribute,
    AttributeValue,
    VariantAttributeValue,
)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = (
        "sku",
        "weight",
        "price",
        "compare_price",
        "stock_status",
        "is_active",
    )
    extra = 1
    raw_id_fields = ("product",)


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    fields = ("variant", "image", "alt_text", "is_primary", "sort_order")
    extra = 1
    raw_id_fields = ("variant",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "category")
    search_fields = ("title", "slug", "description", "sort_description")
    ordering = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("category",)
    inlines = (ProductVariantInline, ProductMediaInline)
    date_hierarchy = "created_at"


@admin.register(Thali)
class ThaliAdmin(admin.ModelAdmin):
    list_display = ("name", "item", "price", "compare_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "item__title")
    raw_id_fields = ("item",)
    ordering = ("name",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product",
        "stock_status",
        "price",
        "compare_price",
        "is_active",
        "created_at",
        "quantity",
    )
    list_filter = ("stock_status", "is_active", "product")
    search_fields = ("sku", "barcode", "product__title")
    ordering = ("-created_at",)
    raw_id_fields = ("product",)
    readonly_fields = ("discount_percentage",)


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "variant",
        "alt_text",
        "is_primary",
        "sort_order",
        "created_at",
    )
    list_filter = ("is_primary", "product", "variant")
    search_fields = ("product__title", "variant__sku", "alt_text")
    ordering = ("product", "sort_order")
    raw_id_fields = ("product", "variant")


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value")
    search_fields = ("attribute__name", "value")
    raw_id_fields = ("attribute",)
    ordering = ("attribute", "value")


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("variant", "attribute_value")
    search_fields = ("variant__sku", "attribute_value__value")
    raw_id_fields = ("variant", "attribute_value")
    ordering = ("variant",)
