from rest_framework.permissions import IsAdminUser
from core.views import DualSerializerViewSet
from supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem
from supplier.serializers import (
    SupplierRequestSerializer, SupplierResponseSerializer,
    PurchaseOrderRequestSerializer, PurchaseOrderResponseSerializer,
    PurchaseOrderItemRequestSerializer, PurchaseOrderItemResponseSerializer
)

class SupplierViewSet(DualSerializerViewSet):
    queryset = Supplier.objects.all()
    request_serializer_class = SupplierRequestSerializer
    response_serializer_class = SupplierResponseSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['name', 'email', 'phone', 'gst_number']
    ordering_fields = ['name', 'created_at']

class PurchaseOrderViewSet(DualSerializerViewSet):
    queryset = PurchaseOrder.objects.all().prefetch_related('items')
    request_serializer_class = PurchaseOrderRequestSerializer
    response_serializer_class = PurchaseOrderResponseSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['po_number']
    ordering_fields = ['ordered_at', 'status']

class PurchaseOrderItemViewSet(DualSerializerViewSet):
    queryset = PurchaseOrderItem.objects.all()
    request_serializer_class = PurchaseOrderItemRequestSerializer
    response_serializer_class = PurchaseOrderItemResponseSerializer
    permission_classes = [IsAdminUser]
