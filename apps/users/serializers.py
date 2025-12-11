from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.contrib.auth.models import Group, update_last_login

from .utils import send_otp_via_email
from .models import OneTimePassword

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # SECURITY: Removed 'role' from fields to prevent users from registering as admins
        fields = ['id', 'email', 'password', 'confirm_password', 'full_name', 'phone_number']    
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None) 
        password = validated_data.pop('password')
        
        # Default role is set to 'student' in the model, so we don't need to pass it here.
        user = User.objects.create_user(
            password=password,
            is_active=False, 
            **validated_data
        )

        student_group, _ = Group.objects.get_or_create(name='Student')
        user.groups.add(student_group)

        return user

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirm_password', 'full_name', 'phone_number']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')

        email = validated_data.pop('email')

        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=True,
            is_staff=True,
            **validated_data
        )

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user.groups.add(admin_group)

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # trigger the update_last_login signal
        update_last_login(None, self.user)
        
        role = 'Student' # default fallback
        # get the first group name to use as the role, handles cases where a user might be in multiple groups or none
        if self.user.groups.exists():
            role = self.user.groups.first().name

        # Add extra data to the response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': role
        }
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'full_name', 'phone_number', 'date_joined', 'last_login']
        read_only_fields = ['id', 'email', 'role', 'date_joined', 'last_login']

    def get_role(self, obj):
        if obj.groups.exists():
            return obj.groups.first().name
        return 'Student'


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=5)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        
        try:
            user_otp = OneTimePassword.objects.get(user=user)
        except OneTimePassword.DoesNotExist:
            raise AuthenticationFailed('Invalid OTP or expired')
        
        if user_otp.otp != otp:
            raise AuthenticationFailed('Invalid OTP')
        
        attrs['user'] = user
        attrs['otp_obj'] = user_otp
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        otp_obj = self.validated_data['otp_obj']

        if not user.is_active:
            user.is_active = True
            user.save()

        # delete the otp after successful verification
        otp_obj.delete()

        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']
    
    def validate_email(self, value):
        # We perform the check here but DO NOT send the email yet.
        # This keeps validation idempotent (safe to run multiple times without side effects).
        if not User.objects.filter(email=value).exists():
             raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        # The side effect (sending email) happens here
        email = self.validated_data['email']
        send_otp_via_email(email)


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True, max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        fields = ['email', 'otp', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': "Passwords do not match"})
        
        email = attrs['email']
        otp = attrs['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        try:
            user_otp = OneTimePassword.objects.get(user=user)
        except OneTimePassword.DoesNotExist:
            raise AuthenticationFailed('Invalid OTP or OTP expired.')

        if user_otp.otp != otp:
             raise AuthenticationFailed('Invalid OTP.')
        
        # Determine validated data for save method
        attrs['user'] = user
        attrs['otp_obj'] = user_otp 
        return attrs
    
    def save(self, **kwargs):
        user = self.validated_data['user']
        otp_obj = self.validated_data['otp_obj']
        password = self.validated_data['password']
        
        user.set_password(password)
        user.save()
        
        # Delete OTP after use
        otp_obj.delete()
        
        return user