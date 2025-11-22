from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LineaBus
from .serializers import LineaBusSerializer


class LineaBusViewSet(ReadOnlyModelViewSet):
    """ViewSet read-only para gestionar líneas de autobús."""
    queryset = LineaBus.objects.filter(activo=True)
    serializer_class = LineaBusSerializer
