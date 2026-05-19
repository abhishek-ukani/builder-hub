from rest_framework import serializers
from order.models import Order, OrderItems, Return, ReturnItem, Delivery

class OrderItemsRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        exclude = ['created_at', 'updated_at', 'id']

class OrderItemsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'

class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['order_number', 'customer', 'created_at', 'updated_at', 'id']

class OrderResponseSerializer(serializers.ModelSerializer):
    items = OrderItemsResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class ReturnItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        exclude = ['created_at', 'updated_at', 'id']

class ReturnItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = '__all__'

class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        exclude = ['created_at', 'updated_at', 'id']

class ReturnResponseSerializer(serializers.ModelSerializer):
    items = ReturnItemResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Return
        fields = '__all__'

class DeliveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        exclude = ['created_at', 'updated_at', 'id']

class DeliveryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'
