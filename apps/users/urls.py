from django.urls import path
from .views import (
    RegistrationView,
    AdminRegistrationView,
    LoginView,
    CustomTokenRefreshView,
    UserProfileView,
    VerifyEmailView,
    ResendActivationEmailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Auth & Registration
    path('register/', RegistrationView.as_view(), name='register'),
    path('register/admin/', AdminRegistrationView.as_view(), name='register-admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Email Verification
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-activation-code/', ResendActivationEmailView.as_view(), name='resend-activation-code'),
    
    # Password Reset
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]