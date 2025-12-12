import random
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.request import Request
from .models import OneTimePassword

User = get_user_model()

def send_verification_email(user):
    otp_code = str(random.randint(10000, 99999)) # generates 5 digits

    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'otp': otp_code}
    )

    # prepare email
    subject = "Verify your email address"
    email_body = f"Hi {user.first_name},\n\nYour verification code is: {otp_code}\n\nPlease enter this code to activate your account."
    from_email = settings.EMAIL_HOST_USER

    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
    d_email.send(fail_silently=True)


def send_otp_via_email(email):
    subject = "Your Account Verification Code"
    otp_code = str(random.randint(10000, 99999))  # generated 5 digits
    
    user = User.objects.get(email=email)
    
    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'otp': otp_code}
    )
    
    email_body = f"Hi {user.first_name},\n\nYour One Time Password (OTP) for password reset is: {otp_code}\n\nThis code is valid for 5 minutes."
    
    from_email = settings.EMAIL_HOST_USER
    
    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    d_email.send(fail_silently=True)