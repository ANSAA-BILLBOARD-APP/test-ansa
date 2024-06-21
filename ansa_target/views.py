from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from . models import Target
from .serializers import TargetSerializer, WeeklyUploadSerializer
from media_asset.models import Billboards
from django.utils import timezone
from datetime import timedelta

class MonthlyTarget(APIView):
    serializer_class = TargetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current_date = timezone.now()
        month = current_date.month
        year = current_date.year
        user = self.request.user
        target = Target.objects.filter(user=user)

        monthly_target, created = Target.objects.get_or_create(user=user, year=year, month=month, defaults={'target': 50})
        target_data = TargetSerializer(monthly_target)
        return Response(target_data.data, status=status.HTTP_200_OK)

