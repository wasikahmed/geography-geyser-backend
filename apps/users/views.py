import jwt
from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .utils import send_otp_via_email, send_verification_email
from .serializers import (
    SetNewPasswordSerializer, 
    UserRegistrationSerializer,
    AdminRegistrationSerializer, 
    CustomTokenObtainPairSerializer, 
    UserProfileSerializer, 
    PasswordResetRequestSerializer,
    VerifyEmailSerializer,
    ResendActivationEmailSerializer,
)
from .models import OneTimePassword

User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # send the OTP email instead of the link
            send_verification_email(user)

            return Response({
                'message': "User registered successfully. Please check your email to verify your account.",
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Admin user created successfully.',
                'user': serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Email verified successfully. You can now log in.'},
            status=status.HTTP_200_OK
        )

class ResendActivationEmailView(generics.GenericAPIView):
    serializer_class = ResendActivationEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        send_verification_email(user)

        return Response(
            {'message': 'A new verification code has been sent to your email.'},
            status=status.HTTP_200_OK
        )

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    pass

class GoogleAuthClient(OAuth2Client):
    def __init__(self, request, consumer_key, consumer_secret, access_token_method, access_token_url, callback_url, scope, scope_delimiter, headers, basic_auth):
        # django-allauth (new version) removed 'scope' and 'scope_delimiter' from __init__
        # but dj-rest-auth (older wrapper) still sends them.
        # We accept them in args to prevent a crash, but we DO NOT pass them to super().
        super().__init__(
            request=request,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_method=access_token_method,
            access_token_url=access_token_url,
            callback_url=callback_url,
            headers=headers,
            basic_auth=basic_auth
        )

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = GoogleAuthClient
    callback_url = "http://localhost:3000"

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # CRITICAL FIX: We must call save() to trigger the email sending logic
        serializer.save()
        
        return Response(
            {'message': "We have sent an OTP to your email address."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Password reset successful.'},
            status=status.HTTP_200_OK
        )