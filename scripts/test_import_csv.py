#!/usr/bin/env python
"""
Test script para verificar la importación CSV con filtrado por año.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_siniestros.settings')
django.setup()

from siniestros.csv_import import import_csv
from siniestros.models import Siniestro, Victima

def test_import():
    print("=== Test de Importación CSV ===\n")
    
    # Limpiar datos de prueba previos
    print("1. Limpiando datos previos...")
    Victima.objects.all().delete()
    Siniestro.objects.all().delete()
    print(f"   ✓ Base de datos limpiada\n")
    
    # Test 1: Importar sin filtro
    print("2. Test sin filtro de año:")
    with open('scripts/test_import.csv', 'rb') as f:
        results = import_csv(f, clear_existing=False, anio_filtro=None)
    
    print(f"   - Filas procesadas: {results['filas_procesadas']}")
    print(f"   - Siniestros creados: {results['siniestros_creados']}")
    print(f"   - Víctimas creadas: {results['victimas_creadas']}")
    print(f"   - Errores: {len(results['errores'])}")
    
    if results['errores']:
        print("   - Primeros 3 errores:")
        for err in results['errores'][:3]:
            print(f"     • {err}")
    
    # Verificar distribución por año
    from django.db.models import Count
    from django.db.models.functions import ExtractYear
    
    distribucion = Siniestro.objects.annotate(
        year=ExtractYear('fecha_hora')
    ).values('year').annotate(count=Count('id')).order_by('year')
    
    print("\n   Distribución por año:")
    for item in distribucion:
        print(f"     {item['year']}: {item['count']} registros")
    
    # Test 2: Limpiar y re-importar solo 2025
    print("\n3. Test con filtro año 2025:")
    Victima.objects.all().delete()
    Siniestro.objects.all().delete()
    
    with open('scripts/test_import.csv', 'rb') as f:
        results = import_csv(f, clear_existing=False, anio_filtro='2025')
    
    print(f"   - Siniestros creados: {results['siniestros_creados']}")
    
    only_2025 = Siniestro.objects.annotate(
        year=ExtractYear('fecha_hora')
    ).values('year').annotate(count=Count('id'))
    
    print("   Verificación (debería ser solo 2025):")
    for item in only_2025:
        print(f"     {item['year']}: {item['count']} registros")
    
    # Test 3: Verificar víctimas con nuevo formato
    print("\n4. Test víctimas (nuevo formato de columnas):")
    victimas_sample = Victima.objects.all()[:5]
    for v in victimas_sample:
        print(f"   - {v.condicion}, Edad: {v.edad}, Sexo: {v.sexo}")
    
    print("\n✅ Tests completados!")

if __name__ == '__main__':
    test_import()
