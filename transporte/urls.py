from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineaBusViewSet, CicloviaViewSet

# Router para registrar las rutas automáticamente
router = DefaultRouter()
router.register(r'lineas', LineaBusViewSet, basename='linea-bus')
router.register(r'ciclovias', CicloviaViewSet, basename='ciclovia')

urlpatterns = [
    path('', include(router.urls)),
]

