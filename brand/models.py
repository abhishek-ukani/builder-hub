from django.db import models
from core.models import BaseModel
from django.utils.text import slugify


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brand/", null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

    def __str__(self):
        return self.name
