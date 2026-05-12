from utils.jwt_manager import JWTManager
from django.conf import settings

def generate_reset_password_url(user):
    token = JWTManager.generate_password_reset_token(user)
    return f"{settings.FRONTEND_URL}/auth/reset-password/?token={token}"
