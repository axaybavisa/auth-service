import random
from django.core.mail import send_mail
from django.conf import settings

from .models import EmailOTP

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def send_otp_via_email(user):
    EmailOTP.objects.filter(user=user, is_used=False).delete()  # Remove any existing OTPs for the user

    code = generate_otp()
    EmailOTP.objects.create(user=user, code=code)

    subject = "Your Email Verification OTP"
    message = f"Your OTP for email verification is: {code}\n\nit will expire in 10 minutes."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    send_mail(subject, message, from_email, [user.email])