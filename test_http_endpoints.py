#!/usr/bin/env python
"""Test endpoints contra un servidor HTTP en vivo."""

import sys
import urllib.request
import urllib.error
import json

def test_http_endpoint(base_url, endpoint):
    """Prueba un endpoint HTTP."""
    url = f"{base_url}{endpoint}"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return response.status, True, data[:100]
    except urllib.error.HTTPError as e:
        return e.code, False, str(e)
    except Exception as e:
        return None, False, str(e)

def print_test_result(endpoint, status_code, success=True):
    """Imprime el resultado de un test."""
    icon = "✓" if success else "✗"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{icon}{reset} {endpoint:50} -> {status_code}")

def main():
    base_url = "http://127.0.0.1:8002"
    
    endpoints = [
        '/api/siniestros/',
        '/api/siniestros/kpi_stats/',
        '/api/siniestros/por_mes/?year=2024',
        '/api/siniestros/por_severidad/',
        '/api/siniestros/por_hora/?year=2024',
        '/api/siniestros/por_dia_hora/?year=2024',
        '/api/victimas/',
        '/api/victimas/por_sexo/?year=2024',
        '/api/victimas/por_actor_vial/?year=2024',
        '/api/victimas/por_edad_sexo/?year=2024',
        '/api/victimas/por_mes/?year=2024',
        '/api/victimas/por_hora/?year=2024',
        '/api/victimas/por_dia_hora/?year=2024',
        '/api/causas/',
        '/api/tipos-siniestro/',
    ]
    
    print("\n" + "="*70)
    print(f"PRUEBAS CONTRA SERVIDOR HTTP: {base_url}")
    print("="*70 + "\n")
    
    passed = 0
    failed = 0
    
    for endpoint in endpoints:
        status, success, data = test_http_endpoint(base_url, endpoint)
        print_test_result(endpoint, status, success)
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTADOS: {passed} pasaron ✓ | {failed} fallaron ✗")
    print("="*70 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
