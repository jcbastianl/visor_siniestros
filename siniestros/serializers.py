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
            'id',
            'edad',
            'condicion',
            'condicion_label',
            'sexo',
            'sexo_label',
            'actor_vial',
            'actor_vial_label',
        ]


class SiniestroSerializer(serializers.ModelSerializer):
    tipo_siniestro = TipoSiniestroSerializer(read_only=True)
    causa_probable = CausaSerializer(read_only=True)
    victimas = VictimaSerializer(many=True, read_only=True)
    severidad_label = serializers.CharField(source='get_grado_severidad_display', read_only=True)

    class Meta:
        model = Siniestro
        fields = [
            'id',
            'fecha_hora',
            'latitud',
            'longitud',
            'via',
            'grado_severidad',
            'severidad_label',
            'tipo_siniestro',
            'causa_probable',
            'victimas',
        ]