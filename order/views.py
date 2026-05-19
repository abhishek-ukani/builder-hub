from rest_framework.permissions import IsAuthenticated
from core.views import DualSerializerViewSet
from order.models import Order, OrderItems, Return, ReturnItem, Delivery
from order.serializers import (
    OrderRequestSerializer, OrderResponseSerializer,
    OrderItemsRequestSerializer, OrderItemsResponseSerializer,
    ReturnRequestSerializer, ReturnResponseSerializer,
    ReturnItemRequestSerializer, ReturnItemResponseSerializer,
    DeliveryRequestSerializer, DeliveryResponseSerializer
)
import uuid

class OrderViewSet(DualSerializerViewSet):
    queryset = Order.objects.all().prefetch_related('items')
    request_serializer_class = OrderRequestSerializer
    response_serializer_class = OrderResponseSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user, order_number=str(uuid.uuid4().hex)[:10].upper())

class OrderItemsViewSet(DualSerializerViewSet):
    queryset = OrderItems.objects.all()
    request_serializer_class = OrderItemsRequestSerializer
    response_serializer_class = OrderItemsResponseSerializer
    permission_classes = [IsAuthenticated]

class ReturnViewSet(DualSerializerViewSet):
    queryset = Return.objects.all().prefetch_related('items')
    request_serializer_class = ReturnRequestSerializer
    response_serializer_class = ReturnResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(order__customer=user)

class ReturnItemViewSet(DualSerializerViewSet):
    queryset = ReturnItem.objects.all()
    request_serializer_class = ReturnItemRequestSerializer
    response_serializer_class = ReturnItemResponseSerializer
    permission_classes = [IsAuthenticated]

class DeliveryViewSet(DualSerializerViewSet):
    queryset = Delivery.objects.all()
    request_serializer_class = DeliveryRequestSerializer
    response_serializer_class = DeliveryResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(order__customer=user)
