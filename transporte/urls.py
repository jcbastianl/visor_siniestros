from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineaBusViewSet

# Router para registrar las rutas automáticamente
router = DefaultRouter()
router.register(r'lineas', LineaBusViewSet, basename='linea-bus')

urlpatterns = [
    path('', include(router.urls)),
]
