from rest_framework import serializers
from .models import AnsaaUser



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnsaaUser
        fields = ['user_id', 'email', 'phone_number', 'fullname', 'picture', 'gender']
        read_only_fields = ['email', 'user_id']


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
