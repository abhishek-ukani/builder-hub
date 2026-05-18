from django.shortcuts import render
from brand.serializers import BrandSerializer
from rest_framework.viewsets import ModelViewSet
from brand.models import Brand

class Brand(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
     
