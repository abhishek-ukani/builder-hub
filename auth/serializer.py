from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from auth.models import User
from auth.services.auth_service import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from utils.jwt_manager import JWTManager
from typing import Dict


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that username already exists.",
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="This email is already registered"
            )
        ],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=True
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, trim_whitespace=True)

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not (username or email):
            raise serializers.ValidationError(
                "Either username or email must be provided."
            )
        if not password:
            raise serializers.ValidationError("Password is required.")

        user = None
        # Determine login field
        lookup = {}
        if username:
            lookup["username"] = username
        elif email:
            lookup["email"] = email

        try:
            user = User.objects.get(**lookup)

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")

            attrs["user"] = user
            attrs["is_email_verified"] = user.is_email_verified

            return attrs

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")


class LoginResponseSerializer(serializers.Serializer):
    user = UserResponseSerializer()
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj) -> Dict[str, str]:
        """
        obj should be a User instance
        """
        user = obj["user"]

        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.strip()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    def validate(self, attrs):
        token = attrs.get("token")
        if not token:
            raise serializers.ValidationError({"token": ["Token is required"]})

        try:
            # Decode token
            payload = JWTManager.decode_token(token)

            # Ensure token is for password reset
            if payload.get("type") != "password_reset":
                raise serializers.ValidationError({"token": ["Invalid token type"]})

            # Get user
            user = User.objects.get(id=payload["user_id"])
            attrs["user"] = user  # Attach user for use in save()

        except User.DoesNotExist:
            raise serializers.ValidationError({"user": ["User not found"]})
        except Exception:
            raise serializers.ValidationError({"token": ["Invalid or expired token"]})

        return attrs

    def save(self):
        """
        Set the new password for the user.
        """
        user = self.validated_data["user"]
        new_password = self.validated_data["password"]
        user.set_password(new_password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is invalid.")
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from old password."}
            )

        return attrs

    def save(self):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return user
