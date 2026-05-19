from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, LogoutView, TokenRefreshView, MeView,
    MinisterioViewSet, MiembroViewSet, CancionViewSet,
    ProgramaAlabanzaViewSet, LeccionEXPLOViewSet,
    RecursoComunicacionViewSet, IdeaComunicacionViewSet,
    EventoViewSet, UsuarioViewSet, PermisoViewSet
)

router = DefaultRouter()
router.register(r'ministerios', MinisterioViewSet, basename='ministerio')
router.register(r'miembros', MiembroViewSet, basename='miembro')
router.register(r'canciones', CancionViewSet, basename='cancion')
router.register(r'programas', ProgramaAlabanzaViewSet, basename='programa')
router.register(r'lecciones', LeccionEXPLOViewSet, basename='leccion')
router.register(r'recursos', RecursoComunicacionViewSet, basename='recurso')
router.register(r'ideas', IdeaComunicacionViewSet, basename='idea')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'permisos', PermisoViewSet, basename='permiso')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),

    path('', include(router.urls)),
]