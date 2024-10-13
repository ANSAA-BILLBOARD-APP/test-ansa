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
from rest_framework import status
from . serializers import LogoutSerializer, ProfileSerializer, LoginSerializer, PasswordResetRequestSerializer
from . models import AnsaaUser, OTP
from todo.models import Task
from drf_spectacular.utils import extend_schema


@extend_schema(
    request=LogoutSerializer,
    responses={status.HTTP_200_OK: LogoutSerializer},
    description='The endpoint is use to logout user by blacklisting their tokens',
    tags=["Authentication"],
    summary='User logout',
)
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


@extend_schema(
    request=ProfileSerializer,
    responses={status.HTTP_200_OK: ProfileSerializer},
    description='User profile endpoint, to get user details and also update user details',
    tags=["Authentication"],
    summary='User Profile',
)
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
    request=LoginSerializer,
    responses={status.HTTP_200_OK: LoginSerializer},
    description='The users "phone number" or "email" is required for authentication on this login endpoint.',
    tags=["Authentication"],
    summary='User Login',
)
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            user = AnsaaUser.objects.filter(email=email).first()
            if not user:
                return Response(
                    {'error': 'User with this email does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            authenticated_user = authenticate(request, email=email, password=password)

            if authenticated_user:
                refresh = RefreshToken.for_user(authenticated_user)

                return Response(
                    {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Return serializer errors if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetAPIView(APIView):
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            
            try:
                user = AnsaaUser.objects.get(email=email)
                
                # prepare user details
                fullname = user.fullname
                email = user.email
                
                # get admin users
                admins = AnsaaUser.objects.filter(is_superuser=True, active=True)
                
                
            except:
                pass
                
                