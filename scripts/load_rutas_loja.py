#!/usr/bin/env python
"""
Script para cargar líneas de bus de Loja con datos realistas.
10 líneas de bus con rutas GeoJSON, origen, destino y tarifas.

Ubicación: Loja, Ecuador
Centro: Lat: -3.9932, Lon: -79.2044

Uso:
    python scripts/load_rutas_loja.py
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_backend.settings')
django.setup()

from transporte.models import LineaBus


def clear_lineas():
    """Elimina todas las líneas existentes."""
    print("🗑️  Limpiando líneas de bus existentes...")
    LineaBus.objects.all().delete()
    print("✓ Líneas eliminadas")


def create_lineas_loja():
    """Crea 10 líneas de bus para Loja."""
    print("\n🚌 Creando líneas de bus para Loja...")
    
    # Centro de Loja: -3.9932, -79.2044
    # Coordenadas aproximadas de puntos importantes en Loja
    
    lineas_data = [
        {
            'nombre': 'L1 - Centro',
            'color': '#FF0000',
            'origen': 'Terminal Terrestre',
            'destino': 'Centro Histórico',
            'descripcion': 'Ruta principal del centro histórico de Loja',
            'tarifa_base': Decimal('0.50'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2050, -3.9950],
                    [-79.2040, -3.9920],
                    [-79.2030, -3.9900],
                    [-79.2020, -3.9880],
                ]
            }
        },
        {
            'nombre': 'L2 - Sauces',
            'color': '#0000FF',
            'origen': 'Terminal Terrestre',
            'destino': 'Barrio Sauces',
            'descripcion': 'Ruta hacia el barrio residencial de Sauces',
            'tarifa_base': Decimal('0.60'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2050, -3.9950],
                    [-79.2100, -3.9950],
                    [-79.2150, -3.9930],
                    [-79.2180, -3.9900],
                ]
            }
        },
        {
            'nombre': 'L3 - Perpetuo Socorro',
            'color': '#00FF00',
            'origen': 'Centro',
            'destino': 'Perpetuo Socorro',
            'descripcion': 'Ruta hacia el barrio Perpetuo Socorro',
            'tarifa_base': Decimal('0.50'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.1990, -3.9920],
                    [-79.1950, -3.9930],
                    [-79.1920, -3.9950],
                ]
            }
        },
        {
            'nombre': 'L4 - Universitaria',
            'color': '#FFFF00',
            'origen': 'Centro',
            'destino': 'Universidad Técnica Particular',
            'descripcion': 'Ruta a la universidad técnica',
            'tarifa_base': Decimal('0.70'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.2050, -3.9850],
                    [-79.2070, -3.9800],
                    [-79.2100, -3.9750],
                ]
            }
        },
        {
            'nombre': 'L5 - Cariamanga',
            'color': '#FF00FF',
            'origen': 'Terminal Terrestre',
            'destino': 'Cariamanga',
            'descripcion': 'Ruta hacia Cariamanga y alrededores',
            'tarifa_base': Decimal('1.00'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2050, -3.9950],
                    [-79.2200, -3.9800],
                    [-79.2300, -3.9700],
                    [-79.2400, -3.9600],
                ]
            }
        },
        {
            'nombre': 'L6 - San Cayetano',
            'color': '#00FFFF',
            'origen': 'Centro',
            'destino': 'San Cayetano',
            'descripcion': 'Ruta al barrio San Cayetano',
            'tarifa_base': Decimal('0.60'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.1900, -3.9900],
                    [-79.1800, -3.9880],
                    [-79.1700, -3.9870],
                ]
            }
        },
        {
            'nombre': 'L7 - Jipijapa',
            'color': '#FFA500',
            'origen': 'Terminal Terrestre',
            'destino': 'Jipijapa',
            'descripcion': 'Ruta hacia Jipijapa',
            'tarifa_base': Decimal('0.80'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2050, -3.9950],
                    [-79.2150, -4.0050],
                    [-79.2200, -4.0100],
                    [-79.2250, -4.0150],
                ]
            }
        },
        {
            'nombre': 'L8 - Argelia',
            'color': '#800080',
            'origen': 'Centro',
            'destino': 'Barrio Argelia',
            'descripcion': 'Ruta al barrio residencial Argelia',
            'tarifa_base': Decimal('0.50'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.2100, -3.9850],
                    [-79.2150, -3.9800],
                    [-79.2200, -3.9750],
                ]
            }
        },
        {
            'nombre': 'L9 - Motupe',
            'color': '#FFC0CB',
            'origen': 'Terminal Terrestre',
            'destino': 'Motupe',
            'descripcion': 'Ruta hacia el sector de Motupe',
            'tarifa_base': Decimal('0.65'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2050, -3.9950],
                    [-79.1900, -4.0050],
                    [-79.1850, -4.0100],
                    [-79.1800, -4.0150],
                ]
            }
        },
        {
            'nombre': 'L10 - Zamora',
            'color': '#A52A2A',
            'origen': 'Centro',
            'destino': 'Zamora',
            'descripcion': 'Ruta hacia Zamora (conexión regional)',
            'tarifa_base': Decimal('2.50'),
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.2300, -4.0300],
                    [-79.2500, -4.0600],
                    [-79.2700, -4.0900],
                ]
            }
        },
    ]
    
    created_count = 0
    for linea_data in lineas_data:
        linea, created = LineaBus.objects.get_or_create(
            nombre=linea_data['nombre'],
            defaults={
                'color': linea_data['color'],
                'origen': linea_data['origen'],
                'destino': linea_data['destino'],
                'descripcion': linea_data['descripcion'],
                'tarifa_base': linea_data['tarifa_base'],
                'geom': linea_data['geom'],
                'activo': True,
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Creada: {linea.nombre} ({linea.origen} → {linea.destino}) - ${linea.tarifa_base}")
        else:
            print(f"⊘ Ya existe: {linea.nombre}")
    
    print(f"\n✅ Total creadas: {created_count} líneas")
    return created_count


def main():
    """Función principal."""
    print("=" * 60)
    print("📍 Cargador de Rutas de Bus - Loja")
    print("=" * 60)
    
    try:
        clear_lineas()
        create_lineas_loja()
        print("\n✅ ¡Script completado exitosamente!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
