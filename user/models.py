from django.db import models
from django.conf import settings
from core.models import BaseModel, phone_validation, pincode_validation
from product.models import ProductVariant



# Create your models here.
class UserAddress(BaseModel):
    ADDRESS_TYPE = (("home", "Home"), ("work", "Work"), ("other", "Other"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE, default="home")
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, validators=[phone_validation])
    address_line_1 = models.CharField(blank=True, max_length=255)
    address_line_2 = models.CharField(blank=True, max_length=255)
    landmark = models.CharField(blank=True, max_length=255)
    pincode = models.CharField(max_length=6, validators=[pincode_validation])
    area = models.CharField(blank=True, max_length=100)
    city = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(
                id=self.id
            ).update(is_default=False)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class WishlistItem(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='wishlist_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="wishlisted_by")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "variant"],
                name="unique_user_variant_wishlist"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["variant"]),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f'{self.user} - {self.variant.sku}'
