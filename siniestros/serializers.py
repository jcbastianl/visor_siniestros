from rest_framework import serializers
from .models import Causa, Siniestro, TipoSiniestro, Victima


class CausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Causa
        fields = ['id', 'nombre', 'activo']


class TipoSiniestroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSiniestro
        fields = ['id', 'nombre', 'activo']


class VictimaSerializer(serializers.ModelSerializer):
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


# --- Serializers de estadísticas ---

class KPIStatsSerializer(serializers.Serializer):
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class MonthlyStatSerializer(serializers.Serializer):
    mes = serializers.IntegerField()
    total = serializers.IntegerField()


class HourlyStatSerializer(serializers.Serializer):
    rango_hora = serializers.CharField()
    total = serializers.IntegerField()


class DayHourStatSerializer(serializers.Serializer):
    dia_semana = serializers.IntegerField()
    hora_dia = serializers.IntegerField()
    total = serializers.IntegerField()


class SeveridadStatSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class SexoStatSerializer(serializers.Serializer):
    sexo = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class ActorVialStatSerializer(serializers.Serializer):
    actor_vial = serializers.CharField()
    label = serializers.CharField()
    total = serializers.IntegerField()


class EdadSexoRangeSerializer(serializers.Serializer):
    rango_edad = serializers.CharField()
    sexo = serializers.CharField()
    sexo_label = serializers.CharField()
    total = serializers.IntegerField()


class ViaStatSerializer(serializers.Serializer):
    via = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class CausaProbableStatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    causa = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class TipoSiniestroStatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class EvolucionAnualSiniestrosSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()


class EvolucionAnualVictimasSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    total = serializers.IntegerField()
