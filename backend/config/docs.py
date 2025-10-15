from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView


@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
class ProtectedSpectacularSwaggerView(SpectacularSwaggerView):
    """Защищённый доступ к Swagger UI"""
    pass


@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
class ProtectedSpectacularRedocView(SpectacularRedocView):
    """Защищённый доступ к Redoc UI"""
    pass
