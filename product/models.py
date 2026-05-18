from django.db import models
from core.models import BaseModel
from category.models import Category
from brand.models import Brand
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from decimal import Decimal

class UnitTypes(models.TextChoices):
        GRAMS = 'gm', 'Grams'
        KILOGRAMS = 'kg', 'KiloGrams'
        PIECES = 'pc', 'Pieces'

class Product(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    title = models.CharField(max_length=225)
    sort_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    quantity = models.CharField(max_length=20,choices=UnitTypes.choices, default=UnitTypes.GRAMS)

    class Meta:
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["category"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)

            while Product.objects.filter(slug=slug).exists():
                slug = f"{slug}-{get_random_string(4)}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Thali(BaseModel):
    name = models.CharField(max_length=100)
    item = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="thali")
    quantity = models.CharField(max_length=20,choices=UnitTypes.choices, default=UnitTypes.GRAMS)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductVariant(BaseModel):
    class StockStatus(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In Stock"
        FEW_LEFT = "FEW_LEFT", "Few Left"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock_status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
        db_index=True,
    )
    sku = models.CharField(max_length=225, unique=True, db_index=True)
    barcode = models.CharField(max_length=225, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(("0.00")))],
    )
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "is_active"]),
            models.Index(fields=["product", "stock_status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="price_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(compare_price__gte=models.F("price")),
                name="compare_price_gte_price",
            ),
        ]

    def clean(self):
        super().clean()

        if self.compare_price is not None and self.compare_price < self.price:
            raise ValidationError(
                {
                    "compare_price": (
                        "Compare price must be greater than or equal to price."
                    )
                }
            )

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > 0:
            return round(
                ((self.compare_price - self.price) / self.compare_price) * 100,
                2,
            )
        return 0

    def __str__(self):
        return f"{self.product} - {self.sku}"


def product_image_upload_path(instance, filename):
    return f"products/{instance.product.id}/{filename}"


class ProductMedia(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to=product_image_upload_path)
    alt_text = models.CharField(blank=True, max_length=255)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["variant", "image"], name="unique_variant_image"
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_primary=True),
                name="unique_primary_product_image",
            ),
        ]

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["variant"]),
            models.Index(fields=["is_primary"]),
            models.Index(fields=["sort_order"]),
        ]

    def __str__(self):
        target = self.variant.sku if self.variant else self.product.title
        return f"{target} - {self.alt_text or 'image'}"


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
