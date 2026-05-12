from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
