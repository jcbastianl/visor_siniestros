# 📋 GUÍA DE TESTING Y USO - PROYECTO REFACTORIZADO

## 🚀 Quick Start

### 1. Preparar el Entorno

```bash
# Activar el virtual environment
source venv/bin/activate

# Ejecutar migraciones
python manage.py migrate --noinput

# Crear datos de demostración
python manage.py shell
>>> from scripts.seed_and_test_api import seed_demo_data
>>> seed_demo_data(2024)
>>> exit()
```

### 2. Ejecutar Pruebas

#### Opción A: Test con Cliente Interno de Django (SIN servidor)
```bash
python test_api_endpoints.py
```

**Resultado esperado:**
```
15 pasaron ✓ | 0 fallaron ✗
```

#### Opción B: Test contra Servidor HTTP (CON servidor)

**Terminal 1: Iniciar servidor**
```bash
python manage.py runserver 127.0.0.1:8002
```

**Terminal 2: Ejecutar tests**
```bash
python test_http_endpoints.py
```

#### Opción C: Script Completo de Seed + Testing
```bash
# Con cliente interno
python scripts/seed_and_test_api.py --year 2024

# Contra servidor HTTP
python scripts/seed_and_test_api.py --base-url http://127.0.0.1:8002 --year 2024
```

---

## 📊 Endpoints Disponibles

### Siniestros

| Endpoint | Método | Parámetros | Descripción |
|----------|--------|-----------|-------------|
| `/api/siniestros/` | GET | `page`, `page_size` | Listar siniestros (paginado) |
| `/api/siniestros/{id}/` | GET | - | Detalle de siniestro |
| `/api/siniestros/kpi_stats/` | GET | - | KPIs: total, lesionados, fallecidos |
| `/api/siniestros/por_mes/` | GET | `year` (opcional) | Breakdown mensual |
| `/api/siniestros/por_severidad/` | GET | - | Agrupado por severidad |
| `/api/siniestros/por_hora/` | GET | `year` (opcional) | Agrupado por hora (0-23) |
| `/api/siniestros/por_dia_hora/` | GET | `year` (opcional) | Matriz día×hora (7×24) |

### Víctimas

| Endpoint | Método | Parámetros | Descripción |
|----------|--------|-----------|-------------|
| `/api/victimas/` | GET | `page`, `page_size` | Listar víctimas (paginado) |
| `/api/victimas/{id}/` | GET | - | Detalle de víctima |
| `/api/victimas/por_sexo/` | GET | `year` (opcional) | Agrupado por sexo |
| `/api/victimas/por_actor_vial/` | GET | `year` (opcional) | Agrupado por tipo de actor |
| `/api/victimas/por_edad_sexo/` | GET | `year` (opcional) | Matriz edad×sexo |
| `/api/victimas/por_mes/` | GET | `year` (opcional) | Breakdown mensual |
| `/api/victimas/por_hora/` | GET | `year` (opcional) | Agrupado por hora |
| `/api/victimas/por_dia_hora/` | GET | `year` (opcional) | Matriz día×hora |

### Catálogos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/causas/` | GET | Listar causas probables (solo activas) |
| `/api/tipos-siniestro/` | GET | Listar tipos de siniestro (solo activos) |

---

## 🧪 Testing Detallado

### Test Unitario: Managers

```python
python manage.py shell
>>> from siniestros.models import Siniestro, Victima
>>> 
>>> # Test KPI Stats
>>> kpi = Siniestro.objects.get_kpi_stats()
>>> print(kpi)
{'total_siniestros': 4, 'total_lesionados': 2, 'total_fallecidos': 2}
>>> 
>>> # Test Por Mes
>>> por_mes = Siniestro.objects.get_por_mes(2024)
>>> print(len(por_mes))  # Debe ser 12 (todos los meses)
12
>>> 
>>> # Test Víctimas Por Sexo
>>> por_sexo = Victima.objects.get_por_sexo(2024)
>>> print(por_sexo)
[{'codigo': 'HOMBRE', 'label': 'Hombre', 'total': 2}, ...]
>>> 
>>> exit()
```

### Test Admin Panel

```bash
# Crear superuser
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver

# Acceder a http://localhost:8000/admin/
# Login y verificar:
# - Siniestros listados
# - Víctimas listadas
# - Causas y Tipos visibles
```

### Test Swagger Documentation

```bash
# Iniciar servidor
python manage.py runserver

# Acceder a http://localhost:8000/api/schema/swagger-ui/
# Verificar:
# - Todos los endpoints listados
# - Documentación visible
# - Prueba interactiva de endpoints
```

