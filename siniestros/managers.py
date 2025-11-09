"""
managers.py - QuerySets y Managers personalizados para lógica de agregación

Centraliza toda la lógica de análisis estadístico para mantener models.py limpio.
"""

from django.db import models
from django.db.models import Count, Case, When, Value, CharField
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
from datetime import datetime


class SiniestroQuerySet(models.QuerySet):
    """QuerySet para Siniestro con métodos de agregación estadística."""

    def _get_year_param(self, year):
        """Helper para obtener año válido."""
        return year or datetime.now().year

    def _fill_monthly_totals(self, queryset):
        """Helper para llenar 12 meses con datos o ceros."""
        monthly_totals = {month: 0 for month in range(1, 13)}
        for item in queryset:
            if item['mes']:
                monthly_totals[item['mes'].month] = item['total']
        return [{'mes': m, 'total': monthly_totals[m]} for m in range(1, 13)]

    def _fill_hourly_totals(self, queryset):
        """Helper para llenar 24 horas con datos o ceros."""
        hourly_totals = {hour: 0 for hour in range(24)}
        for item in queryset:
            if item['hora'] is not None:
                hourly_totals[item['hora']] = item['total']
        return [
            {'rango_hora': f'{h:02d}:00 - {h:02d}:59', 'total': hourly_totals[h]}
            for h in range(24)
        ]

    def get_kpi_stats(self):
        """KPIs: total siniestros, lesionados, fallecidos."""
        from .models import Victima

        return {
            'total_siniestros': self.count(),
            'total_lesionados': Victima.objects.filter(
                condicion=Victima.Condicion.LESIONADO,
                siniestro__in=self
            ).count(),
            'total_fallecidos': Victima.objects.filter(
                condicion=Victima.Condicion.FALLECIDO,
                siniestro__in=self
            ).count(),
        }

    def get_por_mes(self, year=None):
        """Agrupa por mes."""
        year = self._get_year_param(year)
        queryset = (
            self.filter(fecha_hora__year=year)
            .annotate(mes=TruncMonth('fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        return self._fill_monthly_totals(queryset)

    def get_por_severidad(self, year=None):
        """Agrupa por severidad."""
        from .models import Siniestro

        year = self._get_year_param(year)
        labels = dict(Siniestro.Severidad.choices)
        queryset = (
            self.filter(fecha_hora__year=year)
            .values('grado_severidad')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        return [
            {
                'codigo': item['grado_severidad'],
                'label': labels.get(item['grado_severidad'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
        ]

    def get_por_hora(self, year=None):
        """Agrupa por hora del día."""
        year = self._get_year_param(year)
        queryset = (
            self.filter(fecha_hora__year=year)
            .annotate(hora=ExtractHour('fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        return self._fill_hourly_totals(queryset)

    def get_por_dia_hora(self, year=None):
        """Agrupa por día de semana (1-7) y hora (0-23)."""
        year = self._get_year_param(year)
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        for item in (
            self.filter(fecha_hora__year=year)
            .annotate(
                dia_semana=ExtractWeekDay('fecha_hora'),
                hora_dia=ExtractHour('fecha_hora'),
            )
            .values('dia_semana', 'hora_dia')
            .annotate(total=Count('id'))
        ):
            day, hour = item['dia_semana'], item['hora_dia']
            if day in matrix and hour is not None:
                matrix[day][hour] = item['total']

        return [
            {'dia_semana': day, 'hora_dia': hour, 'total': matrix[day][hour]}
            for day in range(1, 8)
            for hour in range(24)
        ]


class SiniestroManager(models.Manager):
    """Manager para Siniestro."""

    def get_queryset(self):
        return SiniestroQuerySet(self.model, using=self._db)

    # Delegated methods for convenience
    def get_kpi_stats(self):
        return self.get_queryset().get_kpi_stats()

    def get_por_mes(self, year=None):
        return self.get_queryset().get_por_mes(year)

    def get_por_severidad(self, year=None):
        return self.get_queryset().get_por_severidad(year)

    def get_por_hora(self, year=None):
        return self.get_queryset().get_por_hora(year)

    def get_por_dia_hora(self, year=None):
        return self.get_queryset().get_por_dia_hora(year)

 
class VictimaQuerySet(models.QuerySet):
    """QuerySet para Victima con métodos de agregación estadística."""

    def _get_year_param(self, year):
        """Helper para obtener año válido."""
        return year or datetime.now().year

    def _fill_monthly_totals(self, queryset):
        """Helper para llenar 12 meses."""
        monthly_totals = {month: 0 for month in range(1, 13)}
        for item in queryset:
            if item['mes']:
                monthly_totals[item['mes'].month] = item['total']
        return [{'mes': m, 'total': monthly_totals[m]} for m in range(1, 13)]

    def _fill_hourly_totals(self, queryset):
        """Helper para llenar 24 horas."""
        hourly_totals = {hour: 0 for hour in range(24)}
        for item in queryset:
            if item['hora'] is not None:
                hourly_totals[item['hora']] = item['total']
        return [
            {'rango_hora': f'{h:02d}:00 - {h:02d}:59', 'total': hourly_totals[h]}
            for h in range(24)
        ]

    def get_por_sexo(self, year=None):
        """Agrupa por sexo."""
        from .models import Victima

        year = self._get_year_param(year)
        labels = dict(Victima.Sexo.choices)
        queryset = (
            self.filter(siniestro__fecha_hora__year=year)
            .values('sexo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        return [
            {
                'sexo': item['sexo'],
                'label': labels.get(item['sexo'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
            if item['sexo'] is not None
        ]

    def get_por_actor_vial(self, year=None):
        """Agrupa por actor vial."""
        from .models import Victima

        year = self._get_year_param(year)
        labels = dict(Victima.ActorVial.choices)
        queryset = (
            self.filter(siniestro__fecha_hora__year=year)
            .values('actor_vial')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        return [
            {
                'actor_vial': item['actor_vial'],
                'label': labels.get(item['actor_vial'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
            if item['actor_vial'] is not None
        ]

    def get_por_edad_sexo(self, year=None):
        """Agrupa por rango de edad y sexo."""
        from .models import Victima

        year = self._get_year_param(year)
        ranges = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 120)]
        sexo_labels = dict(Victima.Sexo.choices)

        result = []
        for start, end in ranges:
            queryset = self.filter(siniestro__fecha_hora__year=year, edad__gte=start, edad__lte=end)
            hombre = queryset.filter(sexo=Victima.Sexo.HOMBRE).count()
            mujer = queryset.filter(sexo=Victima.Sexo.MUJER).count()
            
            # Formato: rango_edad, sexo, sexo_label, total (para cada sexo en el rango)
            result.append({
                'rango_edad': f'{start}-{end}',
                'sexo': Victima.Sexo.HOMBRE,
                'sexo_label': sexo_labels.get(Victima.Sexo.HOMBRE, 'No definido'),
                'total': hombre,
            })
            result.append({
                'rango_edad': f'{start}-{end}',
                'sexo': Victima.Sexo.MUJER,
                'sexo_label': sexo_labels.get(Victima.Sexo.MUJER, 'No definido'),
                'total': mujer,
            })
        return result

    def get_por_mes(self, year=None):
        """Agrupa por mes."""
        year = self._get_year_param(year)
        queryset = (
            self.filter(siniestro__fecha_hora__year=year)
            .annotate(mes=TruncMonth('siniestro__fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        return self._fill_monthly_totals(queryset)

    def get_por_hora(self, year=None):
        """Agrupa por hora del día."""
        year = self._get_year_param(year)
        queryset = (
            self.filter(siniestro__fecha_hora__year=year)
            .annotate(hora=ExtractHour('siniestro__fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        return self._fill_hourly_totals(queryset)

    def get_por_dia_hora(self, year=None):
        """Agrupa por día de semana y hora."""
        year = self._get_year_param(year)
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        for item in (
            self.filter(siniestro__fecha_hora__year=year)
            .annotate(
                dia_semana=ExtractWeekDay('siniestro__fecha_hora'),
                hora_dia=ExtractHour('siniestro__fecha_hora'),
            )
            .values('dia_semana', 'hora_dia')
            .annotate(total=Count('id'))
        ):
            day, hour = item['dia_semana'], item['hora_dia']
            if day in matrix and hour is not None:
                matrix[day][hour] = item['total']

        return [
            {'dia_semana': day, 'hora_dia': hour, 'total': matrix[day][hour]}
            for day in range(1, 8)
            for hour in range(24)
        ]


class VictimaManager(models.Manager):
    """Manager para Victima."""

    def get_queryset(self):
        return VictimaQuerySet(self.model, using=self._db)

    # Delegated methods for convenience
    def get_por_sexo(self, year=None):
        return self.get_queryset().get_por_sexo(year)

    def get_por_actor_vial(self, year=None):
        return self.get_queryset().get_por_actor_vial(year)

    def get_por_edad_sexo(self, year=None):
        return self.get_queryset().get_por_edad_sexo(year)

    def get_por_mes(self, year=None):
        return self.get_queryset().get_por_mes(year)

    def get_por_hora(self, year=None):
        return self.get_queryset().get_por_hora(year)

    def get_por_dia_hora(self, year=None):
        return self.get_queryset().get_por_dia_hora(year)
