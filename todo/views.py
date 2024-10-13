from django.shortcuts import render
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework import status
from . serializers import DeviceDetailSerializer, TaskSerializer
from . models import DeviceDetail, Task
import asyncio
from drf_spectacular.utils import extend_schema
import logging
logger = logging.getLogger(__name__)
from drf_spectacular.utils import extend_schema



@extend_schema(
    request=DeviceDetailSerializer,
    responses={status.HTTP_201_CREATED: DeviceDetailSerializer},
    description='User device verificaion',
    tags=["Todo"],
    summary='Verify and save user device details',
)
class DeviceCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceDetailSerializer

    def post(self, request, *args, **kwargs):
        serializer = DeviceDetailSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            serializer.save(user=request.user)

            try:
                update_davice_task = Task.objects.get(user=user, title="Approve Device")

                if not update_davice_task.is_completed:
                    update_davice_task.is_completed = True
                    update_davice_task.save()
                else:
                    logger.info(f"Task 'Approve Device' for user {user.fullname} is already completed.")

            except Task.DoesNotExist:
                logger.warning(f"Task 'Approve Device' not found for user {user}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=DeviceDetailSerializer,
    responses={status.HTTP_200_OK: DeviceDetailSerializer},
    tags=["Todo"],
)
class DeviceListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceDetailSerializer

    def get(self, request, format=None):
        # Retrieve all devices for the authenticated user
        devices = DeviceDetail.objects.filter(user=request.user)
        serializer = DeviceDetailSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@extend_schema(
    request=TaskSerializer,
    responses={status.HTTP_200_OK: TaskSerializer},
    tags=["Todo"],
)
class DeviceUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


@extend_schema(
    request=TaskSerializer,
    responses={status.HTTP_200_OK: TaskSerializer},
    description='List all user task',
    tags=["Todo"],
    summary='List all available task/todos',
)
class TaskAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(user=user)