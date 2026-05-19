from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from core.views import DualSerializerViewSet
from product.models import (
    Product, Thali, ProductVariant, ProductMedia,
    Attribute, AttributeValue, VariantAttributeValue
)
from product.serializers import (
    ProductRequestSerializer, ProductResponseSerializer,
    ThaliRequestSerializer, ThaliResponseSerializer,
    ProductVariantRequestSerializer, ProductVariantResponseSerializer,
    ProductMediaRequestSerializer, ProductMediaResponseSerializer,
    AttributeRequestSerializer, AttributeResponseSerializer,
    AttributeValueRequestSerializer, AttributeValueResponseSerializer,
    VariantAttributeValueRequestSerializer, VariantAttributeValueResponseSerializer
)

class BaseAdminWriteViewSet(DualSerializerViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

class ProductViewSet(BaseAdminWriteViewSet):
    queryset = Product.objects.all().prefetch_related('variants', 'images')
    request_serializer_class = ProductRequestSerializer
    response_serializer_class = ProductResponseSerializer
    search_fields = ['title', 'sort_description', 'description']
    ordering_fields = ['title', 'created_at']

class ThaliViewSet(BaseAdminWriteViewSet):
    queryset = Thali.objects.all()
    request_serializer_class = ThaliRequestSerializer
    response_serializer_class = ThaliResponseSerializer
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

class ProductVariantViewSet(BaseAdminWriteViewSet):
    queryset = ProductVariant.objects.all().prefetch_related('images')
    request_serializer_class = ProductVariantRequestSerializer
    response_serializer_class = ProductVariantResponseSerializer
    search_fields = ['sku', 'barcode']
    ordering_fields = ['price', 'created_at']

class ProductMediaViewSet(BaseAdminWriteViewSet):
    queryset = ProductMedia.objects.all()
    request_serializer_class = ProductMediaRequestSerializer
    response_serializer_class = ProductMediaResponseSerializer

class AttributeViewSet(BaseAdminWriteViewSet):
    queryset = Attribute.objects.all()
    request_serializer_class = AttributeRequestSerializer
    response_serializer_class = AttributeResponseSerializer

class AttributeValueViewSet(BaseAdminWriteViewSet):
    queryset = AttributeValue.objects.all()
    request_serializer_class = AttributeValueRequestSerializer
    response_serializer_class = AttributeValueResponseSerializer

class VariantAttributeValueViewSet(BaseAdminWriteViewSet):
    queryset = VariantAttributeValue.objects.all()
    request_serializer_class = VariantAttributeValueRequestSerializer
    response_serializer_class = VariantAttributeValueResponseSerializer
