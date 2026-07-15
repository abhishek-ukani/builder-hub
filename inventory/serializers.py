from rest_framework import serializers
from inventory.models import Warehouse, Inventory, InventoryTransaction, StockTransfer, StockTransferItems

class WarehouseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        exclude = ['created_at', 'updated_at', 'id']

    def validate(self, attrs):
        lat = attrs.get('latitude')
        lon = attrs.get('longitude')
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if lon is not None and (lon < -180 or lon > 180):
            raise serializers.ValidationError({"longitude": "Longitude must be between -180 and 180."})
        return attrs

class WarehouseResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class InventoryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        exclude = ['created_at', 'updated_at', 'id']

    def validate(self, attrs):
        avail = attrs.get('available_quantity')
        res = attrs.get('reserved_quantity')
        dam = attrs.get('damaged_quantity')
        inc = attrs.get('incoming_quantity')

        if self.instance:
            avail = avail if avail is not None else self.instance.available_quantity
            res = res if res is not None else self.instance.reserved_quantity
            dam = dam if dam is not None else self.instance.damaged_quantity
            inc = inc if inc is not None else self.instance.incoming_quantity

        if any(q is not None and q < 0 for q in [avail, res, dam, inc]):
            raise serializers.ValidationError("Quantities cannot be negative.")
        return attrs

class InventoryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class InventoryTransactionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        exclude = ['created_at', 'updated_at', 'id']

class InventoryTransactionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'

class StockTransferItemsRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItems
        exclude = ['created_at', 'updated_at', 'id']

class StockTransferItemsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItems
        fields = '__all__'

class StockTransferRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransfer
        exclude = ['created_at', 'updated_at', 'id']

    def validate(self, attrs):
        from_warehouse = attrs.get('from_warehouse')
        to_warehouse = attrs.get('to_warehouse')

        if self.instance:
            from_warehouse = from_warehouse if from_warehouse is not None else self.instance.from_warehouse
            to_warehouse = to_warehouse if to_warehouse is not None else self.instance.to_warehouse

        if from_warehouse and to_warehouse and from_warehouse == to_warehouse:
            raise serializers.ValidationError("Source and destination warehouse cannot be the same.")
        return attrs

class StockTransferResponseSerializer(serializers.ModelSerializer):
    items = StockTransferItemsResponseSerializer(many=True, read_only=True)

    class Meta:
        model = StockTransfer
        fields = '__all__'
