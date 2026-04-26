"""
Configuración de URLs para la API REST de transporte.

Rutas registradas automáticamente por ``DefaultRouter``:
    - ``/api/lineas/``     — Líneas de bus (solo lectura)
    - ``/api/ciclovias/``  — Ciclovías (solo lectura)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineaBusViewSet, CicloviaViewSet

router = DefaultRouter()
router.register(r'lineas', LineaBusViewSet, basename='linea-bus')
router.register(r'ciclovias', CicloviaViewSet, basename='ciclovia')

urlpatterns = [
    path('', include(router.urls)),
]
