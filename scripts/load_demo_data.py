#!/usr/bin/env python
"""
Script para cargar muchos datos de prueba en la base de datos.
Genera siniestros y víctimas realistas para visualización en el frontend.

Los datos están centrados en Loja, Ecuador (Latitud: -4.007, Longitud: -79.201)
con nombres de vías reales de la ciudad.

Uso:
    python scripts/load_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from pathlib import Path
from random import randint, choice, uniform

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_backend.settings')
django.setup()

from django.utils import timezone
from siniestros.models import TipoSiniestro, Causa, Siniestro, Victima


def clear_data():
    """Elimina todos los datos existentes (opcional)."""
    print("🗑️  Limpiando datos existentes...")
    Victima.objects.all().delete()
    Siniestro.objects.all().delete()
    Causa.objects.all().delete()
    TipoSiniestro.objects.all().delete()
    print("✓ Datos eliminados")


def create_base_data():
    """Crea los datos base (tipos y causas)."""
    print("\n📋 Creando tipos de siniestro...")
    tipos = [
        "Choque Vehicular",
        "Caída",
        "Accidente Laboral",
        "Atropellamiento",
        "Volcamiento",
        "Incendio",
        "Colisión Múltiple",
    ]
    
    tipo_objs = []
    for tipo_nombre in tipos:
        obj, created = TipoSiniestro.objects.get_or_create(
            nombre=tipo_nombre,
            defaults={'activo': True}
        )
        tipo_objs.append(obj)
        status = "✓" if created else "∃"
        print(f"  {status} {tipo_nombre}")
    
    print("\n📋 Creando causas probables...")
    causas = [
        "Exceso de velocidad",
        "Imprudencia del conductor",
        "Distracción (celular/radio)",
        "Vía resbaladiza o mojada",
        "Falla mecánica",
        "Visibilidad reducida",
        "Inobservancia de señales",
        "Estado de embriaguez",
        "Fatiga del conductor",
        "Mal estado de la vía",
        "Equipo de seguridad deficiente",
        "Factores externos",
    ]
    
    causa_objs = []
    for causa_nombre in causas:
        obj, created = Causa.objects.get_or_create(
            nombre=causa_nombre,
            defaults={'activo': True}
        )
        causa_objs.append(obj)
        status = "✓" if created else "∃"
        print(f"  {status} {causa_nombre}")
    
    return tipo_objs, causa_objs


def create_siniestros(tipo_objs, causa_objs, num_siniestros=500):
    """Crea siniestros distribuidos en los últimos 2 años."""
    print(f"\n🚗 Creando {num_siniestros} siniestros...")
    
    severidades = [
        Siniestro.Severidad.CON_FALLECIDOS,
        Siniestro.Severidad.CON_LESIONADOS,
        Siniestro.Severidad.SOLO_DANOS,
    ]
    
    # 🗺️  Vías principales y reales de Loja, Ecuador
    vias = [
        # Avenidas principales
        "Av. Orillas del Zamora",
        "Av. Cuxibamba",
        "Av. 8 de Diciembre",
        "Av. Manuel Agustín Aguirre",
        "Av. Universitaria",
        "Av. Reinaldo Espinosa",
        "Av. Pio Jaramillo",
        "Av. Gran Colombia",
        "Av. Metropolitana",
        "Av. Rosa Hermosa",
        
        # Calles principales del centro
        "Calle Bolívar",
        "Calle Miguel Riofrío",
        "Calle Ramón Borrero",
        "Calle 10 de Agosto",
        "Calle 18 de Noviembre",
        "Calle Sucre",
        "Calle Quito",
        "Calle Rocafuerte",
        "Calle Saraguro",
        
        # Otras vías importantes
        "Vía Loja - Zamora",
        "Vía Loja - Catamayo",
        "Ruta 35",
        "Ruta 37",
        "Calle Montúfar",
        "Calle Mercadillo",
        "Av. Isidro Ayora",
        "Calle Colón",
        "Calle Imbabura",
        "Calle Azogues",
    ]
    
    siniestros = []
    start_date = timezone.now() - timedelta(days=730)  # 2 años atrás
    
    # Centro de Loja, Ecuador (Latitud: -4.007, Longitud: -79.201)
    LOJA_LAT = -4.007
    LOJA_LON = -79.201
    
    # Variación aleatoria para dispersar los siniestros en el área urbana
    # ~0.03 grados ≈ 3.3 km (radio de cobertura aproximado)
    LAT_VARIATION = 0.025
    LON_VARIATION = 0.025
    
    for i in range(num_siniestros):
        # Distribuir aleatoriamente en el tiempo
        random_days = randint(0, 729)
        fecha_hora = start_date + timedelta(
            days=random_days,
            hours=randint(0, 23),
            minutes=randint(0, 59)
        )
        
        siniestro = Siniestro(
            fecha_hora=fecha_hora,
            # Coordenadas centradas en Loja con variación aleatoria
            latitud=LOJA_LAT + uniform(-LAT_VARIATION, LAT_VARIATION),
            longitud=LOJA_LON + uniform(-LON_VARIATION, LON_VARIATION),
            via=choice(vias),
            grado_severidad=choice(severidades),
            tipo_siniestro=choice(tipo_objs),
            causa_probable=choice(causa_objs),
        )
        siniestros.append(siniestro)
    
    # Bulk create para velocidad
    Siniestro.objects.bulk_create(siniestros, batch_size=100)
    print(f"  ✓ {num_siniestros} siniestros creados")
    
    return Siniestro.objects.all()


def create_victimas(siniestros):
    """Crea víctimas para los siniestros."""
    print("\n👥 Creando víctimas...")
    
    victimas = []
    victima_count = 0
    
    for siniestro in siniestros:
        # Algunas estadísticas realistas
        severidad = siniestro.grado_severidad
        
        if severidad == Siniestro.Severidad.CON_FALLECIDOS:
            # 1-3 víctimas, mayormente fallecidos
            num_victimas = randint(1, 3)
            fallecidos = randint(1, num_victimas)
            lesionados = max(0, num_victimas - fallecidos)
        elif severidad == Siniestro.Severidad.CON_LESIONADOS:
            # 1-4 víctimas, mayormente lesionados
            num_victimas = randint(1, 4)
            lesionados = randint(1, num_victimas)
            fallecidos = 0
        else:  # SOLO_DANOS
            # 0-2 víctimas
            num_victimas = randint(0, 2)
            lesionados = num_victimas
            fallecidos = 0
        
        # Crear fallecidos
        for _ in range(fallecidos):
            victima = Victima(
                siniestro=siniestro,
                edad=randint(18, 85),
                condicion=Victima.Condicion.FALLECIDO,
                sexo=choice([Victima.Sexo.HOMBRE, Victima.Sexo.MUJER, Victima.Sexo.NO_REGISTRA]),
                actor_vial=choice([
                    Victima.ActorVial.PEATON,
                    Victima.ActorVial.MOTOCICLETA,
                    Victima.ActorVial.VEH_LIVIANO,
                    Victima.ActorVial.CICLISTA,
                ])
            )
            victimas.append(victima)
            victima_count += 1
        
        # Crear lesionados
        for _ in range(lesionados):
            victima = Victima(
                siniestro=siniestro,
                edad=randint(5, 80),
                condicion=Victima.Condicion.LESIONADO,
                sexo=choice([Victima.Sexo.HOMBRE, Victima.Sexo.MUJER, Victima.Sexo.NO_REGISTRA]),
                actor_vial=choice([
                    Victima.ActorVial.PEATON,
                    Victima.ActorVial.MOTOCICLETA,
                    Victima.ActorVial.VEH_LIVIANO,
                    Victima.ActorVial.CICLISTA,
                    Victima.ActorVial.SCOOTER,
                    Victima.ActorVial.OTRO,
                ])
            )
            victimas.append(victima)
            victima_count += 1
    
    # Bulk create
    if victimas:
        Victima.objects.bulk_create(victimas, batch_size=100)
        print(f"  ✓ {victima_count} víctimas creadas")
    else:
        print("  ✓ Sin víctimas (todos SOLO_DANOS)")


def print_summary():
    """Imprime un resumen de los datos cargados."""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DATOS CARGADOS")
    print("=" * 60)
    
    total_siniestros = Siniestro.objects.count()
    total_victimas = Victima.objects.count()
    total_fallecidos = Victima.objects.filter(condicion=Victima.Condicion.FALLECIDO).count()
    total_lesionados = Victima.objects.filter(condicion=Victima.Condicion.LESIONADO).count()
    
    print(f"✓ Siniestros:        {total_siniestros:>6}")
    print(f"✓ Víctimas totales:  {total_victimas:>6}")
    print(f"  - Fallecidos:      {total_fallecidos:>6}")
    print(f"  - Lesionados:      {total_lesionados:>6}")
    print(f"✓ Tipos siniestro:   {TipoSiniestro.objects.count():>6}")
    print(f"✓ Causas probables:  {Causa.objects.count():>6}")
    print("=" * 60)


def main():
    """Función principal."""
    print("🚀 Iniciando carga de datos de prueba...\n")
    
    try:
        # Preguntar si limpiar datos existentes
        response = input("¿Deseas limpiar los datos existentes? (s/n): ").lower().strip()
        if response == 's':
            clear_data()
        
        # Crear datos base
        tipo_objs, causa_objs = create_base_data()
        
        # Crear siniestros
        siniestros = create_siniestros(tipo_objs, causa_objs, num_siniestros=500)
        
        # Crear víctimas
        create_victimas(siniestros)
        
        # Mostrar resumen
        print_summary()
        
        print("\n✨ ¡Datos cargados exitosamente!")
        print("Ahora puedes acceder a http://localhost:5173 para visualizar los datos")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
