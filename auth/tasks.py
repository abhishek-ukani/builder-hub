from auth.services.email_service import send_mail_django
from auth.services.email_context import EmailContextBuilder
from celery import shared_task
from auth.models import User


@shared_task
def send_verification_email(recipient_list, user_id):
    user = User.objects.get(id=user_id)

    send_mail_django(
        recipient_list=recipient_list,
        subject="Verify your email",
        template_name="emails/email_verification.html",
        context=EmailContextBuilder.email_varification(user),
    )


@shared_task
def send_reset_password_email(recipient_list, user_id):
    user = User.objects.get(id=user_id)

    send_mail_django(
        recipient_list=recipient_list,
        subject="Reset your account password",
        template_name="emails/reset_password.html",
        context=EmailContextBuilder.reset_password(user),
    )
