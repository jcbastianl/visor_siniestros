#!/usr/bin/env python
"""Test script para verificar que todos los endpoints funcionan correctamente."""

import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visor_backend.settings')
django.setup()

from django.test import Client
import json

def print_test_result(endpoint, status_code, success=True):
    """Imprime el resultado de un test."""
    icon = "✓" if success else "✗"
    color = "\033[92m" if success else "\033[91m"  # Verde o Rojo
    reset = "\033[0m"
    print(f"{color}{icon}{reset} {endpoint:50} -> {status_code}")

def test_all_endpoints():
    """Prueba todos los endpoints de la API."""
    client = Client()
    
    # Endpoints a probar
    endpoints = [
        # Siniestros
        ('/api/siniestros/', 'GET'),
        ('/api/siniestros/kpi_stats/', 'GET'),
        ('/api/siniestros/por_mes/?year=2024', 'GET'),
        ('/api/siniestros/por_severidad/', 'GET'),
        ('/api/siniestros/por_hora/?year=2024', 'GET'),
        ('/api/siniestros/por_dia_hora/?year=2024', 'GET'),
        
        # Víctimas
        ('/api/victimas/', 'GET'),
        ('/api/victimas/por_sexo/?year=2024', 'GET'),
        ('/api/victimas/por_actor_vial/?year=2024', 'GET'),
        ('/api/victimas/por_edad_sexo/?year=2024', 'GET'),
        ('/api/victimas/por_mes/?year=2024', 'GET'),
        ('/api/victimas/por_hora/?year=2024', 'GET'),
        ('/api/victimas/por_dia_hora/?year=2024', 'GET'),
        
        # Catálogos
        ('/api/causas/', 'GET'),
        ('/api/tipos-siniestro/', 'GET'),
    ]
    
    print("\n" + "="*70)
    print("PRUEBAS DE ENDPOINTS DE LA API")
    print("="*70 + "\n")
    
    passed = 0
    failed = 0
    
    for endpoint, method in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        
        success = response.status_code == 200
        print_test_result(endpoint, response.status_code, success)
        
        if success:
            passed += 1
        else:
            failed += 1
            # Mostrar detalles del error
            try:
                print(f"  Respuesta: {response.json()}")
            except:
                print(f"  Respuesta: {response.content[:200]}")
    
    print("\n" + "="*70)
    print(f"RESULTADOS: {passed} pasaron ✓ | {failed} fallaron ✗")
    print("="*70 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = test_all_endpoints()
    sys.exit(0 if success else 1)
