from datetime import datetime

from django.db.models import Count, Case, When, Value, CharField
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay

from rest_framework import serializers, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Siniestro, Victima, Causa, TipoSiniestro

# --- 1. Serializers para las Opciones (Tablas de Filtros) ---
# Estos son los traductores para tus listas de opciones.
# Los usaremos para "anidarlos" dentro del siniestro.

class CausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Causa
        fields = ['id', 'nombre', 'activo'] # El frontend necesita saber si está activo

class TipoSiniestroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSiniestro
        fields = ['id', 'nombre', 'activo']


# --- 2. Serializer para las Víctimas ---
# Este lo usaremos para anidarlo dentro de cada Siniestro.

class VictimaSerializer(serializers.ModelSerializer):
    # --- BUENA PRÁCTICA ---
    # Por defecto, DRF mostraría solo el CÓDIGO (ej. "FALLECIDO").
    # Usamos 'source' para obtener el texto legible (ej. "Fallecido").
    condicion_label = serializers.CharField(source='get_condicion_display')
    sexo_label = serializers.CharField(source='get_sexo_display')
    actor_vial_label = serializers.CharField(source='get_actor_vial_display')

    class Meta:
        model = Victima
        fields = [
            'id', 'edad', 
            'condicion',        # El código (ej. "FALLECIDO")
            'condicion_label',  # El texto (ej. "Fallecido")
            'sexo',
            'sexo_label',
            'actor_vial',
            'actor_vial_label'
        ]


# --- 3. Serializer Principal (Siniestro) ---
# Este es el traductor más importante.

class SiniestroSerializer(serializers.ModelSerializer):
    """
    Este es el "traductor" principal que convierte un Siniestro
    en un JSON completo y fácil de leer para el frontend.
    """
    
    # --- BUENA PRÁCTICA: Serializadores Anidados ---
    # En lugar de mostrar solo el ID (ej. tipo_siniestro: 5),
    # le decimos a DRF que use los otros serializers para mostrar el objeto completo.
    tipo_siniestro = TipoSiniestroSerializer(read_only=True)
    causa_probable = CausaSerializer(read_only=True)
    
    # Para la relación inversa (de Siniestro -> a todas sus Víctimas)
    # Usamos 'many=True' porque un siniestro puede tener MUCHAS víctimas.
    victimas = VictimaSerializer(many=True, read_only=True)
    
    # También obtenemos el texto legible para 'grado_severidad'
    severidad_label = serializers.CharField(source='get_grado_severidad_display')

    class Meta:
        model = Siniestro
        fields = [
            'id', 
            'fecha_hora', 
            'latitud', 
            'longitud', 
            'via',
            'grado_severidad', # El código (ej. "CON_FALLECIDOS")
            'severidad_label', # El texto (ej. "con fallecidos en sitio")
            'tipo_siniestro',  # Objeto anidado { id: 1, nombre: "Atropello", ... }
            'causa_probable',  # Objeto anidado { id: 1, nombre: "Exceso de...", ... }
            'victimas'         # Lista anidada [ { id: 1, ... }, { id: 2, ... } ]
        ]


class SiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose siniestros in read-only form for the API router."""
    queryset = Siniestro.objects.all()
    serializer_class = SiniestroSerializer


class CausaViewSet(viewsets.ReadOnlyModelViewSet):
    """List only active causas, used by the router."""
    serializer_class = CausaSerializer

    def get_queryset(self):
        return Causa.objects.filter(activo=True)


class TipoSiniestroViewSet(viewsets.ReadOnlyModelViewSet):
    """List only active tipos de siniestro."""
    serializer_class = TipoSiniestroSerializer

    def get_queryset(self):
        return TipoSiniestro.objects.filter(activo=True)

# --- 3. VISTA PARA LOS KPIs (Las tarjetas) ---

class KPIStatsView(APIView):
    """
    Una vista personalizada para calcular y devolver los 3 KPIs
    principales del dashboard.
    """
    
    def get(self, request, format=None):
        """
        Esta función se ejecuta cuando alguien hace un GET a esta URL.
        """
        
        # 1. Hacemos las consultas a la base de datos
        # Usamos los .count() de Django, son súper eficientes
        
        total_siniestros = Siniestro.objects.count()
        
        # Usamos los TextChoices que definimos en el modelo
        total_lesionados = Victima.objects.filter(
            condicion=Victima.Condicion.LESIONADO
        ).count()
        
        total_fallecidos = Victima.objects.filter(
            condicion=Victima.Condicion.FALLECIDO
        ).count()
        
        # 2. Preparamos el diccionario de respuesta
        data = {
            'total_siniestros': total_siniestros,
            'total_lesionados': total_lesionados,
            'total_fallecidos': total_fallecidos
        }
        
        # 3. Enviamos la respuesta en formato JSON
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
    """Aggregate siniestros per severidad for the donut chart."""

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


class VictimasPorSexoView(APIView):
    """Aggregate victimas per sexo for a given year."""

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
    """Aggregate victimas per actor vial for a given year."""

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
    """Aggregate victimas per age range and sexo for a given year."""

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
            output_field=CharField(),
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
    """Aggregate victimas per month for a given year."""

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
    """Aggregate victimas per hour of day for a given year."""

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