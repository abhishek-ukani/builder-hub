from django.contrib import admin
from category.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "level",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "level", "parent")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    list_editable = ("is_active",)
    raw_id_fields = ("parent",)
    date_hierarchy = "created_at"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "parent",
                    "slug",
                    "description",
                    "image",
                    "is_active",
                )
            },
        ),
    )
