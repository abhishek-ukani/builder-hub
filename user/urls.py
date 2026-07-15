from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserAddressViewSet, WishlistItemViewSet

router = DefaultRouter()
router.register(r'addresses', UserAddressViewSet, basename='user-address')
router.register(r'wishlist', WishlistItemViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
