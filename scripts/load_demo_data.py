#!/usr/bin/env python
"""
Script para cargar DATOS MASIVOS de prueba en la base de datos.
Genera siniestros y victimas realistas para visualizacion en el frontend.

Rango: 2020 a 2026
Volumen: ~4,000 por ano (Total ~28,000) para asegurar densidad en filtros.
Ubicacion: Loja, Ecuador (Lat: -4.007, Lon: -79.201)

Uso:
    python scripts/load_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from pathlib import Path
from random import randint, choice, uniform

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_backend.settings')
django.setup()

from django.utils import timezone
from siniestros.models import TipoSiniestro, Causa, Siniestro, Victima


def clear_data():
    """Elimina todos los datos existentes de la base de datos."""
    print("Limpiando datos existentes...")
    Victima.objects.all().delete()
    Siniestro.objects.all().delete()
    Causa.objects.all().delete()
    TipoSiniestro.objects.all().delete()
    print("Datos eliminados")


def create_base_data():
    """Crea los datos base (tipos de siniestro y causas probables)."""
    print("\nCreando tipos de siniestro...")
    tipos = [
        "Choque Vehicular", "Caida", "Accidente Laboral", "Atropellamiento",
        "Volcamiento", "Incendio", "Colision Multiple",
    ]
    
    tipo_objs = []
    for tipo_nombre in tipos:
        obj, created = TipoSiniestro.objects.get_or_create(
            nombre=tipo_nombre,
            defaults={'activo': True}
        )
        tipo_objs.append(obj)
    
    print("Creando causas probables...")
    causas = [
        "Exceso de velocidad", "Imprudencia del conductor", "Distraccion (celular/radio)",
        "Via resbaladiza o mojada", "Falla mecanica", "Visibilidad reducida",
        "Inobservancia de senales", "Estado de embriaguez", "Fatiga del conductor",
        "Mal estado de la via", "Equipo de seguridad deficiente", "Factores externos",
    ]
    
    causa_objs = []
    for causa_nombre in causas:
        obj, created = Causa.objects.get_or_create(
            nombre=causa_nombre,
            defaults={'activo': True}
        )
        causa_objs.append(obj)
    
    return tipo_objs, causa_objs


def create_siniestros(tipo_objs, causa_objs, records_per_year=4000):
    """
    Crea siniestros distribuidos desde 2020 hasta 2026.
    Para el ano actual, limita la fecha maxima a hoy.
    """
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    total_target = len(years) * records_per_year
    
    print(f"\nCreando {total_target:,} siniestros ({records_per_year}/ano)...")
    
    severidades = [
        Siniestro.Severidad.CON_FALLECIDOS,
        Siniestro.Severidad.CON_LESIONADOS,
        Siniestro.Severidad.SOLO_DANOS,
    ]
    
    vias = [
        "Av. Orillas del Zamora", "Av. Cuxibamba", "Av. 8 de Diciembre",
        "Av. Manuel Agustin Aguirre", "Av. Universitaria", "Av. Reinaldo Espinosa",
        "Av. Pio Jaramillo", "Av. Gran Colombia", "Av. Metropolitana",
        "Av. Rosa Hermosa", "Calle Bolivar", "Calle Miguel Riofrio",
        "Calle Ramon Borrero", "Calle 10 de Agosto", "Calle 18 de Noviembre",
        "Calle Sucre", "Calle Quito", "Calle Rocafuerte", "Calle Saraguro",
        "Via Loja - Zamora", "Via Loja - Catamayo", "Ruta 35",
        "Calle Montufar", "Calle Mercadillo", "Av. Isidro Ayora",
        "Calle Colon", "Calle Imbabura", "Calle Azogues",
    ]
    
    LOJA_LAT = -4.007
    LOJA_LON = -79.201
    LAT_VARIATION = 0.030
    LON_VARIATION = 0.030
    
    siniestros_batch = []
    count = 0

    for year in years:
        print(f"   Generando datos para el ano {year}...")
        
        start_date = datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
        end_date = datetime(year, 12, 31, 23, 59, tzinfo=timezone.get_current_timezone())
        
        if year == datetime.now().year:
            end_date = timezone.now()
            
        delta_seconds = int((end_date - start_date).total_seconds())

        for _ in range(records_per_year):
            random_second = randint(0, delta_seconds)
            fecha_hora = start_date + timedelta(seconds=random_second)
            
            siniestro = Siniestro(
                fecha_hora=fecha_hora,
                latitud=LOJA_LAT + uniform(-LAT_VARIATION, LAT_VARIATION),
                longitud=LOJA_LON + uniform(-LON_VARIATION, LON_VARIATION),
                via=choice(vias),
                grado_severidad=choice(severidades),
                tipo_siniestro=choice(tipo_objs),
                causa_probable=choice(causa_objs),
            )
            siniestros_batch.append(siniestro)
            count += 1
            
            if len(siniestros_batch) >= 2000:
                Siniestro.objects.bulk_create(siniestros_batch)
                siniestros_batch = []
                print(f"     -> Guardados {count} siniestros...")

    if siniestros_batch:
        Siniestro.objects.bulk_create(siniestros_batch)
        
    print(f"  Total creado: {Siniestro.objects.count():,} siniestros")
    return Siniestro.objects.all()


def create_victimas_bulk(total_siniestros):
    """
    Crea victimas en masa de manera eficiente.
    Asigna fallecidos y lesionados segun la severidad del siniestro.
    """
    print("\nCreando victimas (esto puede tardar un poco)...")
    
    siniestros_iterator = Siniestro.objects.values_list('id', 'grado_severidad').iterator(chunk_size=2000)
    
    victimas_batch = []
    total_victimas = 0
    
    for s_id, severidad in siniestros_iterator:
        fallecidos = 0
        lesionados = 0
        
        if severidad == Siniestro.Severidad.CON_FALLECIDOS:
            fallecidos = randint(1, 2)
            lesionados = randint(0, 2)
        elif severidad == Siniestro.Severidad.CON_LESIONADOS:
            lesionados = randint(1, 3)
        else:
            if randint(1, 10) == 1:
                lesionados = 1
        
        for _ in range(fallecidos):
            victimas_batch.append(Victima(
                siniestro_id=s_id,
                edad=randint(18, 85),
                condicion=Victima.Condicion.FALLECIDO,
                sexo=choice([Victima.Sexo.HOMBRE, Victima.Sexo.MUJER, Victima.Sexo.NO_REGISTRA]),
                actor_vial=choice(Victima.ActorVial.values)
            ))
            
        for _ in range(lesionados):
            victimas_batch.append(Victima(
                siniestro_id=s_id,
                edad=randint(5, 80),
                condicion=Victima.Condicion.LESIONADO,
                sexo=choice([Victima.Sexo.HOMBRE, Victima.Sexo.MUJER, Victima.Sexo.NO_REGISTRA]),
                actor_vial=choice(Victima.ActorVial.values)
            ))
            
        if len(victimas_batch) >= 3000:
            Victima.objects.bulk_create(victimas_batch)
            total_victimas += len(victimas_batch)
            print(f"     -> Guardadas {total_victimas} victimas...")
            victimas_batch = []
            
    if victimas_batch:
        Victima.objects.bulk_create(victimas_batch)
        total_victimas += len(victimas_batch)

    print(f"  Total creado: {total_victimas:,} victimas")


def print_summary():
    """Imprime un resumen de los datos cargados."""
    print("\n" + "=" * 60)
    print("RESUMEN DE DATOS CARGADOS (2020-2026)")
    print("=" * 60)
    
    print(f"Siniestros Totales: {Siniestro.objects.count():,}")
    print(f"Victimas Totales:   {Victima.objects.count():,}")
    print("=" * 60)


def main():
    """Funcion principal que orquesta la carga de datos."""
    print("Iniciando carga masiva de datos (2020-2026)...\n")
    try:
        response = input("Borrar datos anteriores? (s/n): ").lower().strip()
        if response == 's':
            clear_data()
        
        tipo_objs, causa_objs = create_base_data()
        
        create_siniestros(tipo_objs, causa_objs, records_per_year=4000)
        
        create_victimas_bulk(None)
        
        print_summary()
        print("\nProceso finalizado! Ahora tienes datos densos para todos los anos.")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()