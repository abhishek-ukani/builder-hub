from rest_framework import serializers
from category.models import Category

class CategoryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'image', 'is_active']

    def validate(self, attrs):
        parent = attrs.get('parent')
        if self.instance and parent and self.instance.id == parent.id:
            raise serializers.ValidationError({"parent": "A category cannot be its own parent."})
        return attrs

class CategoryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'slug', 'description', 'image', 'level', 'is_active', 'created_at', 'updated_at']
