"""
Serializers para la API REST de transporte público y ciclovías.

Expone todos los campos de los modelos ``LineaBus`` y ``Ciclovia``
incluyendo la geometría GeoJSON para renderizado en mapas del frontend.
"""

from rest_framework import serializers
from .models import LineaBus, Ciclovia


class LineaBusSerializer(serializers.ModelSerializer):
    """
    Serializer para líneas de autobús.

    Expone la información completa de la línea incluyendo la geometría
    de ruta (``geom``, GeoJSON LineString), paradas, tarifas y horarios.
    El frontend consume ``geom.coordinates`` para dibujar la ruta en el mapa.
    """

    class Meta:
        model = LineaBus
        fields = [
            'id', 'nombre', 'color', 'geom', 'activo',
            'fecha_creacion', 'fecha_actualizacion',
            'origen', 'destino', 'descripcion',
            'tarifa_base', 'tarifa_preferencial', 'paradas',
            'horario_inicio', 'horario_fin', 'intervalo_minutos',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class CicloviaSerializer(serializers.ModelSerializer):
    """
    Serializer para ciclovías.

    Expone la información del segmento incluyendo geometría GeoJSON,
    longitud en km y tipo de separación vial.
    """

    class Meta:
        model = Ciclovia
        fields = [
            'id', 'nombre', 'color', 'geom',
            'longitud_km', 'tipo_separacion',
            'activo', 'fecha_creacion', 'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
