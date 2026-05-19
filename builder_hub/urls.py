from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('auth/', include('auth.urls')),
    path('brand/', include('brand.urls')),
    path('category/', include('category.urls')),
    path('product/', include('product.urls')),
    path('user/', include('user.urls')),
    path('supplier/', include('supplier.urls')),
    path('inventory/', include('inventory.urls')),
    path('order/', include('order.urls')),
]
