from django.contrib import admin
from rating.models import Rating
# Register your models here.

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "order"
    )
    readonly_fields = ('created_at', 'updated_at') 
    list_filter = ("rating",)
    search_fields = ("order__order_number", "user__username", "product__title")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
