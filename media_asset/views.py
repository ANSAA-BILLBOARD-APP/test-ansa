from django.shortcuts import render
from . serializers import CreateBillboardSerializer, AssetSerializer, ZonesSerializer
from rest_framework.generics import ListAPIView
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
from .models import Billboards, Zones
from drf_spectacular.utils import extend_schema


class CreateAssetAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateBillboardSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateBillboardSerializer(data=request.data)
        user = request.user.id
        
        if serializer.is_valid():
            serializer.save(user_id=user)

            add_media_task = Task.objects.get(user=user, title="Add a Media Asset")
            add_media_task.is_completed = True
            add_media_task.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
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



# class AssetSearchAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = AssetSerializer

#     def get(self, request, *args, **kwargs):
#         try:
#             # Retrieve query parameters
#             asset_type = request.query_params.get('asset_type', None)
#             zone = request.query_params.get('zone', None)
#             vacancy = request.query_params.get('vacancy', None)
#             status = request.query_params.get('status', None)

#             # Filter billboards based on query parameters
#             assets = Billboards.objects.filter(user=request.user)
            
#             if asset_type:
#                 if not Billboards.objects.filter(asset_type=asset_type).exists():
#                     raise ValidationError(f"Invalid asset_type: {asset_type}")
#                 assets = assets.filter(asset_type=asset_type)
            
#             if zone:
#                 if not Billboards.objects.filter(zone=zone).exists():
#                     raise ValidationError(f"Invalid zone: {zone}")
#                 assets = assets.filter(zone=zone)
            
#             if status:
#                 if not Billboards.objects.filter(status=status).exists():
#                     raise ValidationError(f"Invalid status: {status}")
#                 assets = assets.filter(status=status)
            
#             if vacancy is not None:
#                 try:
#                     vacancy = bool(int(vacancy))
#                 except ValueError:
#                     raise ValidationError(f"Invalid vacancy value: {vacancy}, must be 0 or 1")
#                 assets = assets.filter(vacancy=vacancy)

#             # Serialize and return the data
#             serializer = AssetSerializer(assets, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except ValidationError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         except Billboards.DoesNotExist:
#             return Response({'error': 'Billboards not found'}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZonesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Zones.objects.all()
    serializer_class = ZonesSerializer