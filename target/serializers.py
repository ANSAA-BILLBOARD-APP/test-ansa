from rest_framework import serializers
from .models import MonthlyTarget

class MonthlyTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target', 'target_count']
        read_only_fields = ['user', 'target_count']
