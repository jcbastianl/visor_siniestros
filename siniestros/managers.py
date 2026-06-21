"""
QuerySets y Managers personalizados para la lógica de agregación estadística.

Centraliza toda la lógica de análisis para mantener models.py y views.py limpios.
Cada método de agregación respeta el queryset filtrado que recibe de la vista.
"""

from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay, TruncYear


class SiniestroQuerySet(models.QuerySet):
    """QuerySet para Siniestro con métodos de agregación estadística."""

    def _fill_monthly(self, queryset):
        """Rellena los 12 meses con datos o ceros para meses sin registros.

        Acumula (``+=``) los totales del mismo mes calendario entre años: como
        ``TruncMonth`` conserva el año, un mismo mes aparece en filas distintas por
        año y deben sumarse, no sobrescribirse.
        """
        monthly = {m: 0 for m in range(1, 13)}
        for item in queryset:
            if item['mes']:
                monthly[item['mes'].month] += item['total']
        return [{'mes': m, 'total': monthly[m]} for m in range(1, 13)]

    def _fill_hourly(self, queryset):
        """Rellena las 24 horas con datos o ceros para horas sin registros."""
        hourly = {h: 0 for h in range(24)}
        for item in queryset:
            if item['hora'] is not None:
                hourly[item['hora']] = item['total']
        return [{'rango_hora': f'{h:02d}:00 - {h:02d}:59', 'total': hourly[h]} for h in range(24)]

    def get_kpi_stats(self):
        """KPIs: total siniestros, lesionados y fallecidos."""
        stats = self.aggregate(
            total_lesionados=Sum('num_heridos'),
            total_fallecidos=Sum('num_fallecidos')
        )
        return {
            'total_siniestros': self.count(),
            'total_lesionados': stats['total_lesionados'] or 0,
            'total_fallecidos': stats['total_fallecidos'] or 0,
        }

    def get_por_mes(self):
        """Siniestros agrupados por mes (siempre devuelve 12 entradas)."""
        qs = self.annotate(mes=TruncMonth('fecha_hora')).values('mes').annotate(total=Count('id')).order_by('mes')
        return self._fill_monthly(qs)

    def get_por_severidad(self):
        """Siniestros agrupados por grado de severidad."""
        from .models import Siniestro
        labels = dict(Siniestro.Severidad.choices)
        qs = self.values('grado_severidad').annotate(total=Count('id')).order_by('-total')
        return [
            {'codigo': item['grado_severidad'], 'label': labels.get(item['grado_severidad'], 'No definido'), 'total': item['total']}
            for item in qs
        ]

    def get_por_hora(self):
        """Siniestros por hora del día (siempre devuelve 24 entradas)."""
        qs = self.annotate(hora=ExtractHour('fecha_hora')).values('hora').annotate(total=Count('id')).order_by('hora')
        return self._fill_hourly(qs)

    def get_por_dia_hora(self):
        """Matriz 7 días x 24 horas de siniestros."""
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}
        for item in (
            self.annotate(dia_semana=ExtractWeekDay('fecha_hora'), hora_dia=ExtractHour('fecha_hora'))
            .values('dia_semana', 'hora_dia').annotate(total=Count('id'))
        ):
            day, hour = item['dia_semana'], item['hora_dia']
            if day in matrix and hour is not None:
                matrix[day][hour] = item['total']
        return [
            {'dia_semana': day, 'hora_dia': hour, 'total': matrix[day][hour]}
            for day in range(1, 8) for hour in range(24)
        ]

    def get_por_via(self):
        """Top 20 vías con más siniestros, incluyendo conteo de lesionados y fallecidos."""
        qs = (
            self.values('via')
            .annotate(total_siniestros=Count('id'), total_lesionados=Sum('num_heridos'), total_fallecidos=Sum('num_fallecidos'))
            .order_by('-total_siniestros')[:20]
        )
        return [
            {
                'via': item['via'] or 'Sin especificar',
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': item['total_lesionados'] or 0,
                'total_fallecidos': item['total_fallecidos'] or 0,
            }
            for item in qs
        ]

    def get_por_causa_probable(self):
        """Siniestros agrupados por causa probable con conteo de víctimas."""
        from .models import Victima
        qs = self.values('causa_probable__nombre', 'causa_probable__id').annotate(total_siniestros=Count('id')).order_by('-total_siniestros')
        result = []
        for item in qs:
            siniestros_causa = self.filter(causa_probable__nombre=item['causa_probable__nombre'])
            result.append({
                'id': item['causa_probable__id'],
                'causa': item['causa_probable__nombre'] or 'Sin especificar',
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': Victima.objects.filter(condicion=Victima.Condicion.LESIONADO, siniestro__in=siniestros_causa).count(),
                'total_fallecidos': Victima.objects.filter(condicion=Victima.Condicion.FALLECIDO, siniestro__in=siniestros_causa).count(),
            })
        return result

    def get_por_tipo_siniestro(self):
        """Siniestros agrupados por tipo con conteo de víctimas."""
        from .models import Victima
        qs = self.values('tipo_siniestro__nombre', 'tipo_siniestro__id').annotate(total_siniestros=Count('id')).order_by('-total_siniestros')
        result = []
        for item in qs:
            siniestros_tipo = self.filter(tipo_siniestro__nombre=item['tipo_siniestro__nombre'])
            result.append({
                'id': item['tipo_siniestro__id'],
                'tipo': item['tipo_siniestro__nombre'] or 'Sin especificar',
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': Victima.objects.filter(condicion=Victima.Condicion.LESIONADO, siniestro__in=siniestros_tipo).count(),
                'total_fallecidos': Victima.objects.filter(condicion=Victima.Condicion.FALLECIDO, siniestro__in=siniestros_tipo).count(),
            })
        return result

    def get_evolucion_anual(self):
        """Evolución anual: siniestros, lesionados y fallecidos por año."""
        qs = (
            self.annotate(ano=TruncYear('fecha_hora')).values('ano')
            .annotate(total_siniestros=Count('id'), total_lesionados=Sum('num_heridos'), total_fallecidos=Sum('num_fallecidos'))
            .order_by('ano')
        )
        return [
            {
                'ano': item['ano'].year,
                'total_siniestros': item['total_siniestros'],
                'total_lesionados': item['total_lesionados'] or 0,
                'total_fallecidos': item['total_fallecidos'] or 0,
            }
            for item in qs if item['ano']
        ]


