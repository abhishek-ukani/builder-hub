import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class JWTManager:
    ALGORITHM = "HS256"

    TOKEN_TYPES = {
        "ACCESS": "access",
        "REFRESH": "refresh",
        "EMAIL_VERIFICATION": "email_verification",
        "PASSWORD_RESET": "password_reset",
    }

    EXPIRATION = {
        "access": timedelta(minutes=30),
        "refresh": timedelta(days=7),
        "email_verification": timedelta(minutes=15),
        "password_reset": timedelta(minutes=10),
    }

    @classmethod
    def generate_token(cls, user, token_type, extra_payload=None):
        """
        Generate JWT token
        """

        if token_type not in cls.EXPIRATION:
            raise ValueError("Invalid token type")

        payload = {
            "user_id": user.id,
            "type": token_type,
            "exp": (datetime.now(timezone.utc) + cls.EXPIRATION[token_type]),
        }

        # Add extra payload if provided
        if extra_payload:
            payload.update(extra_payload)

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=cls.ALGORITHM)

        return token

    @classmethod
    def decode_token(cls, token, expected_type=None):
        """
        Decode and validate JWT token
        """

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[cls.ALGORITHM])

            # Validate token type
            if expected_type and payload.get("type") != expected_type:
                raise AuthenticationFailed("Invalid token type")

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")

        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

    @classmethod
    def generate_access_token(cls, user):
        return cls.generate_token(user=user, token_type=cls.TOKEN_TYPES["ACCESS"])

    @classmethod
    def generate_refresh_token(cls, user):
        return cls.generate_token(user=user, token_type=cls.TOKEN_TYPES["REFRESH"])

    @classmethod
    def generate_email_verification_token(cls, user):
        return cls.generate_token(
            user=user, token_type=cls.TOKEN_TYPES["EMAIL_VERIFICATION"]
        )

    @classmethod
    def generate_password_reset_token(cls, user):
        return cls.generate_token(
            user=user, token_type=cls.TOKEN_TYPES["PASSWORD_RESET"]
        )
