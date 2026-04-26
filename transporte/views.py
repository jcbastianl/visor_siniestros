"""
ViewSets de la API REST para transporte público y ciclovías.

Expone endpoints de solo lectura (``ReadOnlyModelViewSet``) para:
    - ``/api/lineas/``     — Líneas de bus activas
    - ``/api/ciclovias/``  — Ciclovías activas
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LineaBus, Ciclovia
from .serializers import LineaBusSerializer, CicloviaSerializer


class LineaBusViewSet(ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para líneas de autobús.

    Devuelve únicamente las líneas con ``activo=True``. Incluye la geometría
    GeoJSON de la ruta en el campo ``geom`` para renderizado en el mapa.
    """

    queryset = LineaBus.objects.filter(activo=True)
    serializer_class = LineaBusSerializer


class CicloviaViewSet(ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para ciclovías.

    Devuelve únicamente las ciclovías con ``activo=True``.
    """

    queryset = Ciclovia.objects.filter(activo=True)
    serializer_class = CicloviaSerializer
