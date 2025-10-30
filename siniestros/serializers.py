# Este es el código para: siniestros/views.py

from rest_framework import viewsets
from .models import Siniestro, Causa, TipoSiniestro
# ¡Importamos los serializers que acabamos de crear!
from .serializers import SiniestroSerializer, CausaSerializer, TipoSiniestroSerializer

# --- 1. Vista para los Siniestros (Para el Mapa y la lista) ---

class SiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este ViewSet provee automáticamente las acciones `list` (listar todos)
    y `retrieve` (ver uno solo por ID) para los siniestros.
    """
    queryset = Siniestro.objects.all()
    serializer_class = SiniestroSerializer


# --- 2. Vistas para los Filtros (Para los <select> del frontend) ---

class CausaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Un ViewSet para listar solo las causas que están MARCADAS COMO ACTIVAS.
    """
    serializer_class = CausaSerializer
    
    # Usamos una función para filtrar solo las activas
    def get_queryset(self):
        return Causa.objects.filter(activo=True)


class TipoSiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Un ViewSet para listar solo los Tipos de Siniestro ACTIVOS.
    """
    serializer_class = TipoSiniestroSerializer
    
    # Usamos una función para filtrar solo las activas
    def get_queryset(self):
        return TipoSiniestro.objects.filter(activo=True)