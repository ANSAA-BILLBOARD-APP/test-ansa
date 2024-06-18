from .models import UserZone, Billboards, Zones, Dimensions
from rest_framework import serializers


class ZonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zones
        fields = ['id', 'name']

class UserZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserZone
        fields = '__all__'


class CreateBillboardSerializer(serializers.ModelSerializer):
    # sub_zone = serializers.CharField(source='sub_zone.name', read_only=True)
    sub_zone = serializers.SlugRelatedField(
        queryset=Zones.objects.all(),
        slug_field='name'
    )
    
    class Meta:
        model = Billboards
        fields = ['asset_type','category','zone','status','sub_zone','description'
        ,'vacancy','status','dimension','price','main_image','image_1','image_2','image_3'
        ,'address','city','state','country','company','phone_number','longitude','latitude','user_id']
    

    def validate(self, data):
        # Check the fields to determine if the status should be "complete"
        fields_to_check = ['category', 'zone', 'main_image', 'company', 'asset_type', 'sub_zone']
        if all(data.get(field) for field in fields_to_check):
            data['status'] = 'completed'
        else:
            data['status'] = data.get('status', 'pending')

        return data

    def create(self, validated_data):
        # Custom creation logic if needed
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Custom update logic if needed
        return super().update(instance, validated_data)

class DimensionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimensions
        fields = ['id', 'name', 'min_width', 'max_width', 'category', 'zone', 'price']

class AssetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Billboards
        fields = '__all__'