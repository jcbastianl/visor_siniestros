"""Configuración de la app de transporte público y ciclovías."""

from django.apps import AppConfig


class TransporteConfig(AppConfig):
    """Configuración de la aplicación Django para transporte urbano."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transporte'
    verbose_name = 'Transporte Urbano'
