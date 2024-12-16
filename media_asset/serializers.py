from .models import UserZone, Billboards, Zones, Dimensions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class ZonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zones
        fields = ['id', 'name']

class UserZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserZone
        fields = '__all__'


class CreateBillboardSerializer(serializers.ModelSerializer):
    sub_zone = serializers.SlugRelatedField(
        queryset=Zones.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = Billboards
        fields = ['asset_type', 'category', 'zone', 'status', 'sub_zone', 'description',
                  'vacancy', 'status', 'dimension', 'actual_dimension', 'price', 'main_image', 'image_1',
                  'image_2', 'image_3', 'address', 'city', 'state', 'country', 'company',
                  'phone_number', 'longitude', 'latitude']

    def validate(self, data):
        # Check the fields to determine if the status should be "complete"
        fields_to_check = ['category', 'zone', 'main_image', 'company', 'asset_type', 'sub_zone']
        if not all(data.get(field) for field in fields_to_check):
            data['status'] = 'pending'

        else:
            data['status'] = 'completed'

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class DimensionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimensions
        fields = ['id', 'name', 'min_width', 'max_width', 'category', 'zone', 'price']

class AssetSerializer(serializers.ModelSerializer):
    sub_zone = serializers.SlugRelatedField(
        queryset=Zones.objects.all(),
        slug_field='name'
    )
    
    class Meta:
        model = Billboards
        fields = '__all__'


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billboards
        fields = ['payment_status', 'payment_date']

    def validate_payment_status(self, value):
        if value not in dict(Billboards.PAYMENT_CHOICES):
            raise serializers.ValidationError("Invalid payment status.")
        return value 


class AssetsDetailsSerializer(serializers.ModelSerializer):
    sub_zone = serializers.SlugRelatedField(
        queryset=Zones.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = Billboards
        fields = ['asset_type', 'category', 'zone', 'status', 'sub_zone', 'description',
                  'vacancy', 'status', 'dimension', 'actual_dimension', 'price', 'payment_status', 'payment_date', 'main_image', 'image_1',
                  'image_2', 'image_3', 'address', 'city', 'state', 'country', 'company',
                  'phone_number', 'longitude', 'latitude']   