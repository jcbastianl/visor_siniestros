from rest_framework import serializers
from .models import LineaBus, Ciclovia


class LineaBusSerializer(serializers.ModelSerializer):
    """Serializer para el modelo LineaBus."""
    
    class Meta:
        model = LineaBus
        fields = ['id', 'nombre', 'color', 'geom', 'activo', 'fecha_creacion', 'fecha_actualizacion', 'origen', 'destino', 'descripcion', 'tarifa_base']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class CicloviaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Ciclovia."""
    
    class Meta:
        model = Ciclovia
        fields = ['id', 'nombre', 'geom', 'longitud_km', 'tipo_separacion', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

