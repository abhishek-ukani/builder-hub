from rest_framework import serializers
from product.models import (
    Product, Thali, ProductVariant, ProductMedia,
    Attribute, AttributeValue, VariantAttributeValue
)

class AttributeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'

class AttributeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'

class AttributeValueRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'

class AttributeValueResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'

class VariantAttributeValueRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantAttributeValue
        fields = '__all__'

class VariantAttributeValueResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantAttributeValue
        fields = '__all__'

class ProductMediaRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = '__all__'

class ProductMediaResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = '__all__'

class ProductVariantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

    def validate(self, attrs):
        price = attrs.get('price')
        compare_price = attrs.get('compare_price')
        
        if self.instance:
            price = price if price is not None else self.instance.price
            compare_price = compare_price if 'compare_price' in attrs else self.instance.compare_price

        if compare_price is not None and compare_price < price:
            raise serializers.ValidationError({"compare_price": "Compare price must be greater than or equal to price."})
            
        return attrs

class ProductVariantResponseSerializer(serializers.ModelSerializer):
    images = ProductMediaResponseSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['slug', 'created_at', 'updated_at', 'id']

class ProductResponseSerializer(serializers.ModelSerializer):
    variants = ProductVariantResponseSerializer(many=True, read_only=True)
    images = ProductMediaResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ThaliRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thali
        fields = '__all__'

class ThaliResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thali
        fields = '__all__'