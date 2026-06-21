"""Configuración global de pytest para el backend del Visor de Siniestros.

Las pruebas corren contra PostgreSQL (mismo motor que producción). pytest-django
crea y destruye una base de datos de test dedicada (``test_<nombre>``) a partir de
la configuración de ``visor_backend.settings``.

Se limpia la caché de Django entre tests para que el decorador ``cache_page`` de las
vistas no devuelva respuestas cacheadas de un test anterior.
"""

import pytest


@pytest.fixture(autouse=True)
def _clear_cache():
    """Evita colisiones de cache_page entre tests que golpean la misma URL."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
