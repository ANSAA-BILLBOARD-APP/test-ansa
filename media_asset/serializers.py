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
        fields = ['sign_type', 'signage_type', 'sign_format', 'no_of_faces', 'illumination_type', 'category', 'zone', 'status', 'sub_zone', 'description',
                  'vacancy', 'status', 'dimension', 'actual_size', 'length', 'breadth', 'price', 'payment_status', 'image1', 'image2', 'image3',
                  'asset_street_address', 'asset_lga', 'state', 'country', 'company_name', 'company_phone', 'asin', 'business_type',
                  'business_category', 'longitude', 'latitude']

    def validate(self, data):
        # Check the fields to determine if the status should be "complete"
        fields_to_check = ['category', 'zone', 'image1', 'company_name', 'sign_type', 'sub_zone', 'business_category', 'business_type']
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
        fields = ['signage_type', 'sign_type', 'sign_format', 'no_of_faces', 'illumination_type', 'length', 'breadth', 'category', 'zone', 'status', 'sub_zone', 'description',
                  'vacancy', 'status', 'dimension', 'actual_size', 'price', 'payment_status', 'payment_date', 'image1',
                  'image2', 'image3', 'asset_street_address', 'asset_lga', 'state', 'country', 'company_name',
                  'company_number', 'asin', 'business_type', 'business_category', 'longitude', 'latitude']   