import random
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from django.contrib.auth import get_user_model

from .models import EmailOTP, PasswordResetToken


User = get_user_model()


# For Verify-OTP
def generate_otp():
    return f"{random.randint(100000, 999999)}"

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_otp_via_email(self, user_id):
    user = User.objects.get(id=user_id)

    # Remove old Unused OTPs
    EmailOTP.objects.filter(user=user, used=False).delete()

    code = generate_otp()
    EmailOTP.objects.create(user=user, code=code)

    subject = "Your Email Verification OTP"
    message = f"Your OTP for email verification is: {code}\n\nit will expire in 10 minutes."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


# For Forgot Password Link
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_password_reset_email(self, user_id):
    user = User.objects.get(id=user_id)
    
    raw_token, token_obj = PasswordResetToken.generate(user) 

    reset_url = f"{settings.FRONTEND_URL}/reset-password/{raw_token}"

    subject = "Reset Your Password"
    message = f"Click The link below to rest password:\n\n{reset_url}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

    return raw_token 
