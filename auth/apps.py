from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth'          # The actual folder name
    label = 'authentication'  # This makes it unique to Django
