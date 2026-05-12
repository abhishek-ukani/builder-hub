from auth.services.email_varification_service import generate_verification_url
from auth.services.reset_password_service import generate_reset_password_url

class EmailContextBuilder:

    @staticmethod
    def email_varification(user):
        verification_url = generate_verification_url(user)
        return {
            "name": user.first_name,
            "verification_url": verification_url,
        }
    

    @staticmethod
    def reset_password(user):
        reset_url = generate_reset_password_url(user)
        return {
            'name': user.username,
            'reset_url' : reset_url
        }