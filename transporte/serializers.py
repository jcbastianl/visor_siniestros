from rest_framework import serializers
from .models import LineaBus


class LineaBusSerializer(serializers.ModelSerializer):
    """Serializer para el modelo LineaBus."""
    
    class Meta:
        model = LineaBus
        fields = ['id', 'nombre', 'color', 'coordenadas', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
