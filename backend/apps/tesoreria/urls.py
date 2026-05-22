from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TesoreriaViewSet

router = DefaultRouter()
router.register(r'', TesoreriaViewSet, basename='tesoreria')

urlpatterns = [
    path('', include(router.urls)),
]
