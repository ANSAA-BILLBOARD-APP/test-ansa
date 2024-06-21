from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from . models import MonthlyTarget
from .serializers import MonthlyTargetSerializer, WeeklyUploadSerializer
from media_asset.models import Billboards
from django.utils import timezone
from datetime import timedelta

class MonthlyTarget(APIView):
    # serializer_class = MonthlyTargetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        current_date = timezone.now()
        month = current_date.month
        year = current_date.year

        monthly_target, created = MonthlyTarget.objects.get_or_create(user=instance.user, year=year, month=month, defaults={'target': 50})
        target_data = MonthlyTargetSerializer(monthly_target).data

        # Calculate start and end of the current week
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Get all uploads for the current week
        weekly_uploads = Billboard.objects.filter(
            user=user,
            upload_date__range=[start_of_week, end_of_week]
        )
        weekly_upload_data = WeeklyUploadSerializer(weekly_uploads, many=True).data

        return Response({
            'current_month_target': target_data,
            'weekly_uploads': weekly_upload_data
        })
