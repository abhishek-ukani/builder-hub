from django.urls import path
from auth.views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    ForgotPassword,
    ResetPassword,
    ChangePassword,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
    path("forgot-password/", ForgotPassword.as_view(), name="forgot-password"),
    path("reset-password/", ResetPassword.as_view(), name="reset-password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("change-password/", ChangePassword.as_view(), name="change-password"),
]
