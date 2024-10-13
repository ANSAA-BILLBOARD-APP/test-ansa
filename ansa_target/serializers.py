from rest_framework import serializers
from .models import Target
from media_asset.models import Billboards
from datetime import timedelta
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field



class TargetSerializer(serializers.ModelSerializer):
    weekly_target = serializers.SerializerMethodField()
    weekly_count = serializers.SerializerMethodField()

    class Meta:
        model = Target
        fields = ['id', 'user', 'month', 'year', 'target', 'target_count', 'weekly_target', 'weekly_count']
        read_only_fields = ['user', 'target_count', 'weekly_target', 'weekly_count']

    @extend_schema_field(serializers.IntegerField) # Specifying the expected return type for schema
    def get_weekly_target(self, obj) -> int:

        if obj.target:
            return round(obj.target / 4)
        return 0

    @extend_schema_field(serializers.IntegerField)  # Specifying the expected return type for schema
    def get_weekly_count(self, obj) -> int:

        current_date = timezone.now()

        # Calculate the start and end of the current week
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Count uploads for the current week (ensure 'date' is the upload date field)
        weekly_count = Billboards.objects.filter(
            user=obj.user,
            date__range=[start_of_week, end_of_week]  # Ensure 'date' is the correct field for filtering uploads
        ).count()

        return weekly_count


class WeeklyUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboards
        fields = ['id', 'user', 'date']