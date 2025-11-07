"""URLs para documentación de la API."""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = 'docs'

urlpatterns = [
    # Schema OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='docs:schema'),
        name='swagger-ui',
    ),
    
    # ReDoc
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='docs:schema'),
        name='redoc',
    ),
]
