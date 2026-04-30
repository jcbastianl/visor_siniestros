#!/bin/bash
# startup.sh para Azure App Service

echo "Ejecutando colecta de archivos estáticos..."
python manage.py collectstatic --noinput

echo "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

echo "Iniciando Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 visor_backend.wsgi:application
