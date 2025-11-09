"""
Advanced filters for Siniestro model using django-filter.

Provides filters for:
- Temporal attributes: year, month, week_day, hour
- Severity: grado_severidad
- Relationships: causa_probable, tipo_siniestro
- Text search: via
"""

import django_filters
from django.db.models import Q
from .models import Siniestro, Victima, Causa, TipoSiniestro


WEEK_DAY_CHOICES = [
    (1, 'Sunday'),
    (2, 'Monday'),
    (3, 'Tuesday'),
    (4, 'Wednesday'),
    (5, 'Thursday'),
    (6, 'Friday'),
    (7, 'Saturday'),
]

HOUR_CHOICES = [
    (0, '00:00 - 00:59'),
    (1, '01:00 - 01:59'),
    (2, '02:00 - 02:59'),
    (3, '03:00 - 03:59'),
    (4, '04:00 - 04:59'),
    (5, '05:00 - 05:59'),
    (6, '06:00 - 06:59'),
    (7, '07:00 - 07:59'),
    (8, '08:00 - 08:59'),
    (9, '09:00 - 09:59'),
    (10, '10:00 - 10:59'),
    (11, '11:00 - 11:59'),
    (12, '12:00 - 12:59'),
    (13, '13:00 - 13:59'),
    (14, '14:00 - 14:59'),
    (15, '15:00 - 15:59'),
    (16, '16:00 - 16:59'),
    (17, '17:00 - 17:59'),
    (18, '18:00 - 18:59'),
    (19, '19:00 - 19:59'),
    (20, '20:00 - 20:59'),
    (21, '21:00 - 21:59'),
    (22, '22:00 - 22:59'),
    (23, '23:00 - 23:59'),
]

SEVERITY_CHOICES = [
    ('LEVE', 'Leve'),
    ('MODERADO', 'Moderado'),
    ('GRAVE', 'Grave'),
    ('CRITICO', 'Crítico'),
]

SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]

CONDICION_CHOICES = [
    ('LESIONADO', 'Lesionado'),
    ('FALLECIDO', 'Fallecido'),
    ('ILESO', 'Ileso'),
]

ACTOR_VIAL_CHOICES = [
    ('PEATÓN', 'Peatón'),
    ('CONDUCTOR', 'Conductor'),
    ('PASAJERO', 'Pasajero'),
    ('CICLISTA', 'Ciclista'),
    ('MOTOCICLISTA', 'Motociclista'),
]


class SiniestroFilter(django_filters.FilterSet):
    """
    Advanced FilterSet for Siniestro model.
    
    Supports filtering by:
    - Temporal: year, month, week_day (1=Sun, 7=Sat), hour
    - Severity: grado_severidad
    - Relationships: causa_probable, tipo_siniestro
    - Text: via (case-insensitive)
    """
    
    # Temporal filters
    fecha_hora__year = django_filters.NumberFilter(
        field_name='fecha_hora',
        lookup_expr='year',
        label='Año'
    )
    
    fecha_hora__month = django_filters.NumberFilter(
        field_name='fecha_hora',
        lookup_expr='month',
        label='Mes'
    )
    
    fecha_hora__week_day = django_filters.ChoiceFilter(
        field_name='fecha_hora',
        lookup_expr='week_day',
        choices=WEEK_DAY_CHOICES,
        label='Día de la semana'
    )
    
    fecha_hora__hour = django_filters.ChoiceFilter(
        field_name='fecha_hora',
        lookup_expr='hour',
        choices=HOUR_CHOICES,
        label='Hora'
    )
    
    # Severity filter
    grado_severidad = django_filters.ChoiceFilter(
        choices=SEVERITY_CHOICES,
        label='Grado de severidad'
    )
    
    # Relationship filters
    causa_probable = django_filters.ModelChoiceFilter(
        queryset=Causa.objects.all(),
        label='Causa probable'
    )
    
    tipo_siniestro = django_filters.ModelChoiceFilter(
        queryset=TipoSiniestro.objects.all(),
        label='Tipo de siniestro'
    )
    
    # Text search filter
    via = django_filters.CharFilter(
        field_name='via',
        lookup_expr='icontains',
        label='Vía (contiene)'
    )
    
    # Range filters for flexible querying
    fecha_hora__year_range_min = django_filters.NumberFilter(
        field_name='fecha_hora',
        lookup_expr='year__gte',
        label='Año mínimo'
    )
    
    fecha_hora__year_range_max = django_filters.NumberFilter(
        field_name='fecha_hora',
        lookup_expr='year__lte',
        label='Año máximo'
    )
    
    class Meta:
        model = Siniestro
        fields = [
            'fecha_hora__year',
            'fecha_hora__month',
            'fecha_hora__week_day',
            'fecha_hora__hour',
            'grado_severidad',
            'causa_probable',
            'tipo_siniestro',
            'via',
        ]


class VictimaFilter(django_filters.FilterSet):
    """
    Advanced FilterSet for Victima model.
    
    Supports filtering by:
    - Temporal: year, month, week_day, hour
    - Victim attributes: sexo, condicion, actor_vial
    - Age range: edad_min, edad_max
    """
    
    # Temporal filters (from related siniestro)
    siniestro__fecha_hora__year = django_filters.NumberFilter(
        field_name='siniestro__fecha_hora',
        lookup_expr='year',
        label='Año'
    )
    
    siniestro__fecha_hora__month = django_filters.NumberFilter(
        field_name='siniestro__fecha_hora',
        lookup_expr='month',
        label='Mes'
    )
    
    siniestro__fecha_hora__week_day = django_filters.ChoiceFilter(
        field_name='siniestro__fecha_hora',
        lookup_expr='week_day',
        choices=WEEK_DAY_CHOICES,
        label='Día de la semana'
    )
    
    siniestro__fecha_hora__hour = django_filters.ChoiceFilter(
        field_name='siniestro__fecha_hora',
        lookup_expr='hour',
        choices=HOUR_CHOICES,
        label='Hora'
    )
    
    # Victim attributes
    sexo = django_filters.ChoiceFilter(
        choices=SEXO_CHOICES,
        label='Sexo'
    )
    
    condicion = django_filters.ChoiceFilter(
        choices=CONDICION_CHOICES,
        label='Condición'
    )
    
    actor_vial = django_filters.ChoiceFilter(
        choices=ACTOR_VIAL_CHOICES,
        label='Actor vial'
    )
    
    # Age range filters
    edad = django_filters.NumberFilter(
        field_name='edad',
        label='Edad exacta'
    )
    
    edad_min = django_filters.NumberFilter(
        field_name='edad',
        lookup_expr='gte',
        label='Edad mínima'
    )
    
    edad_max = django_filters.NumberFilter(
        field_name='edad',
        lookup_expr='lte',
        label='Edad máxima'
    )
    
    class Meta:
        model = Victima
        fields = [
            'siniestro__fecha_hora__year',
            'siniestro__fecha_hora__month',
            'siniestro__fecha_hora__week_day',
            'siniestro__fecha_hora__hour',
            'sexo',
            'condicion',
            'actor_vial',
            'edad',
        ]

