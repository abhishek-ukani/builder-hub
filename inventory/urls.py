from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.views import (
    WarehouseViewSet, InventoryViewSet, InventoryTransactionViewSet, 
    StockTransferViewSet, StockTransferItemsViewSet
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')
router.register(r'stock-transfer-items', StockTransferItemsViewSet, basename='stock-transfer-item')

urlpatterns = [
    path('', include(router.urls)),
]
