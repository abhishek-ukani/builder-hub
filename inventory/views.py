from rest_framework.permissions import IsAdminUser
from core.views import DualSerializerViewSet
from inventory.models import Warehouse, Inventory, InventoryTransaction, StockTransfer, StockTransferItems
from inventory.serializers import (
    WarehouseRequestSerializer, WarehouseResponseSerializer,
    InventoryRequestSerializer, InventoryResponseSerializer,
    InventoryTransactionRequestSerializer, InventoryTransactionResponseSerializer,
    StockTransferRequestSerializer, StockTransferResponseSerializer,
    StockTransferItemsRequestSerializer, StockTransferItemsResponseSerializer
)

class WarehouseViewSet(DualSerializerViewSet):
    queryset = Warehouse.objects.all()
    request_serializer_class = WarehouseRequestSerializer
    response_serializer_class = WarehouseResponseSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['name', 'code', 'city', 'state']
    ordering_fields = ['name', 'code']

class InventoryViewSet(DualSerializerViewSet):
    queryset = Inventory.objects.all()
    request_serializer_class = InventoryRequestSerializer
    response_serializer_class = InventoryResponseSerializer
    permission_classes = [IsAdminUser]

class InventoryTransactionViewSet(DualSerializerViewSet):
    queryset = InventoryTransaction.objects.all()
    request_serializer_class = InventoryTransactionRequestSerializer
    response_serializer_class = InventoryTransactionResponseSerializer
    permission_classes = [IsAdminUser]
    ordering_fields = ['created_at']

class StockTransferViewSet(DualSerializerViewSet):
    queryset = StockTransfer.objects.all().prefetch_related('items')
    request_serializer_class = StockTransferRequestSerializer
    response_serializer_class = StockTransferResponseSerializer
    permission_classes = [IsAdminUser]
    ordering_fields = ['created_at', 'status']

class StockTransferItemsViewSet(DualSerializerViewSet):
    queryset = StockTransferItems.objects.all()
    request_serializer_class = StockTransferItemsRequestSerializer
    response_serializer_class = StockTransferItemsResponseSerializer
    permission_classes = [IsAdminUser]
