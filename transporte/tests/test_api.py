"""Pruebas de los endpoints de transporte (líneas de bus y ciclovías)."""

import pytest
from rest_framework.test import APIClient

from transporte.models import Ciclovia, LineaBus

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_lineas_solo_devuelve_activas(api_client):
    LineaBus.objects.create(nombre="L1", color="#FF0000", origen="Norte", destino="Sur")
    LineaBus.objects.create(nombre="L2-baja", color="#00FF00", activo=False)

    resp = api_client.get("/api/lineas/")
    assert resp.status_code == 200
    nombres = [linea["nombre"] for linea in resp.data]
    assert nombres == ["L1"]


def test_ciclovia_serializer_expone_campos_clave(api_client):
    Ciclovia.objects.create(
        nombre="Ciclovía Centro", longitud_km="2.50", tipo_separacion="Confinada",
    )
    resp = api_client.get("/api/ciclovias/")
    assert resp.status_code == 200
    cv = resp.data[0]
    assert cv["nombre"] == "Ciclovía Centro"
    assert cv["tipo_separacion"] == "Confinada"
    assert str(cv["longitud_km"]) == "2.50"
    assert "geom" in cv
