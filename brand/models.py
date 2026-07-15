from django.db import models
from core.models import BaseModel
from django.utils.text import slugify
from django.conf import settings


class Brand(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="brand_profile",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brand/", null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=150)
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

    def __str__(self):
        return self.name
