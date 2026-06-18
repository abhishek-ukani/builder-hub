from django.db import models
from core.models import BaseModel
from product.models import Product
from auth.models import User
from order.models import Order

class Rating(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(default=0)
    review = models.TextField(blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="ratings")

    class Meta:
        unique_together = ("product", "user", "order")
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["user"]),
            models.Index(fields=["rating"]),
        ]
    def __str__(self):
        return f"Rating {self.rating} for {self.product.title} by {self.user.username}"