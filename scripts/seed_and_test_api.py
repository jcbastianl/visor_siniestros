#!/usr/bin/env python
"""Populate demo data and exercise the public API endpoints.

Usage examples
--------------

Seed data and hit the endpoints without running the devserver (uses Django's
internal test client)::

    python scripts/seed_and_test_api.py --year 2024

Seed data and test against a live server (for example the one you started with
``python manage.py runserver 8002``)::

    python scripts/seed_and_test_api.py --base-url http://127.0.0.1:8002 --year 2024

The script can safely be re-run; it updates or creates the demo objects each
time so duplicates will not accumulate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import django
from django.test import Client
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_backend.settings')
django.setup()

from siniestros.models import Causa, Siniestro, TipoSiniestro, Victima  # noqa: E402


def seed_demo_data(year: int) -> None:
    """Create or update a minimal dataset that exercises every endpoint."""

    tipo, _ = TipoSiniestro.objects.update_or_create(
        nombre='Colisión Demo',
        defaults={'activo': True},
    )

    causa, _ = Causa.objects.update_or_create(
        nombre='Exceso de velocidad (demo)',
        defaults={'activo': True},
    )

    # Use a fixed day within the requested year so analytics endpoints line up.
    fecha_referencia = timezone.make_aware(
        datetime(year, 6, 15, 8, 30), timezone.get_current_timezone()
    )

    siniestro, _ = Siniestro.objects.update_or_create(
        fecha_hora=fecha_referencia,
        defaults={
            'latitud': -3.9937,
            'longitud': -79.2059,
            'via': 'Av. Demo',
            'grado_severidad': Siniestro.Severidad.CON_LESIONADOS,
            'tipo_siniestro': tipo,
            'causa_probable': causa,
        },
    )

    Victima.objects.update_or_create(
        siniestro=siniestro,
        condicion=Victima.Condicion.LESIONADO,
        sexo=Victima.Sexo.HOMBRE,
        defaults={
            'edad': 32,
            'actor_vial': Victima.ActorVial.MOTOCICLETA,
        },
    )

    Victima.objects.update_or_create(
        siniestro=siniestro,
        condicion=Victima.Condicion.FALLECIDO,
        sexo=Victima.Sexo.MUJER,
        defaults={
            'edad': 45,
            'actor_vial': Victima.ActorVial.PEATON,
        },
    )

    # Add a second siniestro a week later to avoid all-zero hourly buckets.
    fecha_secundaria = fecha_referencia + timedelta(days=7, hours=5)
    siniestro_secundario, _ = Siniestro.objects.update_or_create(
        fecha_hora=fecha_secundaria,
        defaults={
            'latitud': -3.995,
            'longitud': -79.202,
            'via': 'Calle Secundaria',
            'grado_severidad': Siniestro.Severidad.SOLO_DANOS,
            'tipo_siniestro': tipo,
            'causa_probable': causa,
        },
    )

    Victima.objects.update_or_create(
        siniestro=siniestro_secundario,
        condicion=Victima.Condicion.ILESO,
        sexo=Victima.Sexo.HOMBRE,
        defaults={
            'edad': 28,
            'actor_vial': Victima.ActorVial.VEH_LIVIANO,
        },
    )


def make_payload_summary(payload: Any) -> str:
    """Return a compact JSON string for logging purposes."""
    return json.dumps(payload, ensure_ascii=False, indent=2)[:400]


def run_with_test_client(year: int) -> None:
    client = Client()
    endpoints: Iterable[Tuple[str, Dict]] = [
        ('/api/siniestros/', {}),
        ('/api/causas/', {}),
        ('/api/tipos-siniestro/', {}),
        ('/api/stats/kpis/', {}),
        ('/api/stats/por-mes/', {'year': year}),
        ('/api/stats/por-severidad/', {}),
        ('/api/stats/por-hora/', {'year': year}),
        ('/api/stats/por-dia-hora/', {'year': year}),
        ('/api/stats/victimas/por-sexo/', {'year': year}),
        ('/api/stats/victimas/por-actor-vial/', {'year': year}),
        ('/api/stats/victimas/por-edad-sexo/', {'year': year}),
        ('/api/stats/victimas/por-mes/', {'year': year}),
        ('/api/stats/victimas/por-hora/', {'year': year}),
        ('/api/stats/victimas/por-dia-hora/', {'year': year}),
    ]

    for path, params in endpoints:
        response = client.get(path, params)
        print(f"[internal] GET {path} -> {response.status_code}")
        print(make_payload_summary(response.json()))
        print('-' * 40)


def run_against_http(base_url: str, year: int) -> None:
    import urllib.parse
    import urllib.request

    base = base_url.rstrip('/')
    endpoints = [
        ('/api/siniestros/', {}),
        ('/api/causas/', {}),
        ('/api/tipos-siniestro/', {}),
        ('/api/stats/kpis/', {}),
        ('/api/stats/por-mes/', {'year': year}),
        ('/api/stats/por-severidad/', {}),
        ('/api/stats/por-hora/', {'year': year}),
        ('/api/stats/por-dia-hora/', {'year': year}),
        ('/api/stats/victimas/por-sexo/', {'year': year}),
        ('/api/stats/victimas/por-actor-vial/', {'year': year}),
        ('/api/stats/victimas/por-edad-sexo/', {'year': year}),
        ('/api/stats/victimas/por-mes/', {'year': year}),
        ('/api/stats/victimas/por-hora/', {'year': year}),
        ('/api/stats/victimas/por-dia-hora/', {'year': year}),
    ]

    for path, params in endpoints:
        url = f"{base}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url) as response:
            body = response.read().decode('utf-8')
            print(f"[http] GET {url} -> {response.status} at {response.url}")
            print(body[:400])
            print('-' * 40)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=timezone.now().year,
                        help='Año para los filtros de los endpoints (por defecto, año actual).')
    parser.add_argument('--base-url', type=str, default='',
                        help='Si se indica, las pruebas se harán contra ese servidor HTTP.')
    args = parser.parse_args()

    seed_demo_data(args.year)

    if args.base_url:
        run_against_http(args.base_url, args.year)
    else:
        run_with_test_client(args.year)


if __name__ == '__main__':
    main()
