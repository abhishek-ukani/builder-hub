from django.urls import path, include
from rest_framework.routers import DefaultRouter
from order.views import (
    OrderViewSet, ReturnViewSet, ReturnItemViewSet, DeliveryViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'returns', ReturnViewSet, basename='return')
router.register(r'return-items', ReturnItemViewSet, basename='return-item')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')

urlpatterns = [
    path('', include(router.urls)),
]
