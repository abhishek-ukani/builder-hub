from datetime import timezone, datetime

from rest_framework.permissions import IsAuthenticated
from core.views import DualSerializerViewSet
from order.models import Order, OrderItems, Return, ReturnItem, Delivery, OrderItemThaliOption
from order.serializers import (
    OrderRequestSerializer, OrderResponseSerializer,
    ReturnRequestSerializer, ReturnResponseSerializer,
    ReturnItemRequestSerializer, ReturnItemResponseSerializer,
    DeliveryRequestSerializer, DeliveryResponseSerializer
)
import uuid
from django.db import transaction
from decimal import Decimal
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from order.services.order_service import generate_order_number

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

    def create(self, request, *args, **kwargs):
        city_prefix = request.data.get('city')[:2].upper()
        serializer = self.request_serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data.pop('items', [])

        with transaction.atomic():
            order = serializer.save(customer=request.user, order_number=generate_order_number(city_prefix, datetime.now(timezone.utc)))

            subtotal = Decimal('0.00')
            for item in items_data:
                variant = item.get('variant')
                thali = item.get('thali')
                thali_options = item.get('thali_options', [])
                quantity = item.get('quantity')

                if thali:
                    base_price = Decimal(thali.price)
                    options_charge = sum(Decimal(opt.extra_charge) for opt in thali_options)
                    unit_price = base_price + options_charge
                else:
                    unit_price = Decimal(variant.price)

                total_price = Decimal(unit_price) * Decimal(quantity)

                order_item = OrderItems.objects.create(
                    order=order,
                    variant=variant,
                    thali=thali,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )

                if thali:
                    for opt in thali_options:
                        OrderItemThaliOption.objects.create(
                            order_item=order_item,
                            option=opt
                        )

                subtotal += total_price

            # update order totals (tax, shipping, discount may be set from request)
            order.subtotal = subtotal
            order.save()

        resp_serializer = self.response_serializer_class(order, context={'request': request})
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('You do not have permission to update orders.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('You do not have permission to update orders.')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('You do not have permission to delete orders.')
        return super().destroy(request, *args, **kwargs)



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
