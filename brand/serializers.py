from rest_framework import serializers
from brand.models import Brand

class BrandRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['user', 'name', 'description', 'logo', 'is_active', 'latitude', 'longitude']

    def validate(self, attrs):
        lat = attrs.get('latitude')
        lon = attrs.get('longitude')
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if lon is not None and (lon < -180 or lon > 180):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})
        return attrs

class BrandResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'user', 'name', 'description', 'logo', 'slug', 'is_active', 'latitude', 'longitude', 'created_at', 'updated_at']