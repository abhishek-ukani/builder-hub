from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    UserResponseSerializer,
    LoginResponseSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from auth.models import User
from utils.jwt_manager import JWTManager
from auth.tasks import send_reset_password_email, send_verification_email
from auth.throttles import LoginFailRateThrottle


class RegisterView(APIView):
    @extend_schema(
        request=RegisterSerializer,
        responses=UserResponseSerializer,
        description="Register a new user",
        examples=[
            OpenApiExample(
                "User Example",
                value={
                    "username": "john_doe",
                    "email": "john@yopmail.com",
                    "password": "Strongpassword@123",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
        ],
    )
    def post(self, request):
        self.permission_classes = [AllowAny]
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Trigger email after user is created
        send_verification_email.delay(
            user_id=user.id,
            recipient_list=[user.email],
        )

        response_data = UserResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: {
                "description": "Email verified successfully.",
                "content": {
                    "application/json": {
                        "example": {"message": "Email verified successfully."}
                    }
                },
            },
            400: {
                "description": "Something went wrong",
                "content": {
                    "application/json": {
                        "example": {"message": ["Something went wrong"]}
                    }
                },
            },
        },
    )
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response(
                {"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = JWTManager.decode_token(
                expected_type=JWTManager.TOKEN_TYPES["EMAIL_VERIFICATION"],
                token=token,
            )
            # Validate token type
            if payload.get("type") != "email_verification":
                return Response(
                    {"error": "Invalid token type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = User.objects.get(id=payload["user_id"])
            user.is_email_verified = True
            user.save()
            return Response({"message": "Email verified successfully"})
        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": e},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        summary="User login",
        description="Authenticate a user and return user info with token",
        request=LoginSerializer,
        responses=LoginResponseSerializer,
    )
    def post(self, request):
        throttle = LoginFailRateThrottle()
        if not throttle.allow_request(request, self):
            return Response({"message": "Too many failed attempts."}, status=429)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if not serializer.validated_data.get("is_email_verified", ""):
            send_verification_email.delay(
                user_id=user.id,
                recipient_list=[user.email],
            )
            return Response(
                {
                    "message": "Your Email is not verified yet. Sent verification link to your email, go and verify it first."
                }
            )

        if user:
            response_data = LoginResponseSerializer({"user": user}).data
            return Response(response_data, status=status.HTTP_200_OK)

        throttle.throttled(request, wait=throttle.wait())
        return Response({"message": "Invalid credentials"}, status=400)


class ForgotPassword(APIView):
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: {
                "description": "Password reset email sent successfully.",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Reset password mail is sent to your email."
                        }
                    }
                },
            },
            400: {
                "description": "Invalid input.",
                "content": {
                    "application/json": {
                        "example": {"email": ["This field is required."]}
                    }
                },
            },
        },
        description="Send a password reset email to the user.",
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # Attempt to fetch user, trigger email if exists
        try:
            user = User.objects.get(email=email)
            send_reset_password_email.delay(recipient_list=[email], user_id=user.id)
        except User.DoesNotExist:
            # Do nothing — avoid revealing whether email exists
            pass
        return Response(
            {"message": "Reset password mail is sent to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPassword(APIView):
    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: {"description": "Password reset successfully."}},
    )
    def post(self, request):
        data = request.data.copy()
        data["token"] = request.query_params.get("token", "")
        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: {"description": "Password reset successfully."}},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password has been change successfully."},
            status=status.HTTP_200_OK,
        )
