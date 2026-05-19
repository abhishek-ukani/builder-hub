from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from core.views import DualSerializerViewSet
from brand.models import Brand
from brand.serializers import BrandRequestSerializer, BrandResponseSerializer

class BrandViewSet(DualSerializerViewSet):
    queryset = Brand.objects.all()
    request_serializer_class = BrandRequestSerializer
    response_serializer_class = BrandResponseSerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
