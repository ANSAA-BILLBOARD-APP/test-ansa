from django.shortcuts import render
from . serializers import CreateBillboardSerializer, AssetSerializer, ZonesSerializer, DimensionsSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import AnsaaUser
from todo.models import Task
from .models import Billboards, Zones, Dimensions
from drf_spectacular.utils import extend_schema
import logging
logger = logging.getLogger(__name__)
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError



class CreateAssetAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateBillboardSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateBillboardSerializer(data=request.data)
        user = request.user.id

        if serializer.is_valid():
            serializer.save(user_id=user)
                

            # Check the task status and update if necessary
            try:
                tasks = Task.objects.filter(user=user, title="Add a Media Asset")

                if tasks.exists():
                    task = tasks.first()  # Or handle multiple tasks as needed
                    if not task.is_completed:
                        task.is_completed = True
                        task.save()
                else:
                    logger.info(f"Task 'Add a Media Asset' for user {user} is already completed.")

            except ObjectDoesNotExist:
                logger.warning(f"Task 'Add a Media Asset' not found for user {user}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Billboards.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class AssetListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer

    def get_queryset(self):
        user = self.request.user
        return Billboards.objects.filter(user=user)

class AssetDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer

    def delete(self, request, pk, *args, **kwargs):
        try:
            # Retrieve the object using the primary key (pk)
            asset = Billboards.objects.get(pk=pk)
            asset_name = asset.asset_name 
            asset.delete()

            # Return a custom response with a success message
            return Response(
                {"message": f"'{asset_name}' has been successfully deleted."},
                status=status.HTTP_200_OK
            )
        except Billboards.DoesNotExist:
            # If the asset is not found, return a not found response
            return Response(
                {"error": "Billboard not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Handle any other exceptions that may occur
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

            
@extend_schema(
    description="The endpoint is use to filter media assets by (asset type, zone, status and vacancy).",
    summary='Media Search(Filter) endpoint'
)
class AssetSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer

    def get(self, request, *args, **kwargs):
        # Retrieve query parameters
        asset_type = request.query_params.get('asset_type', None)
        zone = request.query_params.get('zone', None)
        vacancy = request.query_params.get('vacancy', None)
        status_param = request.query_params.get('status', None)
        user = request.user

        # Filter billboards based on query parameters
        assets = Billboards.objects.filter(user=user)
        if asset_type is not None:
            assets = assets.filter(asset_type=asset_type)
        if zone is not None:
            assets = assets.filter(zone=zone)
        if status_param is not None:
            assets = assets.filter(status=status_param)
        if vacancy is not None:
            assets = assets.filter(vacancy=vacancy)

        serializer = self.serializer_class(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ZonesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Zones.objects.all()
    serializer_class = ZonesSerializer

class DimensionsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Dimensions.objects.all()
    serializer_class = DimensionsSerializer