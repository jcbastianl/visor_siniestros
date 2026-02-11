"""
Filtros avanzados para Siniestro y Víctima usando django-filter.

Soporta filtrado por: atributos temporales (año, mes, día, hora),
severidad, relaciones (causa, tipo), texto (vía, barrio, parroquia),
condiciones del evento y rango de vehículos.
"""

import django_filters
from .models import Siniestro, Victima, Causa, TipoSiniestro


WEEK_DAY_CHOICES = [
    (1, 'Domingo'), (2, 'Lunes'), (3, 'Martes'), (4, 'Miércoles'),
    (5, 'Jueves'), (6, 'Viernes'), (7, 'Sábado'),
]

HOUR_CHOICES = [(h, f'{h:02d}:00 - {h:02d}:59') for h in range(24)]

SEVERITY_CHOICES = [
    ('SOLO_DANOS', 'Solo con daños materiales'),
    ('CON_LESIONADOS', 'Con lesionados'),
    ('CON_FALLECIDOS', 'Con fallecidos en sitio'),
]

SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
CONDICION_CHOICES = [('LESIONADO', 'Lesionado'), ('FALLECIDO', 'Fallecido'), ('ILESO', 'Ileso')]
ACTOR_VIAL_CHOICES = [
    ('PEATÓN', 'Peatón'), ('CONDUCTOR', 'Conductor'), ('PASAJERO', 'Pasajero'),
    ('CICLISTA', 'Ciclista'), ('MOTOCICLISTA', 'Motociclista'),
]


class SiniestroFilter(django_filters.FilterSet):
    """Filtros para Siniestro: temporales, severidad, relaciones, ubicación y condiciones."""

    # Temporales
    fecha_hora__year = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='year', label='Año')
    fecha_hora__month = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='month', label='Mes')
    fecha_hora__week_day = django_filters.ChoiceFilter(field_name='fecha_hora', lookup_expr='week_day', choices=WEEK_DAY_CHOICES, label='Día de la semana')
    fecha_hora__hour = django_filters.ChoiceFilter(field_name='fecha_hora', lookup_expr='hour', choices=HOUR_CHOICES, label='Hora')

    # Severidad
    grado_severidad = django_filters.ChoiceFilter(choices=SEVERITY_CHOICES, label='Grado de severidad')

    # Relaciones
    causa_probable = django_filters.ModelChoiceFilter(queryset=Causa.objects.all(), label='Causa probable')
    tipo_siniestro = django_filters.ModelChoiceFilter(queryset=TipoSiniestro.objects.all(), label='Tipo de siniestro')

    # Texto
    via = django_filters.CharFilter(field_name='via', lookup_expr='icontains', label='Vía (contiene)')
    zona = django_filters.CharFilter(field_name='zona', lookup_expr='icontains', label='Zona')
    barrio = django_filters.CharFilter(field_name='barrio', lookup_expr='icontains', label='Barrio')
    parroquia = django_filters.CharFilter(field_name='parroquia', lookup_expr='icontains', label='Parroquia')

    # Condiciones
    condicion_calzada = django_filters.CharFilter(field_name='condicion_calzada', lookup_expr='iexact', label='Condición de calzada')
    condicion_atmosferica = django_filters.CharFilter(field_name='condicion_atmosferica', lookup_expr='iexact', label='Condición atmosférica')
    luz_artificial = django_filters.CharFilter(field_name='luz_artificial', lookup_expr='iexact', label='Luz artificial')

    # Vehículos
    num_vehiculos_min = django_filters.NumberFilter(field_name='num_vehiculos_involucrados', lookup_expr='gte', label='Mín. vehículos')
    num_vehiculos_max = django_filters.NumberFilter(field_name='num_vehiculos_involucrados', lookup_expr='lte', label='Máx. vehículos')
    tiene_danos_bien_publico = django_filters.BooleanFilter(field_name='tiene_danos_bien_publico', label='Daños al bien público')

    # Rango de años
    fecha_hora__year_range_min = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='year__gte', label='Año mínimo')
    fecha_hora__year_range_max = django_filters.NumberFilter(field_name='fecha_hora', lookup_expr='year__lte', label='Año máximo')

    class Meta:
        model = Siniestro
        fields = [
            'fecha_hora__year', 'fecha_hora__month', 'fecha_hora__week_day', 'fecha_hora__hour',
            'grado_severidad', 'causa_probable', 'tipo_siniestro', 'via',
            'zona', 'barrio', 'parroquia',
            'condicion_calzada', 'condicion_atmosferica', 'luz_artificial',
            'num_vehiculos_involucrados', 'tiene_danos_bien_publico',
        ]


class VictimaFilter(django_filters.FilterSet):
    """Filtros para Víctima: temporales (del siniestro), atributos y rango de edad."""

    # Temporales (desde el siniestro relacionado)
    siniestro__fecha_hora__year = django_filters.NumberFilter(field_name='siniestro__fecha_hora', lookup_expr='year', label='Año')
    siniestro__fecha_hora__month = django_filters.NumberFilter(field_name='siniestro__fecha_hora', lookup_expr='month', label='Mes')
    siniestro__fecha_hora__week_day = django_filters.ChoiceFilter(field_name='siniestro__fecha_hora', lookup_expr='week_day', choices=WEEK_DAY_CHOICES, label='Día de la semana')
    siniestro__fecha_hora__hour = django_filters.ChoiceFilter(field_name='siniestro__fecha_hora', lookup_expr='hour', choices=HOUR_CHOICES, label='Hora')

    # Atributos de la víctima
    sexo = django_filters.ChoiceFilter(choices=SEXO_CHOICES, label='Sexo')
    condicion = django_filters.ChoiceFilter(choices=CONDICION_CHOICES, label='Condición')
    actor_vial = django_filters.ChoiceFilter(choices=ACTOR_VIAL_CHOICES, label='Actor vial')

    # Rango de edad
    edad = django_filters.NumberFilter(field_name='edad', label='Edad exacta')
    edad_min = django_filters.NumberFilter(field_name='edad', lookup_expr='gte', label='Edad mínima')
    edad_max = django_filters.NumberFilter(field_name='edad', lookup_expr='lte', label='Edad máxima')

    class Meta:
        model = Victima
        fields = [
            'siniestro__fecha_hora__year', 'siniestro__fecha_hora__month',
            'siniestro__fecha_hora__week_day', 'siniestro__fecha_hora__hour',
            'sexo', 'condicion', 'actor_vial', 'edad',
        ]
