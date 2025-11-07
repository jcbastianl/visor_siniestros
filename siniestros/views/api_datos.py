from rest_framework import viewsets

from ..models import Siniestro, Causa, TipoSiniestro
from ..serializers import SiniestroSerializer, CausaSerializer, TipoSiniestroSerializer


class SiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose siniestros for public API consumption."""
    queryset = Siniestro.objects.all()
    serializer_class = SiniestroSerializer


class CausaViewSet(viewsets.ReadOnlyModelViewSet):
    """List only active causas for filter dropdowns."""
    serializer_class = CausaSerializer

    def get_queryset(self):
        return Causa.objects.filter(activo=True)


class TipoSiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """List only active tipos de siniestro for filters."""
    serializer_class = TipoSiniestroSerializer

    def get_queryset(self):
        return TipoSiniestro.objects.filter(activo=True)
