from rest_framework import serializers
from .models import MonthlyTarget

class MonthlyTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTarget
        fields = ['user', 'month', 'year', 'target']
