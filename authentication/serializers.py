from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from phonenumber_field.serializerfields import PhoneNumberField
from .models import AnsaaUser, OTP

 


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsaaUser
        fields = ['user_id', 'email', 'phone_number', 'fullname', 'picture', 'gender']
        read_only_fields = ['email', 'user_id']


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
