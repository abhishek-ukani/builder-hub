import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


phone_validation = RegexValidator(
    regex=r"^[6-9]\d{9}$", message="Enter a valid 10-digit number."
)

pincode_validation = RegexValidator(
    regex=r"^\d{6}$", message="Enter a valid 6-digit pincode."
)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
