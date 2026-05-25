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
    VariantAttributeValueRequestSerializer, VariantAttributeValueResponseSerializer,CategoryWithProductsSerializer
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from category.models import Category
from django.db.models import Window, F, Prefetch
from django.db.models.functions import RowNumber
from rest_framework.decorators import action    
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

class BaseAdminWriteViewSet(DualSerializerViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
class CategoryScrollPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10

class CategoryProductsHomeViewSet(BaseAdminWriteViewSet):
    queryset = Category.objects.filter(is_active=True)
    response_serializer_class = CategoryWithProductsSerializer


    def get_queryset(self):
        # FIX: Changed F('-created_at') to F('created_at').desc()
        annotated_products = Product.objects.filter(is_active=True).annotate(
            row_num=Window(
                expression=RowNumber(),
                partition_by=[F('category_id')],
                order_by=F('created_at').desc()  # <-- Crucial Fix here
            )
        )
        
        # Stage 2: Extract IDs based on window criteria
        products = Product.objects.filter(
            id__in=annotated_products.values('id')
        ).prefetch_related('variants', 'images')
        # Stage 3: Bind to Category
        return Category.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'products',
                queryset=products,
                to_attr='initial_products'
            )
        )
        
    
@method_decorator(cache_page(9000), name='list')
class ProductViewSet(BaseAdminWriteViewSet):
    queryset = Product.objects.all().prefetch_related('variants', 'images')
    request_serializer_class = ProductRequestSerializer
    response_serializer_class = ProductResponseSerializer
    search_fields = ['title', 'sort_description', 'description']
    ordering_fields = ['title', 'created_at']

    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        URL Target: /api/products/category/<category_id>/?limit=10&offset=10
        """
        # Filter products matching targeted category path
        products = Product.objects.filter(
            category_id=category_id, 
            is_active=True
        ).order_by('-created_at').prefetch_related('variants', 'images')

        # Initialize the pagination engine
        paginator = CategoryScrollPagination()
        page = paginator.paginate_queryset(products, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

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
