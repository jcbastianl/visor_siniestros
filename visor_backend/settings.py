"""
Configuración de Django para el proyecto Visor de Siniestros (visor_backend).

Entorno de producción:
    Las variables sensibles (SECRET_KEY, DEBUG, DATABASE_URL, ALLOWED_HOSTS)
    se leen desde variables de entorno con valores por defecto para desarrollo local.

Documentación oficial:
    https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────
# Rutas base
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────
# Seguridad
# ──────────────────────────────────────────────

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-k(#4@q93snk$^z9vogj_16q#ke+^6@zc9sifr^s0b3i!0grck$'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,testserver'
).split(',')


# ──────────────────────────────────────────────
# Aplicaciones instaladas
# ──────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    # Apps propias
    'siniestros',
    'transporte',
]


# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'visor_backend.urls'


# ──────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'visor_backend.wsgi.application'


# ──────────────────────────────────────────────
# Base de datos
# ──────────────────────────────────────────────
# En producción (Render), se usa DATABASE_URL.
# En desarrollo local, se conecta a PostgreSQL local.

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=(
            'postgres://visor_user:visor1234@localhost:5432/visor_siniestros'
        ),
        conn_max_age=600,
    )
}


# ──────────────────────────────────────────────
# Validación de contraseñas
# ──────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ──────────────────────────────────────────────
# Internacionalización
# ──────────────────────────────────────────────

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────────
# Archivos estáticos
# ──────────────────────────────────────────────

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ──────────────────────────────────────────────
# Clave primaria por defecto
# ──────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ──────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing)
# ──────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
]

# Agregar orígenes desde variables de entorno para Producción (Azure)
env_cors = os.environ.get('CORS_ALLOWED_ORIGINS')
if env_cors:
    CORS_ALLOWED_ORIGINS.extend(env_cors.split(','))

# CSRF Trusted Origins (necesario para el admin de Django en Azure)
CSRF_TRUSTED_ORIGINS = []
env_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS')
if env_csrf:
    CSRF_TRUSTED_ORIGINS.extend(env_csrf.split(','))

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ──────────────────────────────────────────────
# Django REST Framework
# ──────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


# ──────────────────────────────────────────────
# Política de Referrer
# ──────────────────────────────────────────────
# Permite que servicios externos (ej. tiles de OpenStreetMap) reciban
# el header Referer necesario para autorizar las peticiones.

SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

# Configuración para que Django confíe en el SSL proxy de Azure
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
