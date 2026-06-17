"""Pruebas de la lógica de agregación estadística (managers/QuerySets)."""

from datetime import datetime

import pytest
from django.utils import timezone

from siniestros.models import Siniestro, Victima

pytestmark = pytest.mark.django_db


@pytest.fixture
def siniestros_un_mes(db, causa, tipo):
    """Tres siniestros en marzo de 2023 a las 08:00 hora local (America/Guayaquil).

    Se usan datetimes tz-aware en la zona del proyecto (no UTC) para que las
    extracciones de mes/hora sean deterministas. Al estar todos en el mismo
    año-mes evitan el solapamiento que ``_fill_monthly`` produce entre años.
    """
    for dia in (10, 15, 20):
        Siniestro.objects.create(
            fecha_hora=timezone.make_aware(datetime(2023, 3, dia, 8, 0)),
            latitud=-4.0, longitud=-79.2, via="Av. de prueba",
            grado_severidad=Siniestro.Severidad.SOLO_DANOS,
            causa_probable=causa, tipo_siniestro=tipo,
        )


def test_kpi_stats_suma_heridos_y_fallecidos(siniestros):
    assert Siniestro.objects.get_kpi_stats() == {
        "total_siniestros": 2,
        "total_lesionados": 5,
        "total_fallecidos": 1,
    }


def test_kpi_stats_sin_datos_devuelve_ceros(db):
    assert Siniestro.objects.get_kpi_stats() == {
        "total_siniestros": 0,
        "total_lesionados": 0,
        "total_fallecidos": 0,
    }


def test_por_mes_siempre_devuelve_12_entradas(siniestros_un_mes):
    data = Siniestro.objects.get_por_mes()
    assert len(data) == 12
    assert [d["mes"] for d in data] == list(range(1, 13))
    marzo = next(d for d in data if d["mes"] == 3)
    assert marzo["total"] == 3
    assert sum(d["total"] for d in data) == 3  # el resto de meses se rellenan con 0


def test_por_hora_siempre_devuelve_24_entradas(siniestros_un_mes):
    data = Siniestro.objects.get_por_hora()
    assert len(data) == 24
    assert sum(d["total"] for d in data) == 3
    franja_8 = next(d for d in data if d["rango_hora"].startswith("08"))
    assert franja_8["total"] == 3  # 08:00 hora local del proyecto


def test_por_severidad_agrupa_con_label(siniestros):
    por_codigo = {d["codigo"]: d for d in Siniestro.objects.get_por_severidad()}
    assert por_codigo["CON_FALLECIDOS"]["total"] == 1
    assert por_codigo["CON_FALLECIDOS"]["label"] == "Con fallecidos en sitio"
    assert por_codigo["CON_LESIONADOS"]["total"] == 1


def test_por_dia_hora_devuelve_matriz_7x24(siniestros):
    data = Siniestro.objects.get_por_dia_hora()
    assert len(data) == 7 * 24
    assert sum(d["total"] for d in data) == 2


def test_evolucion_anual_por_ano(siniestros):
    por_ano = {d["ano"]: d for d in Siniestro.objects.get_evolucion_anual()}
    assert por_ano[2022]["total_siniestros"] == 1
    assert por_ano[2022]["total_fallecidos"] == 1
    assert por_ano[2023]["total_siniestros"] == 1
    assert por_ano[2023]["total_lesionados"] == 3


def test_por_via_incluye_conteos_de_victimas(siniestros):
    via = next(d for d in Siniestro.objects.get_por_via() if d["via"] == "Av. Pío Jaramillo")
    assert via["total_siniestros"] == 2
    assert via["total_lesionados"] == 5
    assert via["total_fallecidos"] == 1


def test_por_causa_probable_cuenta_victimas_por_condicion(siniestros):
    causa = next(
        d for d in Siniestro.objects.get_por_causa_probable()
        if d["causa"] == "Exceso de velocidad"
    )
    assert causa["total_siniestros"] == 2
    assert causa["total_lesionados"] == 2  # 1 lesionado en s1 + 1 en s2
    assert causa["total_fallecidos"] == 1


def test_victimas_por_actor_vial(siniestros):
    por_actor = {d["actor_vial"]: d for d in Victima.objects.get_por_actor_vial()}
    assert por_actor["PEATON"]["total"] == 1
    assert por_actor["MOTOCICLETA"]["label"] == "Ocupante Motocicleta"
    assert por_actor["CICLISTA"]["total"] == 1


def test_victimas_por_sexo(siniestros):
    por_sexo = {d["sexo"]: d["total"] for d in Victima.objects.get_por_sexo()}
    assert por_sexo["HOMBRE"] == 2
    assert por_sexo["MUJER"] == 1


def test_victimas_por_edad_sexo(siniestros):
    data = Victima.objects.get_por_edad_sexo()
    fila = next(d for d in data if d["rango_edad"] == "30-39" and d["sexo"] == "HOMBRE")
    assert fila["total"] == 1
    assert fila["sexo_label"] == "Hombre"
