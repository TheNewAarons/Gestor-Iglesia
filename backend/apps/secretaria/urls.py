from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.secretaria.views import (
    ActaReunionViewSet,
    SolicitudTramiteViewSet,
    VisitaIglesiaViewSet,
    ComunicadoInternoViewSet,
    HistorialEstadoMiembroViewSet,
    DirectorioViewSet,
    EstadisticasViewSet,
    WhatsAppViewSet,
)

router = DefaultRouter()
router.register(r'actas', ActaReunionViewSet, basename='acta')
router.register(r'solicitudes', SolicitudTramiteViewSet, basename='solicitud')
router.register(r'visitas', VisitaIglesiaViewSet, basename='visita')
router.register(r'comunicados', ComunicadoInternoViewSet, basename='comunicado')
router.register(r'historial', HistorialEstadoMiembroViewSet, basename='historial')
router.register(r'directorio', DirectorioViewSet, basename='directorio')
router.register(r'estadisticas', EstadisticasViewSet, basename='estadisticas')
router.register(r'whatsapp', WhatsAppViewSet, basename='whatsapp')

urlpatterns = [
    path('', include(router.urls)),
]
