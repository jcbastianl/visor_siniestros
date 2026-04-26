"""
Serializers para la API REST de siniestros y víctimas.

Contiene dos grupos de serializers:
- **CRUD**: ``SiniestroSerializer``, ``VictimaSerializer``, ``CausaSerializer``,
  ``TipoSiniestroSerializer`` — para endpoints de lectura de registros.
- **Estadísticas**: Serializers ligeros (``Serializer`` base) para endpoints
  de agregación que devuelven datos calculados, no instancias de modelos.
"""

from rest_framework import serializers
from .models import Causa, Siniestro, TipoSiniestro, Victima


# ──────────────────────────────────────────────
# Serializers CRUD (ModelSerializer)
# ──────────────────────────────────────────────

class CausaSerializer(serializers.ModelSerializer):
    """
    Serializer para el catálogo de causas probables.

    Campos expuestos: ``id``, ``nombre``, ``activo``.
    """

    class Meta:
        model = Causa
        fields = ['id', 'nombre', 'activo']


class TipoSiniestroSerializer(serializers.ModelSerializer):
    """
    Serializer para el catálogo de tipos de siniestro.

    Campos expuestos: ``id``, ``nombre``, ``activo``.
    """

    class Meta:
        model = TipoSiniestro
        fields = ['id', 'nombre', 'activo']


class VictimaSerializer(serializers.ModelSerializer):
    """
    Serializer para víctimas de siniestros.

    Incluye campos derivados con ``_label`` que exponen la etiqueta legible
    de cada ``TextChoices`` (condición, sexo, actor vial).
    """

    condicion_label = serializers.CharField(source='get_condicion_display', read_only=True)
    sexo_label = serializers.CharField(source='get_sexo_display', read_only=True)
    actor_vial_label = serializers.CharField(source='get_actor_vial_display', read_only=True)

    class Meta:
        model = Victima
        fields = [
            'id', 'edad',
            'condicion', 'condicion_label',
            'sexo', 'sexo_label',
            'actor_vial', 'actor_vial_label',
        ]


class SiniestroSerializer(serializers.ModelSerializer):
    """
    Serializer completo para un siniestro de tránsito.

    Incluye relaciones anidadas (tipo, causa, víctimas) y la label
    legible del grado de severidad. Usado en endpoints de detalle y listado.
    """

    tipo_siniestro = TipoSiniestroSerializer(read_only=True)
    causa_probable = CausaSerializer(read_only=True)
    victimas = VictimaSerializer(many=True, read_only=True)
    severidad_label = serializers.CharField(source='get_grado_severidad_display', read_only=True)

    class Meta:
        model = Siniestro
        fields = [
            'id', 'fecha_hora', 'latitud', 'longitud', 'via',
            'grado_severidad', 'severidad_label',
            'tipo_siniestro', 'causa_probable', 'victimas',
            'zona', 'barrio', 'parroquia', 'parroquia_rural',
            'direccion_completa', 'calle_principal', 'calle_secundaria', 'referencia',
            'condicion_calzada', 'condicion_atmosferica', 'condicion_via',
            'luz_artificial', 'lugar_en_via', 'senalizacion_existente',
            'num_vehiculos_involucrados', 'vehiculos_particular',
            'vehiculos_publico', 'vehiculos_comercial', 'tipos_vehiculos', 'vehiculos_retenidos',
            'num_heridos', 'num_fallecidos', 'num_pruebas_alcohotest', 'num_personas_detenidas',
            'tiene_danos_bien_publico', 'descripcion_dano_bien_publico',
            'datos_adicionales',
        ]


# ──────────────────────────────────────────────
# Serializers de estadísticas (no vinculados a modelos)
# ──────────────────────────────────────────────

class KPIStatsSerializer(serializers.Serializer):
    """KPIs globales: total de siniestros, lesionados y fallecidos."""

    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class MonthlyStatSerializer(serializers.Serializer):
    """Conteo agrupado por mes (1-12)."""

    mes = serializers.IntegerField()
    total = serializers.IntegerField()


class HourlyStatSerializer(serializers.Serializer):
    """Conteo agrupado por rango horario (ej. '08:00 - 08:59')."""

    rango_hora = serializers.CharField()
    total = serializers.IntegerField()


class DayHourStatSerializer(serializers.Serializer):
    """Celda de la matriz día de la semana × hora del día."""

    dia_semana = serializers.IntegerField()
    hora_dia = serializers.IntegerField()
    total = serializers.IntegerField()


class SeveridadStatSerializer(serializers.Serializer):
    """Conteo agrupado por grado de severidad con código y label legible."""

    codigo = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class SexoStatSerializer(serializers.Serializer):
    """Conteo de víctimas agrupado por sexo."""

    sexo = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class ActorVialStatSerializer(serializers.Serializer):
    """Conteo de víctimas agrupado por actor vial (peatón, motocicleta, etc.)."""

    actor_vial = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class EdadSexoRangeSerializer(serializers.Serializer):
    """Conteo de víctimas por rango de edad (0-9, 10-19, …, 70+) cruzado con sexo."""

    rango_edad = serializers.CharField()
    sexo = serializers.CharField()
    sexo_label = serializers.CharField()
    total = serializers.IntegerField()


class ViaStatSerializer(serializers.Serializer):
    """Estadísticas de una vía: siniestros, lesionados y fallecidos."""

    via = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class CausaProbableStatSerializer(serializers.Serializer):
    """Estadísticas agrupadas por causa probable."""

    id = serializers.IntegerField()
    causa = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class TipoSiniestroStatSerializer(serializers.Serializer):
    """Estadísticas agrupadas por tipo de siniestro."""

    id = serializers.IntegerField()
    tipo = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class EvolucionAnualSiniestrosSerializer(serializers.Serializer):
    """Evolución anual: siniestros, lesionados y fallecidos por año."""

    ano = serializers.IntegerField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class EvolucionAnualVictimasSerializer(serializers.Serializer):
    """Evolución anual: total de víctimas por año."""

    ano = serializers.IntegerField()
    total = serializers.IntegerField()
