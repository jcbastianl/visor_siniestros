# Guía de Despliegue en Render (PostgreSQL)

Esta guía detalla cómo desplegar la aplicación **Visor Siniestros** en [Render.com](https://render.com) utilizando PostgreSQL como base de datos de producción.

## 1. Preparación del Proyecto (Ya realizado)
He configurado el proyecto en la rama `main` con los siguientes cambios necesarios para producción:

1.  **Dependencias**: Se agregaron `gunicorn`, `dj-database-url`, `whitenoise` y `psycopg2-binary` a `requirements.txt`.
2.  **Configuración (`settings.py`)**: 
    - Se configuró la base de datos para usar PostgreSQL automáticamente cuando detecta la variable `DATABASE_URL`.
    - Se configuró `WhiteNoise` para servir archivos estáticos (CSS/JS) en producción.
3.  **Scripts**: Se creó `build.sh` para automatizar la instalación y migración.
4.  **Infraestructura**: Se creó `render.yaml` (Blueprint) para desplegar todo automáticamente.

## 2. Pasos para Desplegar en Render

### Opción A: Usando Blueprints (Recomendada y Más Fácil)

La opción "Blueprint" lee el archivo `render.yaml` y configura todo (Web Service + Base de Datos) por ti.

1.  Crear una cuenta en [Render](https://dashboard.render.com/).
2.  En el Dashboard, haz clic en **New +** y selecciona **Blueprint**.
3.  Conecta tu repositorio de GitHub/GitLab.
4.  Selecciona el repositorio `Siniestros_Backend`.
5.  Dale un nombre al servicio (ej. `visor-siniestros-prod`).
6.  Render detectará automáticamente el archivo `render.yaml`.
7.  Haz clic en **Apply**.

Render creará:
- Una base de datos PostgreSQL (`visor-db`).
- El servicio web (`visor-siniestros`).
- Conectará ambos automáticamente.

### Opción B: Configuración Manual (Si prefieres control total)

1.  **Crear Base de Datos PostgreSQL**:
    - Dashboard -> New + -> PostgreSQL.
    - Nombre: `visor-db`.
    - Copia la **Internal DB URL** cuando esté lista.

2.  **Crear Web Service**:
    - Dashboard -> New + -> Web Service.
    - Conecta el repo.
    - **Runtime**: Python 3.
    - **Build Command**: `./build.sh`
    - **Start Command**: `gunicorn visor_backend.wsgi:application`
    - **Environment Variables**:
        - `DATABASE_URL`: Pegar la Internal DB URL copiada antes.
        - `SECRET_KEY`: Genera una clave segura aleatoria.
        - `PYTHON_VERSION`: `3.12.0`
        - `DEBUG`: `False` (Opcional, por defecto será False).

## 3. Verificación
Una vez desplegado, Render te dará una URL (ej. `https://visor-siniestros.onrender.com`).
Al entrar, deberías ver la aplicación funcionando correctamente con los datos importados (si decides cargar datos en producción).

### Cargar datos en Producción
Para cargar tus datos (Excel) en la base de datos de producción:
1.  Entra al Admin de Django en la URL de producción (`/admin`).
2.  Usa la funcionalidad de **Importar CSV/Excel** que restauramos.
3.  O bien, usa la Shell de Render ("Shell" tab en el dashboard) para correr comandos si prefieres subir el archivo manualmente.

## 4. Notas Importantes
- **Archivos Estáticos**: `WhiteNoise` se encargará de ellos.
- **Base de Datos**: Los datos de SQLite (local) **NO** se suben a Render. Empezarás con una base de datos vacía en PostgreSQL y deberás importar los datos nuevamente vía el Admin.
