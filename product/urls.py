from django.urls import path, include
from rest_framework.routers import DefaultRouter
from product.views import (
    ProductViewSet, ThaliViewSet, ProductVariantViewSet, ProductMediaViewSet,
    AttributeViewSet, AttributeValueViewSet, VariantAttributeValueViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'thalis', ThaliViewSet, basename='thali')
router.register(r'product-variants', ProductVariantViewSet, basename='product-variant')
router.register(r'product-media', ProductMediaViewSet, basename='product-media')
router.register(r'attributes', AttributeViewSet, basename='attribute')
router.register(r'attribute-values', AttributeValueViewSet, basename='attribute-value')
router.register(r'variant-attribute-values', VariantAttributeValueViewSet, basename='variant-attribute-value')

urlpatterns = [
    path('', include(router.urls)),
]
