from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

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
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

