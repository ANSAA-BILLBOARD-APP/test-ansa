from django.shortcuts import render
from . serializers import CreateBillboardSerializer, AssetSerializer, AmountPerSqFtSerializer, ZonesSerializer, DimensionsSerializer, PaymentUpdateSerializer, AssetsDetailsSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import AnsaaUser
from todo.models import Task
from .models import Billboards, Zones, Dimensions, AmountPerSqFt
from drf_spectacular.utils import extend_schema
import logging
logger = logging.getLogger(__name__)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .decorator import apikey_required


class AmountPerSqFtListView(ListAPIView):
    queryset = AmountPerSqFt.objects.all()
    serializer_class = AmountPerSqFtSerializer


@extend_schema(
    request=CreateBillboardSerializer,
    responses={status.HTTP_201_CREATED: CreateBillboardSerializer},
    description='Upload media asset to the database',
    tags=["Media Assets"],
    summary='Upload media asset',
)
class CreateAssetAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateBillboardSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateBillboardSerializer(data=request.data)
        user = request.user.id

        if serializer.is_valid():
            serializer.save(user=request.user)                

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


@extend_schema(
    request=AssetSerializer,
    responses={status.HTTP_201_CREATED: AssetSerializer},
    tags=["Media Assets"],
)
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


@extend_schema(
    request=AssetSerializer,
    responses={status.HTTP_200_OK: AssetSerializer},
    description='List all uploaded media assets from database',
    tags=["Media Assets"],
    summary='List all uploaded media assets',
)
class AssetListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer

    def get_queryset(self):
        user = self.request.user
        return Billboards.objects.filter(user=user)




@extend_schema(
    request=AssetSerializer,
    responses={status.HTTP_200_OK: AssetSerializer},
    description='Delete media asset',
    tags=["Media Assets"],
    summary='Delete media asset from database',
)
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
    description="The endpoint is use to filter media assets by (sign type, zone, status and vacancy).",
    summary='Media Search(Filter) endpoint',
    tags=["Media Assets"],
)
class AssetSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer

    def get(self, request, *args, **kwargs):
        # Retrieve query parameters
        sign_type = request.query_params.get('sign_type', None)
        zone = request.query_params.get('zone', None)
        vacancy = request.query_params.get('vacancy', None)
        status_param = request.query_params.get('status', None)
        user = request.user

        # Filter billboards based on query parameters
        assets = Billboards.objects.filter(user=user)
        if sign_type is not None:
            assets = assets.filter(sign_type=sign_type)
        if zone is not None:
            assets = assets.filter(zone=zone)
        if status_param is not None:
            assets = assets.filter(status=status_param)
        if vacancy is not None:
            assets = assets.filter(vacancy=vacancy)

        serializer = self.serializer_class(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="List of Zone in Anambra",
    summary='List all zone in Anambra',
    tags=["Media Assets"],
)
class ZonesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Zones.objects.all()
    serializer_class = ZonesSerializer


@extend_schema(
    description="Media assets dimension for determining assets price",
    summary='List all Media Assets dimensions',
    tags=["Media Assets"],
)
class DimensionsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Dimensions.objects.all()
    serializer_class = DimensionsSerializer


# oasis endpoints

@extend_schema(
    request=AssetsDetailsSerializer,
    responses={status.HTTP_200_OK: AssetsDetailsSerializer},
    description='List all uploaded media assets from database',
    tags=["Media Assets"],
    summary='List all uploaded media assets',
)
class AssetDetailsListAPIView(generics.ListAPIView):
    serializer_class = AssetsDetailsSerializer
    @apikey_required
    def get_queryset(self):
        return Billboards.objects.filter(status="completed")


@extend_schema(
    request=PaymentUpdateSerializer,
    responses={status.HTTP_200_OK: {'message': 'Payment details updated successfully!'}},
    description='Update payment status and payment date for a billboard asset.',
    tags=["Media Assets"],
    summary='Update Payment Details',
)
class UpdatePaymentView(APIView):
    @apikey_required
    def post(self, request, unique_id):
        billboard = get_object_or_404(Billboards, unique_id=unique_id)
        serializer = PaymentUpdateSerializer(billboard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Payment details updated successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
