from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from django.conf import settings
from django.conf.urls.static import static

from api.views import PaymeCallBackAPIView

from .docs import ProtectedSpectacularSwaggerView, ProtectedSpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Search
    path('api/search/', include('api.search.urls')),

    # Payme callback
    path('payme/callback', PaymeCallBackAPIView.as_view()),

    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger / Redoc
    path('api/schema/swagger/', ProtectedSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', ProtectedSpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
