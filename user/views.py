from rest_framework.permissions import IsAuthenticated
from core.views import DualSerializerViewSet
from user.models import UserAddress, WishlistItem
from user.serializers import (
    UserAddressRequestSerializer, UserAddressResponseSerializer,
    WishlistItemRequestSerializer, WishlistItemResponseSerializer
)

class BaseUserViewSet(DualSerializerViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserAddressViewSet(BaseUserViewSet):
    queryset = UserAddress.objects.all()
    request_serializer_class = UserAddressRequestSerializer
    response_serializer_class = UserAddressResponseSerializer
    search_fields = ['full_name', 'city', 'pincode']

class WishlistItemViewSet(BaseUserViewSet):
    queryset = WishlistItem.objects.all()
    request_serializer_class = WishlistItemRequestSerializer
    response_serializer_class = WishlistItemResponseSerializer
