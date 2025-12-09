import random
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.request import Request
from .models import OneTimePassword

User = get_user_model()

def send_verification_email(user, request: Request):
    token = RefreshToken.for_user(user=user).access_token

    # CHANGED: Just get the base path '/auth/verify-email/'
    relative_link = reverse('verify-email')

    current_site = request.get_host()
    
    # CHANGED: Manually construct URL with Query Param
    abs_url = f"http://{current_site}{relative_link}?token={str(token)}"

    # Keep this print for safety!
    print(f"\nClick this link to verify: {abs_url}\n") 

    email_body = f"Hi {user.email}, \n\n Please use this link below to verify your email:\n{abs_url}"

    send_mail(
        subject="Verify your email",
        message=email_body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_otp_via_email(email):
    # Kept your OTP logic
    subject = "Your Account Verification Code"
    otp_code = str(random.randint(100000, 999999)) 
    
    user = User.objects.get(email=email)
    
    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'otp': otp_code}
    )
    
    email_body = f"Hi {user.full_name},\n\nYour One Time Password (OTP) for password reset is: {otp_code}\n\nThis code is valid for 5 minutes."
    
    from_email = settings.EMAIL_HOST_USER
    
    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    d_email.send(fail_silently=True)