from django.db import models
from core.models import BaseModel
from category.models import Category
from brand.models import Brand
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Product(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=225)
    sort_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["category"]),
            models.Index(fields=["brand"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(max_length=225, unique=True)
    barcode = models.CharField(max_length=225, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    compare_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField()

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self):

        if self.compare_price is not None and self.compare_price < self.price:
            raise ValidationError(
                {
                    "compare_price": (
                        "Compare price must be greater than or equal to price."
                    )
                }
            )

    def __str__(self):
        return self.sku


class Attribute(BaseModel):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name


class AttributeValue(BaseModel):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="values"
    )
    value = models.CharField()

    class Meta:
        unique_together = ("attribute", "value")

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"


class VariantAttributeValue(BaseModel):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="attribut_values"
    )
    attribute_value = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE, related_name="variant_values"
    )

    class Meta:
        unique_together = ("variant", "attribute_value")