class SiniestroManager(models.Manager):
    """Manager que expone el SiniestroQuerySet personalizado."""

    def get_queryset(self):
        return SiniestroQuerySet(self.model, using=self._db)

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

    def _fill_monthly(self, queryset):
        """Rellena los 12 meses con datos o ceros."""
        monthly = {m: 0 for m in range(1, 13)}
        for item in queryset:
            if item['mes']:
                monthly[item['mes'].month] += item['total']
        return [{'mes': m, 'total': monthly[m]} for m in range(1, 13)]

    def _fill_hourly(self, queryset):
        """Rellena las 24 horas con datos o ceros."""
        hourly = {h: 0 for h in range(24)}
        for item in queryset:
            if item['hora'] is not None:
                hourly[item['hora']] = item['total']
        return [{'rango_hora': f'{h:02d}:00 - {h:02d}:59', 'total': hourly[h]} for h in range(24)]

    def get_por_sexo(self):
        """Víctimas agrupadas por sexo."""
        from .models import Victima
        labels = dict(Victima.Sexo.choices)
        qs = self.values('sexo').annotate(total=Count('id')).order_by('-total')
        return [
            {'sexo': item['sexo'], 'label': labels.get(item['sexo'], 'No definido'), 'total': item['total']}
            for item in qs if item['sexo'] is not None
        ]

    def get_por_actor_vial(self):
        """Víctimas agrupadas por actor vial."""
        from .models import Victima
        labels = dict(Victima.ActorVial.choices)
        qs = self.values('actor_vial').annotate(total=Count('id')).order_by('-total')
        return [
            {'actor_vial': item['actor_vial'], 'label': labels.get(item['actor_vial'], 'No definido'), 'total': item['total']}
            for item in qs if item['actor_vial'] is not None
        ]

    def get_por_edad_sexo(self):
        """Víctimas agrupadas por rango de edad (0-9, 10-19, ..., 70+) y sexo."""
        from .models import Victima
        ranges = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 120)]
        sexo_labels = dict(Victima.Sexo.choices)
        result = []
        for start, end in ranges:
            qs = self.filter(edad__gte=start, edad__lte=end)
            for sexo_val in [Victima.Sexo.HOMBRE, Victima.Sexo.MUJER]:
                result.append({
                    'rango_edad': f'{start}-{end}',
                    'sexo': sexo_val,
                    'sexo_label': sexo_labels.get(sexo_val, 'No definido'),
                    'total': qs.filter(sexo=sexo_val).count(),
                })
        return result

    def get_por_mes(self):
        """Víctimas agrupadas por mes (siempre devuelve 12 entradas)."""
        qs = (
            self.annotate(mes=TruncMonth('siniestro__fecha_hora'))
            .values('mes').annotate(total=Count('id')).order_by('mes')
        )
        return self._fill_monthly(qs)

    def get_por_hora(self):
        """Víctimas por hora del día (siempre devuelve 24 entradas)."""
        qs = (
            self.annotate(hora=ExtractHour('siniestro__fecha_hora'))
            .values('hora').annotate(total=Count('id')).order_by('hora')
        )
        return self._fill_hourly(qs)

    def get_por_dia_hora(self):
        """Matriz 7 días x 24 horas de víctimas."""
        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}
        for item in (
            self.annotate(dia_semana=ExtractWeekDay('siniestro__fecha_hora'), hora_dia=ExtractHour('siniestro__fecha_hora'))
            .values('dia_semana', 'hora_dia').annotate(total=Count('id'))
        ):
            day, hour = item['dia_semana'], item['hora_dia']
            if day in matrix and hour is not None:
                matrix[day][hour] = item['total']
        return [
            {'dia_semana': day, 'hora_dia': hour, 'total': matrix[day][hour]}
            for day in range(1, 8) for hour in range(24)
        ]

    def get_evolucion_anual(self):
        """Víctimas totales por año."""
        qs = self.annotate(ano=TruncYear('siniestro__fecha_hora')).values('ano').annotate(total=Count('id')).order_by('ano')
        return [{'ano': item['ano'].year, 'total': item['total']} for item in qs if item['ano']]


class VictimaManager(models.Manager):
    """Manager que expone el VictimaQuerySet personalizado."""

    def get_queryset(self):
        return VictimaQuerySet(self.model, using=self._db)

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
