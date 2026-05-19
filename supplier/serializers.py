from rest_framework import serializers
from supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem

class SupplierRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        exclude = ['created_at', 'updated_at', 'id']

class SupplierResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseOrderItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['created_at', 'updated_at', 'id']
        
    def validate(self, attrs):
        ordered_quantity = attrs.get('ordered_quantity')
        received_quantity = attrs.get('received_quantity')
        
        if self.instance:
            ordered_quantity = ordered_quantity if ordered_quantity is not None else self.instance.ordered_quantity
            received_quantity = received_quantity if received_quantity is not None else self.instance.received_quantity
            
        if received_quantity is not None and ordered_quantity is not None and received_quantity > ordered_quantity:
            raise serializers.ValidationError({"received_quantity": "Received quantity cannot exceed ordered quantity."})
        return attrs

class PurchaseOrderItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

class PurchaseOrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        exclude = ['ordered_at', 'created_at', 'updated_at', 'id']

class PurchaseOrderResponseSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
