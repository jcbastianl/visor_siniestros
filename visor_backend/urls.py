"""
Configuración raíz de URLs del proyecto Visor de Siniestros.

Estructura de la API:
    - ``/admin/``                       — Panel de administración de Django
    - ``/api/siniestros/``              — API de siniestros (CRUD + estadísticas)
    - ``/api/victimas/``                — API de víctimas (CRUD + estadísticas)
    - ``/api/causas/``                  — Catálogo de causas probables
    - ``/api/tipos-siniestro/``         — Catálogo de tipos de siniestro
    - ``/api/lineas/``                  — Líneas de bus (solo lectura)
    - ``/api/ciclovias/``               — Ciclovías (solo lectura)
    - ``/api/schema/``                  — Esquema OpenAPI 3.0
    - ``/api/schema/swagger-ui/``       — Documentación interactiva (Swagger)
    - ``/api/schema/redoc/``            — Documentación alternativa (ReDoc)
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/'), name='home'),
    path('admin/', admin.site.urls),

    # Documentación OpenAPI (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API REST
    path('api/', include('siniestros.urls')),
    path('api/', include('transporte.urls')),
]
