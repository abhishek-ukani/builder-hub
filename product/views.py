from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from core.views import DualSerializerViewSet
from product.models import (
    Product,
    Thali,
    ProductVariant,
    ProductMedia,
    Attribute,
    AttributeValue,
    VariantAttributeValue,ThaliComponentGroup,ThaliComponentOption
)
from product.serializers import (
    ProductRequestSerializer,
    ProductResponseSerializer,
    ThaliRequestSerializer,
    ThaliResponseSerializer,
    ProductVariantRequestSerializer,
    ProductVariantResponseSerializer,
    ProductMediaRequestSerializer,
    ProductMediaResponseSerializer,
    AttributeRequestSerializer,
    AttributeResponseSerializer,
    AttributeValueRequestSerializer,
    AttributeValueResponseSerializer,
    VariantAttributeValueRequestSerializer,
    VariantAttributeValueResponseSerializer,
    CategoryWithProductsSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from category.models import Category
from django.db.models import Window, F, Prefetch, Avg, Count
from django.db.models.functions import RowNumber
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from product.recommender import get_collaborative_recommendations, get_hybrid_recommendations


class BaseAdminWriteViewSet(DualSerializerViewSet):
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class CategoryScrollPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10


class CategoryProductsHomeViewSet(BaseAdminWriteViewSet):
    queryset = Category.objects.filter(is_active=True)
    response_serializer_class = CategoryWithProductsSerializer

    def get_queryset(self):

        # Only variants that are NOT thali components
        valid_variants = ProductVariant.objects.filter(is_thali_component=False)

        # Products having at least one non-thali variant with rating annotations
        annotated_products = (
            Product.objects.filter(is_active=True, variants__is_thali_component=False)
            .distinct()
            .annotate(
                row_num=Window(
                    expression=RowNumber(),
                    partition_by=[F("category_id")],
                    order_by=F("created_at").desc(),
                ),
                average_rating=Avg("ratings__rating"),
                rating_count=Count("ratings", distinct=True)
            )
        )

        products = Product.objects.filter(
            id__in=annotated_products.values("id")
        ).prefetch_related(Prefetch("variants", queryset=valid_variants), "images").annotate(
            average_rating=Avg("ratings__rating"),
            rating_count=Count("ratings", distinct=True)
        )

        return Category.objects.filter(is_active=True).prefetch_related(
            Prefetch("products", queryset=products, to_attr="initial_products")
        )

    def list(self, request, *args, **kwargs):
        # 1. Get standard categories list
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginate if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
        # 2. Get recommendations if user is authenticated
        user = request.user
        if user and user.is_authenticated:
            try:
                k = int(request.query_params.get("k", 5))
            except ValueError:
                k = 5
            try:
                alpha = float(request.query_params.get("alpha", 0.7))
            except ValueError:
                alpha = 0.7
                
            exclude_ordered = request.query_params.get("exclude_ordered", "true").lower() in ["true", "1", "yes"]
            recommended_products = get_hybrid_recommendations(user.id, k=k, alpha=alpha, exclude_ordered=exclude_ordered)
            if recommended_products:
                # Serialize the products
                from product.serializers import ProductResponseSerializer
                serialized_products = ProductResponseSerializer(
                    recommended_products, many=True, context=self.get_serializer_context()
                ).data
                
                # Prepend the pseudo-category
                recommendations_category = {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "name": "Recommended for You",
                    "slug": "recommended-for-you",
                    "products": serialized_products
                }
                data.insert(0, recommendations_category)
                
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk == "00000000-0000-0000-0000-000000000000":
            user = request.user
            if user and user.is_authenticated:
                try:
                    k = int(request.query_params.get("k", 5))
                except ValueError:
                    k = 5
                try:
                    alpha = float(request.query_params.get("alpha", 0.7))
                except ValueError:
                    alpha = 0.7
                    
                exclude_ordered = request.query_params.get("exclude_ordered", "true").lower() in ["true", "1", "yes"]
                recommended_products = get_hybrid_recommendations(user.id, k=k, alpha=alpha, exclude_ordered=exclude_ordered)
                from product.serializers import ProductResponseSerializer
                serialized_products = ProductResponseSerializer(
                    recommended_products, many=True, context=self.get_serializer_context()
                ).data
                return Response({
                    "id": "00000000-0000-0000-0000-000000000000",
                    "name": "Recommended for You",
                    "slug": "recommended-for-you",
                    "products": serialized_products
                })
            else:
                return Response(
                    {"detail": "Authentication credentials were not provided or no recommendations found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        return super().retrieve(request, *args, **kwargs)


@method_decorator(cache_page(9000), name="list")
class ProductViewSet(BaseAdminWriteViewSet):
    queryset = Product.objects.all().prefetch_related("variants", "images")
    request_serializer_class = ProductRequestSerializer
    response_serializer_class = ProductResponseSerializer
    search_fields = ["title", "sort_description", "description"]
    ordering_fields = ["title", "created_at"]

    @action(detail=False, methods=["get"], url_path="category/(?P<category_id>[^/.]+)")
    def by_category(self, request, category_id=None):
        """
        URL Target: /api/products/category/<category_id>/?limit=10&offset=10
        """
        # Filter products matching targeted category path
        products = (
            Product.objects.filter(category_id=category_id, is_active=True)
            .order_by("-created_at")
            .prefetch_related("variants", "images")
        )

        # Initialize the pagination engine
        paginator = CategoryScrollPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ThaliViewSet(BaseAdminWriteViewSet):
    request_serializer_class = ThaliRequestSerializer
    response_serializer_class = ThaliResponseSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        options_prefetch = Prefetch(
        'options',
        queryset=ThaliComponentOption.objects.select_related('product_variant__product')
    )

        # 2. Middle prefetch: Grab groups and attach the optimized options query inside them
        groups_prefetch = Prefetch(
            'component_groups',
            queryset=ThaliComponentGroup.objects.prefetch_related(options_prefetch)
        )

        # 3. Execution: Fetch active Thalis with the entire pre-loaded tree structure
        return Thali.objects.filter(is_active=True).prefetch_related(groups_prefetch)
        


class ProductVariantViewSet(BaseAdminWriteViewSet):
    queryset = ProductVariant.objects.all().prefetch_related("images")
    request_serializer_class = ProductVariantRequestSerializer
    response_serializer_class = ProductVariantResponseSerializer
    search_fields = ["sku", "barcode"]
    ordering_fields = ["price", "created_at"]


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
