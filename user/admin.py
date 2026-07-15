from django.contrib import admin
from user.models import UserAddress, WishlistItem


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "phone_number",
        "city",
        "pincode",
        "address_type",
        "is_default",
        "created_at",
    )
    list_filter = ("address_type", "city", "is_default")
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone_number",
        "city",
        "pincode",
    )
    raw_id_fields = ("user",)
    ordering = ("-is_default", "-created_at")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "variant", "created_at")
    list_filter = ("user", "variant")
    search_fields = ("user__username", "variant__sku")
    raw_id_fields = ("user", "variant")
    ordering = ("-created_at",)
