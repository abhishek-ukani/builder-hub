from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.html import strip_tags

def send_mail_django(
    recipient_list:list,
    subject:str,
    template_name,
    context=None,
    from_email=None,
):
    """
    Send dynamic HTML email using Django template
    """

    context = context or {}

    # Required field validation
    if not recipient_list:
        raise ValueError("recipient_list is required")

    if not subject:
        raise ValueError("subject is required")

    if not template_name:
        raise ValueError("template_name is required")

    # Default sender email
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    print("recipient_list", recipient_list)

    # Validate emails
    for email in recipient_list:
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(f"Invalid email address: {email}")

    try:
        # Render HTML template
        html_content = render_to_string(
            template_name,
            context
        )

        # Plain text fallback
        text_content = strip_tags(html_content)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send()

        return {
            "success": True,
            "message": "Email sent successfully"
        }

    except Exception as e:
        print("EMAIL ERROR:", str(e))
        raise e
    

