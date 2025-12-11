"""
managers.py - QuerySets y Managers personalizados para lógica de agregación

Centraliza toda la lógica de análisis estadístico para mantener models.py limpio.
"""

from django.db import models
from django.db.models import Count, Case, When, Value, CharField
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay, TruncYear
from datetime import datetime


class SiniestroQuerySet(models.QuerySet):
    """QuerySet para Siniestro con métodos de agregación estadística."""

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

    def get_por_mes(self):
        """Agrupa por mes (respeta el queryset filtrado de la vista)."""
        queryset = (
            self
            .annotate(mes=TruncMonth('fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        return self._fill_monthly_totals(queryset)

    def get_por_severidad(self):
        """Agrupa por severidad (ya filtrado por el queryset)."""
        from .models import Siniestro

        labels = dict(Siniestro.Severidad.choices)
        queryset = (
            self
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

    def get_por_hora(self):
        """Agrupa por hora del día (respeta el queryset filtrado de la vista)."""
        queryset = (
            self
            .annotate(hora=ExtractHour('fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        return self._fill_hourly_totals(queryset)

    def get_por_dia_hora(self):
        """Agrupa por día de semana (1-7) y hora (0-23) (respeta el queryset filtrado)."""
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        for item in (
            self
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

    def get_por_via(self):
        """Agrupa por vía con conteo de siniestros, lesionados y fallecidos (ya filtrado)."""
        from .models import Victima
        
        queryset = (
            self
            .values('via')
            .annotate(total_siniestros=Count('id'))
            .order_by('-total_siniestros')[:20]  # Top 20 vías
        )
        
        result = []
        for item in queryset:
            via = item['via']
            siniestros_en_via = self.filter(via=via)
            lesionados = Victima.objects.filter(
                condicion=Victima.Condicion.LESIONADO,
                siniestro__in=siniestros_en_via
            ).count()
            fallecidos = Victima.objects.filter(
                condicion=Victima.Condicion.FALLECIDO,
                siniestro__in=siniestros_en_via
            ).count()
            
            result.append({
                'via': via or 'Sin especificar',
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': lesionados,
                'total_fallecidos': fallecidos,
            })
        
        return result

    def get_por_causa_probable(self):
        """Agrupa por causa probable con totales (ya filtrado)."""
        from .models import Victima
        
        queryset = (
            self
            .values('causa_probable__nombre', 'causa_probable__id')
            .annotate(total_siniestros=Count('id'))
            .order_by('-total_siniestros')
        )
        
        result = []
        for item in queryset:
            causa_nombre = item['causa_probable__nombre'] or 'Sin especificar'
            siniestros_causa = self.filter(
                causa_probable__nombre=item['causa_probable__nombre']
            )
            lesionados = Victima.objects.filter(
                condicion=Victima.Condicion.LESIONADO,
                siniestro__in=siniestros_causa
            ).count()
            fallecidos = Victima.objects.filter(
                condicion=Victima.Condicion.FALLECIDO,
                siniestro__in=siniestros_causa
            ).count()
            
            result.append({
                'id': item['causa_probable__id'],
                'causa': causa_nombre,
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': lesionados,
                'total_fallecidos': fallecidos,
            })
        
        return result

    def get_por_tipo_siniestro(self):
        """Agrupa por tipo de siniestro con totales (ya filtrado)."""
        from .models import Victima
        
        queryset = (
            self
            .values('tipo_siniestro__nombre', 'tipo_siniestro__id')
            .annotate(total_siniestros=Count('id'))
            .order_by('-total_siniestros')
        )
        
        result = []
        for item in queryset:
            tipo_nombre = item['tipo_siniestro__nombre'] or 'Sin especificar'
            siniestros_tipo = self.filter(
                tipo_siniestro__nombre=item['tipo_siniestro__nombre']
            )
            lesionados = Victima.objects.filter(
                condicion=Victima.Condicion.LESIONADO,
                siniestro__in=siniestros_tipo
            ).count()
            fallecidos = Victima.objects.filter(
                condicion=Victima.Condicion.FALLECIDO,
                siniestro__in=siniestros_tipo
            ).count()
            
            result.append({
                'id': item['tipo_siniestro__id'],
                'tipo': tipo_nombre,
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': lesionados,
                'total_fallecidos': fallecidos,
            })
        
        return result

    def get_evolucion_anual(self):
        """Evolución anual de siniestros, lesionados y fallecidos."""
        from .models import Victima
        
        years_data = (
            self
            .annotate(ano=TruncYear('fecha_hora'))
            .values('ano')
            .annotate(total_siniestros=Count('id'))
            .order_by('ano')
        )
        
        result = []
        for item in years_data:
            if not item['ano']:
                continue
            
            year = item['ano'].year
            siniestros_year = self.filter(fecha_hora__year=year)
            lesionados = Victima.objects.filter(
                condicion=Victima.Condicion.LESIONADO,
                siniestro__in=siniestros_year
            ).count()
            fallecidos = Victima.objects.filter(
                condicion=Victima.Condicion.FALLECIDO,
                siniestro__in=siniestros_year
            ).count()
            
            result.append({
                'ano': year,
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': lesionados,
                'total_fallecidos': fallecidos,
            })
        
        return result


class SiniestroManager(models.Manager):
    """Manager para Siniestro."""

    def get_queryset(self):
        return SiniestroQuerySet(self.model, using=self._db)

    # Delegated methods for convenience
    def get_kpi_stats(self):
        return self.get_queryset().get_kpi_stats()

    def get_por_mes(self):
        return self.get_queryset().get_por_mes()

    def get_por_severidad(self):
        return self.get_queryset().get_por_severidad()

    def get_por_hora(self):
        return self.get_queryset().get_por_hora()

    def get_por_dia_hora(self):
        return self.get_queryset().get_por_dia_hora()

    def get_por_via(self):
        return self.get_queryset().get_por_via()

    def get_por_causa_probable(self):
        return self.get_queryset().get_por_causa_probable()

    def get_por_tipo_siniestro(self):
        return self.get_queryset().get_por_tipo_siniestro()

    def get_evolucion_anual(self):
        return self.get_queryset().get_evolucion_anual()

 
class VictimaQuerySet(models.QuerySet):
    """QuerySet para Victima con métodos de agregación estadística."""

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

    def get_por_sexo(self):
        """Agrupa por sexo (ya filtrado por el queryset)."""
        from .models import Victima

        labels = dict(Victima.Sexo.choices)
        queryset = (
            self
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

    def get_por_actor_vial(self):
        """Agrupa por actor vial (ya filtrado por el queryset)."""
        from .models import Victima

        labels = dict(Victima.ActorVial.choices)
        queryset = (
            self
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

    def get_por_edad_sexo(self):
        """Agrupa por rango de edad y sexo (ya filtrado por el queryset)."""
        from .models import Victima

        ranges = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 120)]
        sexo_labels = dict(Victima.Sexo.choices)

        result = []
        for start, end in ranges:
            queryset = self.filter(edad__gte=start, edad__lte=end)
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

    def get_por_mes(self):
        """Agrupa por mes (respeta el queryset filtrado de la vista)."""
        queryset = (
            self
            .annotate(mes=TruncMonth('siniestro__fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        return self._fill_monthly_totals(queryset)

    def get_por_hora(self):
        """Agrupa por hora del día (respeta el queryset filtrado de la vista)."""
        queryset = (
            self
            .annotate(hora=ExtractHour('siniestro__fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        return self._fill_hourly_totals(queryset)

    def get_por_dia_hora(self):
        """Agrupa por día de semana y hora (respeta el queryset filtrado de la vista)."""
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        for item in (
            self
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

    def get_evolucion_anual(self):
        """Evolución anual de víctimas."""
        years_data = (
            self
            .annotate(ano=TruncYear('siniestro__fecha_hora'))
            .values('ano')
            .annotate(total=Count('id'))
            .order_by('ano')
        )
        
        result = []
        for item in years_data:
            if not item['ano']:
                continue
            
            year = item['ano'].year
            result.append({
                'ano': year,
                'total': item['total'],
            })
        
        return result


class VictimaManager(models.Manager):
    """Manager para Victima."""

    def get_queryset(self):
        return VictimaQuerySet(self.model, using=self._db)

    # Delegated methods for convenience
    def get_por_sexo(self):
        return self.get_queryset().get_por_sexo()

    def get_por_actor_vial(self):
        return self.get_queryset().get_por_actor_vial()

    def get_por_edad_sexo(self):
        return self.get_queryset().get_por_edad_sexo()

    def get_por_mes(self):
        return self.get_queryset().get_por_mes()

    def get_por_hora(self):
        return self.get_queryset().get_por_hora()

    def get_por_dia_hora(self):
        return self.get_queryset().get_por_dia_hora()

    def get_evolucion_anual(self):
        return self.get_queryset().get_evolucion_anual()
