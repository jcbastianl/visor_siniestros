from datetime import datetime

from django.db.models import Case, CharField, Count, Value, When
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncMonth
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Victima


class VictimasPorSexoView(APIView):
    """Aggregate victims per sexo for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        labels = dict(Victima.Sexo.choices)
        queryset = (
            Victima.objects
            .filter(siniestro__fecha_hora__year=year)
            .values('sexo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        data = [
            {
                'codigo': item['sexo'],
                'label': labels.get(item['sexo'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
            if item['sexo'] is not None
        ]
        return Response(data)


class VictimasPorActorVialView(APIView):
    """Aggregate victims per actor vial for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        labels = dict(Victima.ActorVial.choices)
        queryset = (
            Victima.objects
            .filter(siniestro__fecha_hora__year=year)
            .values('actor_vial')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        data = [
            {
                'codigo': item['actor_vial'],
                'label': labels.get(item['actor_vial'], 'No definido'),
                'total': item['total'],
            }
            for item in queryset
            if item['actor_vial'] is not None
        ]
        return Response(data)


class VictimasPorEdadSexoView(APIView):
    """Aggregate victims per age range and sexo for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        sexos = [Victima.Sexo.HOMBRE, Victima.Sexo.MUJER]
        rangos_edad = {
            '0-9': (0, 9),
            '10-19': (10, 19),
            '20-29': (20, 29),
            '30-39': (30, 39),
            '40-49': (40, 49),
            '50-59': (50, 59),
            '60-69': (60, 69),
            '70+': (70, 150),
        }

        data = {rango: {Victima.Sexo.HOMBRE: 0, Victima.Sexo.MUJER: 0} for rango in rangos_edad}

        rango_edad_case = Case(
            *[When(edad__range=rango, then=Value(nombre)) for nombre, rango in rangos_edad.items()],
            default=Value('No Registra'),
            output_field=CharField(max_length=20),
        )

        queryset = (
            Victima.objects
            .filter(
                siniestro__fecha_hora__year=year,
                sexo__in=sexos,
                edad__isnull=False,
            )
            .annotate(rango_edad=rango_edad_case)
            .values('rango_edad', 'sexo')
            .annotate(total=Count('id'))
            .order_by('rango_edad', 'sexo')
        )

        for item in queryset:
            rango = item['rango_edad']
            sexo = item['sexo']
            if rango in data and sexo in data[rango]:
                data[rango][sexo] = item['total']

        data_formateada = [
            {
                'rango': rango,
                'hombre': totales[Victima.Sexo.HOMBRE],
                'mujer': totales[Victima.Sexo.MUJER],
            }
            for rango, totales in data.items()
        ]
        return Response(data_formateada)


class VictimasPorMesView(APIView):
    """Aggregate victims per month for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        queryset = (
            Victima.objects
            .filter(siniestro__fecha_hora__year=year)
            .annotate(mes=TruncMonth('siniestro__fecha_hora'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )

        monthly_totals = {month: 0 for month in range(1, 13)}
        for item in queryset:
            monthly_totals[item['mes'].month] = item['total']

        data = [{'mes': month, 'total': monthly_totals[month]} for month in range(1, 13)]
        return Response(data)


class VictimasPorHoraView(APIView):
    """Aggregate victims per hour of day for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        queryset = (
            Victima.objects
            .filter(siniestro__fecha_hora__year=year)
            .annotate(hora=ExtractHour('siniestro__fecha_hora'))
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


class VictimasPorDiaHoraView(APIView):
    """Aggregate victims per weekday and hour for a given year."""

    def get(self, request, format=None):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
        except ValueError:
            return Response({'error': "Parámetro 'year' debe ser un número."}, status=400)

        matrix = {day: {hour: 0 for hour in range(24)} for day in range(1, 8)}

        queryset = (
            Victima.objects
            .filter(siniestro__fecha_hora__year=year)
            .annotate(
                dia_semana=ExtractWeekDay('siniestro__fecha_hora'),
                hora_dia=ExtractHour('siniestro__fecha_hora'),
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
