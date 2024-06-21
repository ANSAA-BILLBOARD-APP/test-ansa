from rest_framework import serializers
from .models import Target
from media_asset.models import Billboards
from datetime import timedelta
from django.utils import timezone


class TargetSerializer(serializers.ModelSerializer):
    weekly_target = serializers.SerializerMethodField()
    weekly_count = serializers.SerializerMethodField()

    class Meta:
        model = Target
        fields = ['id', 'user', 'month', 'year', 'target', 'target_count', 'weekly_target', 'weekly_count']
        read_only_fields = ['user', 'target_count', 'weekly_target', 'weekly_count']

    def get_weekly_target(self, obj):
        # Safely divide the target by 4 to get the weekly target
        if obj.target:
            return round(obj.target / 4)
        return 0

    def get_weekly_count(self, obj):
        # Get the current date
        current_date = timezone.now()

        # Calculate the start and end of the current week
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Get the count of uploads for the current week
        weekly_count = Billboards.objects.filter(
            user=obj.user,
            date__range=[start_of_week, end_of_week]  # Ensure 'upload_date' is the correct field
        ).count()

        return weekly_count

class WeeklyUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboards
        fields = ['id', 'user', 'date']