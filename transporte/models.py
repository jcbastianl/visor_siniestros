"""
Modelos de datos para la app de transporte público y ciclovías.

Incluye:
    - ``LineaBus``: Líneas de autobús con geometría de ruta, paradas y tarifas.
    - ``Ciclovia``: Segmentos de ciclovía con tipo de separación y longitud.
"""

from django.db import models


class LineaBus(models.Model):
    """Modelo para gestionar líneas de autobús con coordenadas de ruta."""
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre de la línea (ej. L10)")
    color = models.CharField(max_length=7, help_text="Color en formato hexadecimal (ej. #FF0000)")
    geom = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Datos de geometria GeoJSON de la ruta de la linea de bus (LineString)."
    )
    origen = models.CharField(max_length=100, default="", help_text="Punto de inicio o terminal de la línea.")
    destino = models.CharField(max_length=100, default="", help_text="Punto final o terminal de la línea.")
    descripcion = models.TextField(blank=True, null=True, help_text="Detalles o información adicional sobre la ruta.")
    tarifa_base = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Tarifa base del pasaje.")
    tarifa_preferencial = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Tarifa preferencial/reducida (tercera edad, discapacidad, etc.).")
    paradas = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Lista de paradas en formato [[lng, lat, 'nombre opcional'], ...]"
    )
    horario_inicio = models.TimeField(null=True, blank=True, help_text="Hora de inicio del servicio (ej. 06:00:00)")
    horario_fin = models.TimeField(null=True, blank=True, help_text="Hora de fin del servicio (ej. 22:30:00)")
    intervalo_minutos = models.IntegerField(default=0, help_text="Frecuencia/Intervalo de paso en minutos")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Línea de Bus"
        verbose_name_plural = "Líneas de Bus"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Ciclovia(models.Model):
    """
    Segmento de ciclovía de la ciudad.

    Almacena la geometría de la ruta (GeoJSON LineString), longitud en km
    y tipo de separación respecto al tránsito vehicular.
    """

    TIPO_SEPARACION_CHOICES = [
        ('Pintada', 'Ciclovía Pintada'),
        ('Confinada', 'Ciclovía Confinada'),
        ('Mixta', 'Ciclovía Mixta'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la ciclovía o segmento"
    )
    color = models.CharField(
        max_length=7,
        default="#008000",
        help_text="Color en formato hexadecimal (ej. #008000)"
    )
    geom = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Geometria GeoJSON LineString de la ruta. Formato [lng, lat]"
    )
    longitud_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Longitud total en kilómetros"
    )
    tipo_separacion = models.CharField(
        max_length=50,
        choices=TIPO_SEPARACION_CHOICES,
        default='Pintada',
        help_text="Tipo de separación: 'Pintada', 'Confinada', 'Mixta'"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ciclovía"
        verbose_name_plural = "Ciclovías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

