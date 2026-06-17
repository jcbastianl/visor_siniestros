"""Fixtures compartidas para las pruebas de la app ``siniestros``.

Las fechas se crean en UTC explícito para que las extracciones de mes/hora/día
(TruncMonth, ExtractHour, ExtractWeekDay) sean deterministas independientemente de
la zona horaria del proyecto.
"""

from datetime import datetime, timezone as dt_timezone

import pytest

from siniestros.models import Causa, Siniestro, TipoSiniestro, Victima


@pytest.fixture
def causa(db):
    return Causa.objects.create(nombre="Exceso de velocidad")


@pytest.fixture
def causa_inactiva(db):
    return Causa.objects.create(nombre="Causa dada de baja", activo=False)


@pytest.fixture
def tipo(db):
    return TipoSiniestro.objects.create(nombre="Choque lateral")


@pytest.fixture
def siniestros(db, causa, tipo):
    """Dos siniestros (2022 y 2023) en marzo a las 08:00 UTC, con 3 víctimas en total."""
    s1 = Siniestro.objects.create(
        fecha_hora=datetime(2022, 3, 15, 8, 0, tzinfo=dt_timezone.utc),
        latitud=-3.99, longitud=-79.20, via="Av. Pío Jaramillo",
        grado_severidad=Siniestro.Severidad.CON_FALLECIDOS,
        causa_probable=causa, tipo_siniestro=tipo,
        num_heridos=2, num_fallecidos=1,
    )
    s2 = Siniestro.objects.create(
        fecha_hora=datetime(2023, 3, 20, 8, 0, tzinfo=dt_timezone.utc),
        latitud=-4.00, longitud=-79.21, via="Av. Pío Jaramillo",
        grado_severidad=Siniestro.Severidad.CON_LESIONADOS,
        causa_probable=causa, tipo_siniestro=tipo,
        num_heridos=3, num_fallecidos=0,
    )
    Victima.objects.create(
        siniestro=s1, edad=30, condicion=Victima.Condicion.FALLECIDO,
        sexo=Victima.Sexo.HOMBRE, actor_vial=Victima.ActorVial.PEATON,
    )
    Victima.objects.create(
        siniestro=s1, edad=25, condicion=Victima.Condicion.LESIONADO,
        sexo=Victima.Sexo.MUJER, actor_vial=Victima.ActorVial.MOTOCICLETA,
    )
    Victima.objects.create(
        siniestro=s2, edad=40, condicion=Victima.Condicion.LESIONADO,
        sexo=Victima.Sexo.HOMBRE, actor_vial=Victima.ActorVial.CICLISTA,
    )
    return [s1, s2]
