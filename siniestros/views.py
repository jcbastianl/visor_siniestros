"""
ViewSets de la API REST para siniestros y víctimas.

Cada ViewSet expone endpoints CRUD (solo lectura) y acciones estadísticas
como @action(detail=False). La lógica de agregación se delega a los
QuerySets en managers.py. El filtrado usa django-filter (ver filters.py).
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, ExtractHour

from .models import Siniestro, Victima, Causa, TipoSiniestro
from .filters import SiniestroFilter, VictimaFilter
from .serializers import (
    SiniestroSerializer, VictimaSerializer, CausaSerializer,
    TipoSiniestroSerializer, KPIStatsSerializer, MonthlyStatSerializer,
    HourlyStatSerializer, DayHourStatSerializer, SeveridadStatSerializer,
    SexoStatSerializer, ActorVialStatSerializer, EdadSexoRangeSerializer,
    ViaStatSerializer, CausaProbableStatSerializer, TipoSiniestroStatSerializer,
    EvolucionAnualSiniestrosSerializer, EvolucionAnualVictimasSerializer
)


class SiniestroViewSet(ReadOnlyModelViewSet):
    """
    ViewSet para Siniestros con estadísticas integradas y filtros avanzados.

    Endpoints de estadísticas disponibles como acciones:
    - kpi_stats: Totales generales
    - por_mes, por_hora, por_dia_hora: Distribución temporal
    - por_severidad, por_via, por_causa_probable, por_tipo_siniestro: Clasificación
    - evolucion_anual: Tendencia histórica
    - map_data: Datos optimizados para renderizar mapa
    - filtros_disponibles: Opciones dinámicas para dropdowns del frontend
    """

    queryset = Siniestro.objects.all()
    serializer_class = SiniestroSerializer
    filterset_class = SiniestroFilter

    @extend_schema(summary="KPIs principales", responses=KPIStatsSerializer)
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def kpi_stats(self, request):
        """Total siniestros, lesionados y fallecidos."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_kpi_stats()
        serializer = KPIStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(summary="Estadísticas mensuales", responses=MonthlyStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_mes(self, request):
        """Siniestros por mes (rellena meses vacíos con 0)."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_mes()
        serializer = MonthlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por severidad", responses=SeveridadStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_severidad(self, request):
        """Siniestros agrupados por grado de severidad."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_severidad()
        serializer = SeveridadStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por hora del día", responses=HourlyStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_hora(self, request):
        """Siniestros por hora del día (rellena horas vacías con 0)."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_hora()
        serializer = HourlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Matriz día x hora", responses=DayHourStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_dia_hora(self, request):
        """Matriz 7 días x 24 horas."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_dia_hora()
        serializer = DayHourStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Top 20 vías", responses=ViaStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_via(self, request):
        """Top 20 vías con más siniestros, lesionados y fallecidos."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_via()
        serializer = ViaStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por causa probable", responses=CausaProbableStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_causa_probable(self, request):
        """Siniestros agrupados por causa probable."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_causa_probable()
        serializer = CausaProbableStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por tipo de siniestro", responses=TipoSiniestroStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_tipo_siniestro(self, request):
        """Siniestros agrupados por tipo."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_tipo_siniestro()
        serializer = TipoSiniestroStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Evolución anual", responses=EvolucionAnualSiniestrosSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))
    def evolucion_anual(self, request):
        """Siniestros, lesionados y fallecidos por año."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_evolucion_anual()
        serializer = EvolucionAnualSiniestrosSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Datos para mapa")
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def map_data(self, request):
        """
        Endpoint optimizado para el mapa. Usa .values() para devolver solo
        coordenadas y metadata esencial, evitando la serialización pesada de DRF.
        """
        queryset = self.filter_queryset(self.get_queryset())
        data = list(queryset.values(
            'id', 'latitud', 'longitud', 'grado_severidad',
            'fecha_hora', 'via',
            'tipo_siniestro__nombre', 'causa_probable__nombre'
        ))
        return Response(data)

    @extend_schema(summary="Filtros disponibles con datos")
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def filtros_disponibles(self, request):
        """
        Devuelve solo las opciones de filtro que tienen datos según los filtros activos.
        Útil para poblar dropdowns dinámicos: si filtras por año=2021, solo devuelve
        las causas que existen en 2021.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Causas con datos
        causas = list(
            queryset
            .values('causa_probable__id', 'causa_probable__nombre')
            .annotate(total=Count('id'))
            .filter(causa_probable__isnull=False)
            .order_by('-total')
        )
        causas_formatted = [
            {'id': c['causa_probable__id'], 'nombre': c['causa_probable__nombre'], 'total': c['total']}
            for c in causas
        ]

        # Tipos de siniestro con datos
        tipos = list(
            queryset
            .values('tipo_siniestro__id', 'tipo_siniestro__nombre')
            .annotate(total=Count('id'))
            .filter(tipo_siniestro__isnull=False)
            .order_by('-total')
        )
        tipos_formatted = [
            {'id': t['tipo_siniestro__id'], 'nombre': t['tipo_siniestro__nombre'], 'total': t['total']}
            for t in tipos
        ]

        # Días de la semana con datos
        dias_nombres = {
            1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles',
            5: 'Jueves', 6: 'Viernes', 7: 'Sábado'
        }
        dias = list(
            queryset
            .annotate(dia=ExtractWeekDay('fecha_hora'))
            .values('dia')
            .annotate(total=Count('id'))
            .order_by('dia')
        )
        dias_formatted = [
            {'dia': d['dia'], 'nombre': dias_nombres.get(d['dia'], f'Día {d["dia"]}'), 'total': d['total']}
            for d in dias
        ]

        # Horas con datos
        horas = list(
            queryset
            .annotate(hora=ExtractHour('fecha_hora'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        horas_formatted = [{'hora': h['hora'], 'total': h['total']} for h in horas]

        return Response({
            'causas': causas_formatted,
            'tipos_siniestro': tipos_formatted,
            'dias_semana': dias_formatted,
            'horas': horas_formatted
        })


class VictimaViewSet(ReadOnlyModelViewSet):
    """
    ViewSet para Víctimas con estadísticas por sexo, actor vial, edad y distribución temporal.
    """

    queryset = Victima.objects.all()
    serializer_class = VictimaSerializer
    filterset_class = VictimaFilter

    @extend_schema(summary="Por sexo", responses=SexoStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_sexo(self, request):
        """Víctimas agrupadas por sexo."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_sexo()
        serializer = SexoStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por actor vial", responses=ActorVialStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_actor_vial(self, request):
        """Víctimas por actor vial (peatón, motocicleta, vehículo, etc.)."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_actor_vial()
        serializer = ActorVialStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Por edad y sexo", responses=EdadSexoRangeSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_edad_sexo(self, request):
        """Víctimas por rango de edad y sexo."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_edad_sexo()
        serializer = EdadSexoRangeSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Víctimas por mes", responses=MonthlyStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_mes(self, request):
        """Víctimas agrupadas por mes."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_mes()
        serializer = MonthlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Víctimas por hora", responses=HourlyStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_hora(self, request):
        """Víctimas por hora del día."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_hora()
        serializer = HourlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Víctimas día x hora", responses=DayHourStatSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_dia_hora(self, request):
        """Matriz 7 días x 24 horas de víctimas."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_dia_hora()
        serializer = DayHourStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Evolución anual víctimas", responses=EvolucionAnualVictimasSerializer(many=True))
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))
    def evolucion_anual(self, request):
        """Víctimas totales por año."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_evolucion_anual()
        serializer = EvolucionAnualVictimasSerializer(stats, many=True)
        return Response(serializer.data)


class CausaViewSet(ReadOnlyModelViewSet):
    """Catálogo de causas probables (solo activas)."""
    queryset = Causa.objects.filter(activo=True)
    serializer_class = CausaSerializer


class TipoSiniestroViewSet(ReadOnlyModelViewSet):
    """Catálogo de tipos de siniestro (solo activos)."""
    queryset = TipoSiniestro.objects.filter(activo=True)
    serializer_class = TipoSiniestroSerializer
