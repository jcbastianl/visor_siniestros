from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LineaBus, Ciclovia
from .serializers import LineaBusSerializer, CicloviaSerializer


class LineaBusViewSet(ReadOnlyModelViewSet):
    """ViewSet read-only para gestionar líneas de autobús."""
    queryset = LineaBus.objects.filter(activo=True)
    serializer_class = LineaBusSerializer


class CicloviaViewSet(ReadOnlyModelViewSet):
    """ViewSet read-only para gestionar ciclovías."""
    queryset = Ciclovia.objects.filter(activo=True)
    serializer_class = CicloviaSerializer