---

## 📁 Estructura de Archivos

```
siniestros/
├── managers.py              ← QuerySets + Managers (agregación)
├── models.py                ← Definiciones de modelos
├── serializers.py           ← Serializadores
├── urls.py                  ← URLs consolidadas
├── views/
│   ├── __init__.py          ← Exports
│   └── api_datos.py         ← ViewSets consolidados
├── migrations/
│   ├── 0001_initial.py
│   └── 0002_alter_siniestro_options...py  ← Índices y opciones
├── admin.py                 ← Admin site
├── apps.py
└── tests.py                 ← Tests unitarios

scripts/
├── seed_and_test_api.py     ← Seed + testing

test_api_endpoints.py         ← Test script interno
test_http_endpoints.py        ← Test script HTTP
TESTING_REPORT.md             ← Reporte completo
```

---

## 🔍 Verificar Estado del Proyecto

### 1. Líneas de Código

```bash
wc -l siniestros/{managers.py,models.py,serializers.py,urls.py} siniestros/views/api_datos.py
# Expected: ~788 total
```

### 2. Validar Sintaxis

```bash
# Usa VS Code + Pylance o:
python -m py_compile siniestros/managers.py
python -m py_compile siniestros/models.py
python -m py_compile siniestros/views/api_datos.py
```

### 3. Ejecutar Tests Django

```bash
python manage.py test siniestros -v 2
```

### 4. Verificar Migraciones

```bash
python manage.py showmigrations siniestros
# Must show: [X] 0001_initial
#           [X] 0002_alter_siniestro_options...
```

---

## 🐛 Troubleshooting

### Error: "No module named 'siniestros'"

```bash
# Asegúrate que estás en la raíz del proyecto
cd /home/joseph/Documents/visor_siniestros
source venv/bin/activate
```

### Error: "get_kpi_stats() not found"

```bash
# Actualiza los managers (ya deberían tener delegación)
# Verifica que managers.py tenga los métodos delegados:
grep "def get_kpi_stats" siniestros/managers.py
```

### Error 404 en endpoints

```bash
# Verifica que urls.py esté importando correctamente
grep "DefaultRouter" siniestros/urls.py
grep "SiniestroViewSet" siniestros/urls.py

# Revisa visor_backend/urls.py
grep "include(.*siniestros" visor_backend/urls.py
```

### Servidor no responde

```bash
# Asegúrate que no hay otro proceso en el puerto
lsof -i :8000
lsof -i :8002

# Mata el proceso si es necesario
kill -9 <PID>
```

---

## 📈 Métricas de Éxito

✓ **Código:**
- Managers: 326 líneas
- Models: 100 líneas  
- Views: 231 líneas
- URLs: 14 líneas
- Total: 788 líneas (-34% vs antes)

✓ **Testing:**
- 15/15 endpoints: 200 OK
- Todos los managers funcionan
- Migraciones aplicadas
- Demo data seeded

✓ **Arquitectura:**
- Separación clara (models → managers → views → serializers)
- Sin duplicación de código
- Pragmático, sin sobre-ingeniería
- Máximo aprovechamiento de DRF

---

## 📞 Referencias Rápidas

### QuerySet Methods (Siniestro)

```python
Siniestro.objects.get_kpi_stats()          # KPI stats
Siniestro.objects.get_por_mes(year)        # Monthly breakdown
Siniestro.objects.get_por_severidad()      # By severity
Siniestro.objects.get_por_hora(year)       # By hour
Siniestro.objects.get_por_dia_hora(year)   # Day×Hour matrix
```

### QuerySet Methods (Victima)

```python
Victima.objects.get_por_sexo(year)         # By gender
Victima.objects.get_por_actor_vial(year)   # By road actor
Victima.objects.get_por_edad_sexo(year)    # Age×Gender
Victima.objects.get_por_mes(year)          # Monthly
Victima.objects.get_por_hora(year)         # By hour
Victima.objects.get_por_dia_hora(year)     # Day×Hour
```

### URLs Autogeneradas

```
# List
GET /api/siniestros/
GET /api/victimas/

# Detail
GET /api/siniestros/1/
GET /api/victimas/1/

# Actions
GET /api/siniestros/kpi_stats/
GET /api/siniestros/por_mes/
GET /api/victimas/por_sexo/
... (ver tabla de endpoints completa arriba)
```

---

**Última actualización:** 7 de Noviembre de 2025
**Status:** ✅ Completo y testeado
