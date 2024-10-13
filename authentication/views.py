from django.shortcuts import render
from rest_framework.exceptions import NotFound
from django.db import DatabaseError
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework import status
from . serializers import RequestOTPSerializer, LogoutSerializer, OTPVerificationSerializer, ProfileSerializer, LoginSerializer
from . models import AnsaaUser, OTP
from todo.models import Task
from . task import generate_otp, EmailThread, send_otp_email, send_otp_sms
import asyncio
from drf_spectacular.utils import extend_schema



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViews(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        user = request.user
        try:  
            user_profile = AnsaaUser.objects.get(pk=user.pk)
            serializer = ProfileSerializer(user_profile)
            return Response(serializer.data)
        except AnsaaUser.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        user = request.user
        user_profile = AnsaaUser.objects.get(pk=user.pk)
        if not user_profile:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        picture = request.data.get('picture')
        if not picture:
            return Response({'error': 'Picture field is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.picture = picture
        user_profile.save()

        update_profile_task = Task.objects.get(user=user, title="Add a Profile Picture")

        if update_profile_task:
            if not update_profile_task.is_completed:
                update_profile_task.is_completed = True
                update_profile_task.save()
        else:
            pass

        serializer = ProfileSerializer(user_profile)
        return Response(serializer.data)

@extend_schema(
    description='The users "phone number" or "email" is required for authentication on this login endpoint.',
    summary='User Login'
)
class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            phone_number = serializer.validated_data.get("phone_number")
            

            #if otp is in record and it's verified
            existing_otp = OTP.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
            ).first()
            if existing_otp:
                email = existing_otp.email
                if email:
                    otp_record = OTP.objects.get(email=email, verified=True)
                    if not otp_record.is_expired():
                        user = AnsaaUser.objects.filter(email=email).first()
                        authenticated_user = authenticate(request, email=email)
                        if authenticated_user:
                            refresh = RefreshToken.for_user(authenticated_user)
                            otp_record.delete()

                            return Response({'refresh': str(refresh), 'access': str(refresh.access_token),}, status=status.HTTP_200_OK)  
                        else:
                            return Response({'error': 'Invalid user credentials'}, status.status.HTTP_400_BAD_REQUEST)
                    else:
                        otp_record.delete()
                        return Response({'error':'OTP expired, request for another'}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({'error': 'Invalid user credentials'}, status=status.HTTP_400_BAD_REQUEST)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

