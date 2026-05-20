from django.contrib import admin
from product.models import (
    Product,
    Thali,
    ProductVariant,
    ProductMedia,
    Attribute,
    AttributeValue,
    VariantAttributeValue,
    ThaliComponentGroup,
    ThaliComponentOption,
    MealSlot,
)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = (
        "sku",
        "quantity",
        "quantity_type",
        "weight",
        "price",
        "compare_price",
        "cost_price",
        "stock_status",
        "is_active",
    )
    extra = 1
    raw_id_fields = ("product",)
    readonly_fields = ("discount_percentage",)


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    fields = (
        "variant",
        "image",
        "alt_text",
        "is_primary",
        "sort_order",
    )
    extra = 1
    raw_id_fields = ("product", "variant")


class ThaliComponentOptionInline(admin.TabularInline):
    model = ThaliComponentOption
    fields = (
        "product_variant",
        "extra_charge",
        "is_default",
    )
    extra = 1
    raw_id_fields = ("product_variant",)


class ThaliComponentGroupInline(admin.StackedInline):
    model = ThaliComponentGroup
    fields = (
        "name",
        "min_selections",
        "max_selections",
        "is_required",
    )
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "product_type",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "category",
        "product_type",
    )
    search_fields = (
        "title",
        "slug",
        "description",
        "sort_description",
    )
    ordering = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("category",)
    inlines = (ProductVariantInline, ProductMediaInline)
    date_hierarchy = "created_at"


@admin.register(Thali)
class ThaliAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "compare_price",
        "cost_price",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (ThaliComponentGroupInline,)


@admin.register(ThaliComponentGroup)
class ThaliComponentGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "thali",
        "min_selections",
        "max_selections",
        "is_required",
    )
    list_filter = (
        "is_required",
        "thali",
    )
    search_fields = (
        "name",
        "thali__name",
    )
    raw_id_fields = ("thali",)
    inlines = (ThaliComponentOptionInline,)


@admin.register(ThaliComponentOption)
class ThaliComponentOptionAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "product_variant",
        "extra_charge",
        "is_default",
    )
    list_filter = (
        "is_default",
        "group",
    )
    search_fields = (
        "group__name",
        "product_variant__sku",
    )
    raw_id_fields = (
        "group",
        "product_variant",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product",
        "quantity",
        "quantity_type",
        "stock_status",
        "price",
        "compare_price",
        "discount_percentage",
        "is_active",
        "created_at",
    )
    list_filter = (
        "stock_status",
        "is_active",
        "product",
        "quantity_type",
    )
    search_fields = (
        "sku",
        "barcode",
        "product__title",
    )
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
    list_filter = (
        "is_primary",
        "product",
        "variant",
    )
    search_fields = (
        "product__title",
        "variant__sku",
        "alt_text",
    )
    ordering = ("product", "sort_order")
    raw_id_fields = (
        "product",
        "variant",
    )


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "attribute",
        "value",
    )
    search_fields = (
        "attribute__name",
        "value",
    )
    raw_id_fields = ("attribute",)
    ordering = (
        "attribute",
        "value",
    )


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "attribute_value",
    )
    search_fields = (
        "variant__sku",
        "attribute_value__value",
    )
    raw_id_fields = (
        "variant",
        "attribute_value",
    )
    ordering = ("variant",)


@admin.register(MealSlot)
class MealSlotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_time",
        "end_time",
        "cutoff_time",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("start_time",)
    