from rest_framework import serializers
from user.models import UserAddress, WishlistItem

class UserAddressRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        exclude = ['user', 'created_at', 'updated_at', 'id']

    def validate(self, attrs):
        lat = attrs.get('latitude')
        lon = attrs.get('longitude')
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if lon is not None and (lon < -180 or lon > 180):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})
        return attrs

class UserAddressResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'

class WishlistItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['variant']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        variant = attrs.get('variant')
        
        if user and variant and not self.instance:
            if WishlistItem.objects.filter(user=user, variant=variant).exists():
                raise serializers.ValidationError({"variant": "This item is already in your wishlist."})
        return attrs

class WishlistItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all__'

