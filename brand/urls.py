from django.urls import path, include
from brand.views import Brand
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("brand",Brand,basename='brand')
urlpatterns = [
path("",include(router.urls))
]