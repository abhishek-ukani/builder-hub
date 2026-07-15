from rest_framework import serializers
from order.models import Order, OrderItems, Return, ReturnItem, Delivery, OrderItemThaliOption
from product.models import Thali, ThaliComponentOption

class OrderItemsRequestSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    thali_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ThaliComponentOption.objects.all(),
        required=False,
        default=list
    )

    class Meta:
        model = OrderItems
        exclude = ['created_at', 'updated_at', 'id', 'order']

    def validate(self, attrs):
        variant = attrs.get('variant')
        thali = attrs.get('thali')
        thali_options = attrs.get('thali_options', [])

        # 1. Verify either variant or thali is provided, but not both or neither
        if not variant and not thali:
            raise serializers.ValidationError("Each order item must specify either a variant or a thali.")
        if variant and thali:
            raise serializers.ValidationError("An order item cannot specify both a variant and a thali.")

        # 2. If it is a variant, thali_options should not be provided
        if variant and thali_options:
            raise serializers.ValidationError("Thali options can only be specified when ordering a thali.")

        # 3. If it is a Thali, validate the selections
        if thali:
            # All selected options must belong to this Thali's component groups
            valid_option_ids = set(
                ThaliComponentOption.objects.filter(
                    group__thali=thali
                ).values_list('id', flat=True)
            )
            for opt in thali_options:
                if opt.id not in valid_option_ids:
                    raise serializers.ValidationError(
                        f"Option {opt} is not a valid option for Thali {thali.name}."
                    )

            # Check min/max selections per group
            groups = thali.component_groups.all()
            for group in groups:
                selected_count = sum(1 for opt in thali_options if opt.group_id == group.id)

                if group.is_required or group.min_selections > 0:
                    if selected_count < group.min_selections:
                        raise serializers.ValidationError(
                            f"Group '{group.name}' requires at least {group.min_selections} selections, but only {selected_count} were selected."
                        )
                if selected_count > group.max_selections:
                    raise serializers.ValidationError(
                        f"Group '{group.name}' allows at most {group.max_selections} selections, but {selected_count} were selected."
                    )

        return attrs

class OrderItemThaliOptionResponseSerializer(serializers.ModelSerializer):
    component_group = serializers.CharField(source="option.group.name", read_only=True)
    option_name = serializers.CharField(source="option.product_variant.product.title", read_only=True)
    variant_sku = serializers.CharField(source="option.product_variant.sku", read_only=True)
    extra_charge = serializers.DecimalField(source="option.extra_charge", max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItemThaliOption
        fields = ["id", "component_group", "option", "option_name", "variant_sku", "extra_charge"]

class OrderItemsResponseSerializer(serializers.ModelSerializer):
    thali_options = OrderItemThaliOptionResponseSerializer(many=True, read_only=True)
    thali_name = serializers.CharField(source="thali.name", read_only=True)
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)

    class Meta:
        model = OrderItems
        fields = [
            "id",
            "order",
            "variant",
            "variant_sku",
            "product_title",
            "thali",
            "thali_name",
            "thali_options",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        ]

class OrderRequestSerializer(serializers.ModelSerializer):
    items = OrderItemsRequestSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = Order
        exclude = ['order_number', 'customer', 'created_at', 'updated_at', 'id']

    def validate_items(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Order must include at least one item.")
        return value

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
