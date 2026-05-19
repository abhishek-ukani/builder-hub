from django.contrib import admin
from brand.models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "is_active",
        "slug",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description", "user__username")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("user",)
    ordering = ("name",)
    list_editable = ("is_active",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "name",
                    "description",
                    "logo",
                    "slug",
                    "is_active",
                    "latitude",
                    "longitude",
                )
            },
        ),
    )
