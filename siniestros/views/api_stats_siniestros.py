from datetime import datetime

from django.db.models import Count
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Siniestro, Victima


class KPIStatsView(APIView):
    """Expose the top-level KPIs for siniestros and victims."""

    def get(self, request, format=None):
        total_siniestros = Siniestro.objects.count()
        total_lesionados = Victima.objects.filter(
            condicion=Victima.Condicion.LESIONADO
        ).count()
        total_fallecidos = Victima.objects.filter(
            condicion=Victima.Condicion.FALLECIDO
        ).count()
        data = {
            'total_siniestros': total_siniestros,
            'total_lesionados': total_lesionados,
            'total_fallecidos': total_fallecidos,
        }
        return Response(data)


class SiniestrosPorMesView(APIView):
    """Aggregate siniestros per month for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        queryset = (
            Siniestro.objects
            .filter(fecha_hora__year=year)
            .annotate(mes=TruncMonth('fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        monthly_totals = {month: 0 for month in range(1, 13)}
        for item in queryset:
            monthly_totals[item['mes'].month] = item['total']

        data = [{'mes': month, 'total': monthly_totals[month]} for month in range(1, 13)]
        return Response(data)


class SeveridadStatsView(APIView):
    """Aggregate siniestros by severidad."""

    def get(self, request, format=None):
        labels = dict(Siniestro.Severidad.choices)
        queryset = (
            Siniestro.objects
            .values('grado_severidad')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        data = [
            {
                'codigo': item['grado_severidad'],
                'label': labels.get(item['grado_severidad'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
            if item['grado_severidad'] is not None
        ]
        return Response(data)


class SiniestrosPorHoraView(APIView):
    """Aggregate siniestros per hour of day for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        queryset = (
            Siniestro.objects
            .filter(fecha_hora__year=year)
            .annotate(hora=ExtractHour('fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )

        hourly_totals = {hour: 0 for hour in range(24)}
        for item in queryset:
            hourly_totals[item['hora']] = item['total']

        data = [
            {
                'rango_hora': f'{hour:02d}:00 - {hour:02d}:59',
                'total': hourly_totals[hour],
            }
            for hour in range(24)
        ]
        return Response(data)


class SiniestrosPorDiaHoraView(APIView):
    """Aggregate siniestros per weekday and hour for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        queryset = (
            Siniestro.objects
            .filter(fecha_hora__year=year)
            .annotate(
                dia_semana=ExtractWeekDay('fecha_hora'),
                hora_dia=ExtractHour('fecha_hora'),
            )
            .values('dia_semana', 'hora_dia')
            .annotate(total=Count('id'))
        )

        for item in queryset:
            day = item['dia_semana']
            hour = item['hora_dia']
            if day in matrix and hour is not None:
                matrix[day][hour] = item['total']

        data = [
            {
                'dia_semana': day,
                'hora_dia': hour,
                'total': matrix[day][hour],
            }
            for day in range(1, 8)
            for hour in range(24)
        ]
        return Response(data)
