from rest_framework import serializers
from .models import MonthlyTarget
from media_asset.models import Billboards

class MonthlyTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target', 'target_count']
        # read_only_fields = ['user', 'target_count']

class WeeklyUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboards
        fields = ['id', 'user', 'upload_date']