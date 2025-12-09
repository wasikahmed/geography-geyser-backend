import jwt
from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .utils import send_otp_via_email, send_verification_email
from .serializers import (
    SetNewPasswordSerializer, 
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer, 
    UserProfileSerializer, 
    PasswordResetRequestSerializer
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
            send_verification_email(user, request)
            return Response({
                'message': "User registered successfully. Please check your email to verify your account.",
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    pass 

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request):
        token = request.GET.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Cleanup token from potential terminal copy-paste issues
        if '3D' in token or '\n' in token:
             token = token.replace('=3D', '').replace('=', '').replace('\n', '')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)

            if not user.is_active:
                user.is_active = True
                user.save()
                return Response({'message': 'Email successfully verified! You can now log in.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email already verified.'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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