from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserType(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        FARMER = "FARMER", "Farmer"
        STAFF = "STAFF", "Staff"

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    user_type = models.CharField(
        max_length=20, choices=UserType.choices, default=UserType.CUSTOMER
    )
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
