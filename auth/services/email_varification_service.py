from utils.jwt_manager import JWTManager
from django.conf import settings


def generate_verification_url(user):
    token = JWTManager.generate_email_verification_token(user)

    return f"{settings.FRONTEND_URL}/auth/verify-email/?token={token}"


