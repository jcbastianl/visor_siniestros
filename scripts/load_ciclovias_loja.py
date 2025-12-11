#!/usr/bin/env python
"""
Script para cargar ciclovías de Loja con datos realistas.
Carga 8 ciclovías con rutas GeoJSON, longitudes y tipos de separación.

Ubicación: Loja, Ecuador
Centro: Lat: -3.9932, Lon: -79.2044

Uso:
    python scripts/load_ciclovias_loja.py
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

from transporte.models import Ciclovia


def clear_ciclovias():
    """Elimina todas las ciclovías existentes."""
    print("🗑️  Limpiando ciclovías existentes...")
    Ciclovia.objects.all().delete()
    print("✓ Ciclovías eliminadas")


def create_ciclovias_loja():
    """Crea 8 ciclovías para Loja."""
    print("\n🚴 Creando ciclovías para Loja...")
    
    # Centro de Loja: -3.9932, -79.2044
    # Coordenadas aproximadas de ciclovías en Loja
    
    ciclovias_data = [
        {
            'nombre': 'Ciclovía Avenida Universidad',
            'color': '#FF6B6B',
            'longitud_km': Decimal('3.50'),
            'tipo_separacion': 'Confinada',
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
            'nombre': 'Ciclovía Parque Bolívar',
            'color': '#4ECDC4',
            'longitud_km': Decimal('2.80'),
            'tipo_separacion': 'Pintada',
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
            'nombre': 'Ciclovía Centro-Perpetuo Socorro',
            'color': '#95E1D3',
            'longitud_km': Decimal('2.15'),
            'tipo_separacion': 'Mixta',
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.1990, -3.9920],
                    [-79.1950, -3.9930],
                    [-79.1920, -3.9960],
                ]
            }
        },
        {
            'nombre': 'Ciclovía Sauces Orellana',
            'color': '#C7CEEA',
            'longitud_km': Decimal('4.20'),
            'tipo_separacion': 'Confinada',
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
            'nombre': 'Ciclovía Calle Bolívar',
            'color': '#FFDAB9',
            'longitud_km': Decimal('3.75'),
            'tipo_separacion': 'Pintada',
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
            'nombre': 'Ciclovía Paseo Turístico',
            'color': '#B4E7FF',
            'longitud_km': Decimal('5.50'),
            'tipo_separacion': 'Confinada',
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
            'nombre': 'Ciclovía San Cayetano-Centro',
            'color': '#FFB3BA',
            'longitud_km': Decimal('1.90'),
            'tipo_separacion': 'Mixta',
            'geom': {
                'type': 'LineString',
                'coordinates': [
                    [-79.2040, -3.9920],
                    [-79.1900, -3.9900],
                    [-79.1800, -3.9880],
                    [-79.1750, -3.9870],
                ]
            }
        },
        {
            'nombre': 'Ciclovía Barrio Argelia',
            'color': '#BAFFC9',
            'longitud_km': Decimal('3.30'),
            'tipo_separacion': 'Pintada',
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
    ]
    
    created_count = 0
    for ciclovia_data in ciclovias_data:
        ciclovia, created = Ciclovia.objects.get_or_create(
            nombre=ciclovia_data['nombre'],
            defaults={
                'color': ciclovia_data['color'],
                'longitud_km': ciclovia_data['longitud_km'],
                'tipo_separacion': ciclovia_data['tipo_separacion'],
                'geom': ciclovia_data['geom'],
                'activo': True,
            }
        )
        
        if created:
            created_count += 1
            tipo = ciclovia_data['tipo_separacion']
            longitud = ciclovia_data['longitud_km']
            print(f"✓ Creada: {ciclovia.nombre}")
            print(f"  └─ Tipo: {tipo} | Longitud: {longitud} km | Color: {ciclovia.color}")
        else:
            print(f"⊘ Ya existe: {ciclovia.nombre}")
    
    print(f"\n✅ Total creadas: {created_count} ciclovías")
    return created_count


def main():
    """Función principal."""
    print("=" * 70)
    print("🚴 Cargador de Ciclovías - Loja")
    print("=" * 70)
    
    try:
        clear_ciclovias()
        create_ciclovias_loja()
        print("\n✅ ¡Script completado exitosamente!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
