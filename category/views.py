from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from core.views import DualSerializerViewSet
from category.models import Category
from category.serializers import CategoryRequestSerializer, CategoryResponseSerializer

class CategoryViewSet(DualSerializerViewSet):
    queryset = Category.objects.all()
    request_serializer_class = CategoryRequestSerializer
    response_serializer_class = CategoryResponseSerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'level']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
