"""
Configuración de URLs para la API REST de siniestros.

Rutas registradas automáticamente por ``DefaultRouter``:
    - ``/api/siniestros/``         — CRUD y estadísticas de siniestros
    - ``/api/victimas/``           — CRUD y estadísticas de víctimas
    - ``/api/causas/``             — Catálogo de causas probables
    - ``/api/tipos-siniestro/``    — Catálogo de tipos de siniestro
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiniestroViewSet, VictimaViewSet, CausaViewSet, TipoSiniestroViewSet

router = DefaultRouter()
router.register(r'siniestros', SiniestroViewSet, basename='siniestro')
router.register(r'victimas', VictimaViewSet, basename='victima')
router.register(r'causas', CausaViewSet, basename='causa')
router.register(r'tipos-siniestro', TipoSiniestroViewSet, basename='tipo-siniestro')

urlpatterns = [
    path('', include(router.urls)),
]
