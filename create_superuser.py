"""
Script para crear un superusuario de Django en despliegues automatizados.

Lee las credenciales desde variables de entorno:
    - ``DJANGO_SUPERUSER_USERNAME`` (default: ``admin``)
    - ``DJANGO_SUPERUSER_EMAIL`` (default: ``admin@example.com``)
    - ``DJANGO_SUPERUSER_PASSWORD`` (requerida, sin default)

Uso:
    Ejecutado automáticamente por ``build.sh`` durante el deploy en Render.
    También puede ejecutarse manualmente: ``python create_superuser.py``
"""

import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visor_backend.settings")
django.setup()


def create_superuser():
    """
    Crea un superusuario si no existe ya uno con el mismo username.

    Las credenciales se obtienen de variables de entorno. Si
    ``DJANGO_SUPERUSER_PASSWORD`` no está definida, se omite la creación
    con un aviso informativo (no es un error).
    """
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not password:
        print("AVISO: 'DJANGO_SUPERUSER_PASSWORD' no está configurada. Saltando creación de superusuario.")
        print("Para crear el admin, añade esta variable de entorno en Render.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"Creando superusuario '{username}'...")
        try:
            User.objects.create_superuser(username, email, password)
            print(f"¡ÉXITO! Superusuario '{username}' creado correctamente.")
        except Exception as e:
            print(f"ERROR: Falló la creación del superusuario: {e}")
    else:
        print(f"El superusuario '{username}' ya existe. No es necesario crearlo.")


if __name__ == "__main__":
    create_superuser()
