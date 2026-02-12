import os
import django
from django.contrib.auth import get_user_model

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visor_backend.settings")
django.setup()

def create_superuser():
    User = get_user_model()
    
    # Obtener credenciales de variables de entorno (con defaults seguros)
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
