"""Pruebas de los endpoints de la API de siniestros (DRF APIClient)."""

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_kpi_stats_endpoint(api_client, siniestros):
    resp = api_client.get("/api/siniestros/kpi_stats/")
    assert resp.status_code == 200
    assert resp.data["total_siniestros"] == 2
    assert resp.data["total_fallecidos"] == 1
    assert resp.data["total_lesionados"] == 5


def test_map_data_devuelve_lista_ligera(api_client, siniestros):
    resp = api_client.get("/api/siniestros/map_data/")
    assert resp.status_code == 200
    assert isinstance(resp.data, list)
    assert len(resp.data) == 2
    assert {"id", "latitud", "longitud", "grado_severidad"} <= set(resp.data[0])


def test_catalogo_causas_solo_devuelve_activas(api_client, causa, causa_inactiva):
    resp = api_client.get("/api/causas/")
    assert resp.status_code == 200
    nombres = [c["nombre"] for c in resp.data]
    assert "Exceso de velocidad" in nombres
    assert "Causa dada de baja" not in nombres


def test_filtros_disponibles_estructura(api_client, siniestros):
    resp = api_client.get("/api/siniestros/filtros_disponibles/")
    assert resp.status_code == 200
    assert {"causas", "tipos_siniestro", "dias_semana", "horas"} <= set(resp.data)
    assert any(c["nombre"] == "Exceso de velocidad" for c in resp.data["causas"])


def _items(resp):
    """Devuelve los items tanto si la respuesta está paginada como si es lista."""
    data = resp.data
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


def test_filtro_victimas_por_sexo_mujer(api_client, siniestros):
    """Regresión bug choices: filtrar por sexo=MUJER (valor real del modelo) debe
    devolver la víctima MUJER. Con SEXO_CHOICES=M/F/O el filtro nunca coincidía."""
    resp = api_client.get("/api/victimas/?sexo=MUJER")
    assert resp.status_code == 200
    items = _items(resp)
    assert len(items) == 1
    assert all(v["sexo"] == "MUJER" for v in items)


def test_filtro_victimas_por_actor_vial_peaton(api_client, siniestros):
    """Regresión bug choices: filtrar por actor_vial=PEATON (valor real del modelo)
    debe devolver la víctima peatón. ACTOR_VIAL_CHOICES no incluía PEATON."""
    resp = api_client.get("/api/victimas/?actor_vial=PEATON")
    assert resp.status_code == 200
    items = _items(resp)
    assert len(items) == 1
    assert all(v["actor_vial"] == "PEATON" for v in items)
