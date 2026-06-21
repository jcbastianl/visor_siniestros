"""Pruebas de serializers de siniestros y víctimas."""

import pytest

from siniestros.models import Siniestro
from siniestros.serializers import SiniestroSerializer, VictimaSerializer

pytestmark = pytest.mark.django_db


def test_siniestro_serializer_incluye_labels_y_relaciones_anidadas(siniestros):
    instancia = Siniestro.objects.get(pk=siniestros[0].pk)
    data = SiniestroSerializer(instancia).data

    assert data["severidad_label"] == "Con fallecidos en sitio"
    assert data["causa_probable"]["nombre"] == "Exceso de velocidad"
    assert data["tipo_siniestro"]["nombre"] == "Choque lateral"
    assert len(data["victimas"]) == 2
    assert {"condicion_label", "sexo_label", "actor_vial_label"} <= set(data["victimas"][0])


def test_victima_serializer_expone_labels_legibles(siniestros):
    victima = siniestros[0].victimas.get(condicion="FALLECIDO")
    data = VictimaSerializer(victima).data

    assert data["condicion_label"] == "Fallecido"
    assert data["actor_vial_label"] == "Peatón"
    assert data["sexo_label"] == "Hombre"
