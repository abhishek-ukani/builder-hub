from django.db import models
from core.models import BaseModel
from product.models import Product, Thali
from auth.models import User
from order.models import Order

class Rating(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    thali = models.ForeignKey(Thali, on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(default=0)
    review = models.TextField(blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="ratings")

    class Meta:
        unique_together = (("product", "user", "order"), ("thali", "user", "order"))
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["thali"]),
            models.Index(fields=["user"]),
            models.Index(fields=["rating"]),
        ]
    def __str__(self):
        target = self.thali.name if self.thali else (self.product.title if self.product else "N/A")
        return f"Rating {self.rating} for {target} by {self.user.username}"