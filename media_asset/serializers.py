from .models import UserZone, Billboards, Zones, Dimensions, AmountPerSqFt
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class AmountPerSqFtSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountPerSqFt
        fields = ['amount_per_sq_ft']

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
        fields = ['sign_type', 'signage_type', 'sign_format', 'no_of_faces', 'illumination_type', 'zone', 'status', 
                  'sub_zone', 'description', 'vacancy', 'dimension', 'actual_size', 'length', 'breadth', 'price', 
                  'payment_status', 'image1', 'image2', 'image3', 'asset_street_address', 'asset_lga', 'state', 
                  'country', 'asin', 'company_name', 'company_phone', 'business_type', 'business_category', 'longitude', 'latitude']

    def validate(self, data):
        validated_data = data.copy()

        required_fields = ['zone', 'image1', 'sign_type', 'sub_zone', 'business_category', 'business_type']
        validated_data['status'] = 'completed' if all(validated_data.get(field) for field in required_fields) else 'pending'

        return validated_data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class DimensionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimensions
        fields = ['id', 'name', 'min_width', 'max_width', 'zone', 'price']

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
        fields = ['signage_type', 'sign_type', 'sign_format', 'no_of_faces', 'illumination_type', 'length', 'breadth', 'zone', 'status', 'sub_zone', 'description',
                  'vacancy', 'status', 'dimension', 'actual_size', 'price', 'payment_status', 'payment_date', 'image1',
                  'image2', 'image3', 'asset_street_address', 'asset_lga', 'state', 'country',
                   'asin', 'business_type', 'company_name', 'company_phone', 'business_category', 'longitude', 'latitude']   