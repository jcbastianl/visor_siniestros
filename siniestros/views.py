"""
views.py - ViewSets consolidados para toda la API

Arquitectura pragmática:
- Un ViewSet por recurso principal (Siniestro, Victima)
- Acciones estadísticas integradas como @action(detail=False)
- Lógica delegada a QuerySets en managers.py
- Filtrado avanzado usando django-filter con SiniestroFilter
- Caching automático para endpoints de estadísticas
- Documentación Swagger automática con @extend_schema
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

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
    """ViewSet para Siniestros con estadísticas integradas y filtros avanzados."""

    queryset = Siniestro.objects.all()
    serializer_class = SiniestroSerializer
    filterset_class = SiniestroFilter

    @extend_schema(
        summary="KPIs principales",
        description="Total de siniestros, lesionados y fallecidos",
        responses=KPIStatsSerializer
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))  # Cache 5 minutos
    def kpi_stats(self, request):
        """KPIs: Total siniestros, lesionados, fallecidos."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_kpi_stats()
        serializer = KPIStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas mensuales",
        description="Siniestros agrupados por mes del año",
        responses=MonthlyStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_mes(self, request):
        """Siniestros por mes (rellena meses vacíos con 0)."""
        queryset = self.filter_queryset(self.get_queryset())
        # Obtén el año del queryset filtrado si está disponible
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_mes(year=year)
        serializer = MonthlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por severidad",
        description="Siniestros agrupados por grado de severidad",
        responses=SeveridadStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_severidad(self, request):
        """Siniestros por severidad."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_severidad()
        serializer = SeveridadStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por hora del día",
        description="Siniestros agrupados por hora (0-23)",
        responses=HourlyStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_hora(self, request):
        """Siniestros por hora del día (rellena horas vacías con 0)."""
        queryset = self.filter_queryset(self.get_queryset())
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_hora(year=year)
        serializer = HourlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Matriz día × hora",
        description="Siniestros en matriz de 7 días × 24 horas",
        responses=DayHourStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_dia_hora(self, request):
        """Siniestros por día de semana × hora (matriz 7×24)."""
        queryset = self.filter_queryset(self.get_queryset())
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_dia_hora(year=year)
        serializer = DayHourStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por vía",
        description="Siniestros agrupados por vía con conteo de lesionados y fallecidos",
        responses=ViaStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_via(self, request):
        """Siniestros por vía (Top 20)."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_via()
        serializer = ViaStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por causa probable",
        description="Siniestros agrupados por causa probable",
        responses=CausaProbableStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_causa_probable(self, request):
        """Siniestros por causa probable."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_causa_probable()
        serializer = CausaProbableStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por tipo de siniestro",
        description="Siniestros agrupados por tipo",
        responses=TipoSiniestroStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_tipo_siniestro(self, request):
        """Siniestros por tipo de siniestro."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_tipo_siniestro()
        serializer = TipoSiniestroStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Evolución anual de siniestros",
        description="Siniestros, lesionados y fallecidos por año",
        responses=EvolucionAnualSiniestrosSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))  # Cache 1 hora
    def evolucion_anual(self, request):
        """Evolución anual de siniestros."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_evolucion_anual()
        serializer = EvolucionAnualSiniestrosSerializer(stats, many=True)
        return Response(serializer.data)


class VictimaViewSet(ReadOnlyModelViewSet):
    """ViewSet para Víctimas con estadísticas integradas y filtros avanzados."""

    queryset = Victima.objects.all()
    serializer_class = VictimaSerializer
    filterset_class = VictimaFilter

    @extend_schema(
        summary="Estadísticas por sexo",
        description="Víctimas agrupadas por sexo",
        responses=SexoStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_sexo(self, request):
        """Víctimas por sexo."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_sexo()
        serializer = SexoStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por actor vial",
        description="Víctimas agrupadas por actor vial (peatón, conductor, etc)",
        responses=ActorVialStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_actor_vial(self, request):
        """Víctimas por actor vial (peatón, conductor, pasajero)."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_actor_vial()
        serializer = ActorVialStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por edad y sexo",
        description="Víctimas agrupadas por rango de edad y sexo",
        responses=EdadSexoRangeSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_edad_sexo(self, request):
        """Víctimas por rango de edad y sexo."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_por_edad_sexo()
        serializer = EdadSexoRangeSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas mensuales",
        description="Víctimas agrupadas por mes del año",
        responses=MonthlyStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_mes(self, request):
        """Víctimas por mes."""
        queryset = self.filter_queryset(self.get_queryset())
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_mes(year=year)
        serializer = MonthlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estadísticas por hora del día",
        description="Víctimas agrupadas por hora (0-23)",
        responses=HourlyStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_hora(self, request):
        """Víctimas por hora del día."""
        queryset = self.filter_queryset(self.get_queryset())
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_hora(year=year)
        serializer = HourlyStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Matriz día × hora",
        description="Víctimas en matriz de 7 días × 24 horas",
        responses=DayHourStatSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))
    def por_dia_hora(self, request):
        """Víctimas por día de semana × hora."""
        queryset = self.filter_queryset(self.get_queryset())
        year = request.query_params.get('year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        stats = queryset.get_por_dia_hora(year=year)
        serializer = DayHourStatSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Evolución anual de víctimas",
        description="Víctimas totales por año",
        responses=EvolucionAnualVictimasSerializer(many=True)
    )
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))  # Cache 1 hora
    def evolucion_anual(self, request):
        """Evolución anual de víctimas."""
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.get_evolucion_anual()
        serializer = EvolucionAnualVictimasSerializer(stats, many=True)
        return Response(serializer.data)


class CausaViewSet(ReadOnlyModelViewSet):
    """ViewSet para Causas (catálogo)."""

    queryset = Causa.objects.filter(activo=True)
    serializer_class = CausaSerializer


class TipoSiniestroViewSet(ReadOnlyModelViewSet):
    """ViewSet para Tipos de Siniestro (catálogo)."""

    queryset = TipoSiniestro.objects.filter(activo=True)
    serializer_class = TipoSiniestroSerializer
