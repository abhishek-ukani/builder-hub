from django.db import models
from core.models import BaseModel
from django.utils.text import slugify


class Category(BaseModel):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
