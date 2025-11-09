# Guía de Filtros Avanzados - API de Siniestros

## 📋 Overview

La API ahora soporta **filtros avanzados** usando `django-filter`. Todos los endpoints de `Siniestro` y `Victima` pueden ser filtrados por:

- **Temporal**: Año, Mes, Día de la semana, Hora
- **Severity/Condición**: Grado de severidad (para Siniestro), Sexo y Condición (para Victima)
- **Relaciones**: Causa probable, Tipo de siniestro
- **Búsqueda**: Vía (búsqueda case-insensitive)

## 🔧 Instalación y Configuración

### 1. django-filter está instalado y configurado en:

```python
# visor_backend/settings.py

INSTALLED_APPS = [
    # ...
    'django_filters',
    'siniestros',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}
```

### 2. Filtros definidos en `siniestros/filters.py`:

- `SiniestroFilter`: Para modelo `Siniestro`
- `VictimaFilter`: Para modelo `Victima`

### 3. ViewSets configurados con filtros:

```python
class SiniestroViewSet(ReadOnlyModelViewSet):
    filterset_class = SiniestroFilter

class VictimaViewSet(ReadOnlyModelViewSet):
    filterset_class = VictimaFilter
```

---

## 📊 Ejemplos de Uso

### Filtros de Siniestro

#### 1. Filtrar por Año

```bash
GET /api/siniestros/?fecha_hora__year=2024
```

Response: Todos los siniestros del año 2024

#### 2. Filtrar por Mes

```bash
GET /api/siniestros/?fecha_hora__month=6
```

Response: Todos los siniestros de junio (cualquier año)

#### 3. Filtrar por Día de la Semana

```bash
GET /api/siniestros/?fecha_hora__week_day=5
```

**Valores válidos**:
- 1 = Sunday (Domingo)
- 2 = Monday (Lunes)
- 3 = Tuesday (Martes)
- 4 = Wednesday (Miércoles)
- 5 = Thursday (Jueves)
- 6 = Friday (Viernes)
- 7 = Saturday (Sábado)

Response: Todos los siniestros que ocurrieron en jueves

#### 4. Filtrar por Hora

```bash
GET /api/siniestros/?fecha_hora__hour=15
```

**Valores válidos**: 0-23 (representan rangos horarios)
- 0 = 00:00 - 00:59
- 15 = 15:00 - 15:59
- 23 = 23:00 - 23:59

Response: Todos los siniestros que ocurrieron entre las 15:00 y 15:59

#### 5. Filtrar por Severidad

```bash
GET /api/siniestros/?grado_severidad=GRAVE
```

**Valores válidos**:
- `LEVE`
- `MODERADO`
- `GRAVE`
- `CRITICO`

Response: Todos los siniestros graves

#### 6. Filtrar por Causa Probable

```bash
GET /api/siniestros/?causa_probable=1
```

(Reemplaza `1` con el ID de la causa)

Response: Todos los siniestros con esa causa probable

#### 7. Filtrar por Tipo de Siniestro

```bash
GET /api/siniestros/?tipo_siniestro=2
```

(Reemplaza `2` con el ID del tipo)

Response: Todos los siniestros de ese tipo

#### 8. Búsqueda de Vía

```bash
GET /api/siniestros/?via=carrera
```

Response: Todos los siniestros en vías que contengan "carrera" (case-insensitive)

#### 9. Rango de Años

```bash
GET /api/siniestros/?fecha_hora__year_range_min=2022&fecha_hora__year_range_max=2024
```

Response: Todos los siniestros entre 2022 y 2024 (inclusive)

### Filtros Combinados (Y lógico)

Todos los filtros se pueden combinar con `&`:

```bash
GET /api/siniestros/?fecha_hora__year=2024&fecha_hora__month=6&grado_severidad=GRAVE
```

Response: Siniestros graves de junio de 2024

```bash
GET /api/siniestros/?fecha_hora__week_day=5&fecha_hora__hour=15&grado_severidad=CRITICO
```

Response: Siniestros críticos que ocurrieron en jueves a las 15:xx horas

---

## 👥 Filtros de Victima

El `VictimaFilter` incluye filtros adicionales porque se accede al modelo `Victima` a través del siniestro relacionado:

### 1. Filtros Temporales (del Siniestro)

```bash
GET /api/victimas/?siniestro__fecha_hora__year=2024
```

### 2. Filtrar por Sexo

```bash
GET /api/victimas/?sexo=M
```

**Valores válidos**:
- `M` = Masculino
- `F` = Femenino
- `O` = Otro

### 3. Filtrar por Condición

```bash
GET /api/victimas/?condicion=LESIONADO
```

**Valores válidos**:
- `LESIONADO`
- `FALLECIDO`
- `ILESO`

### 4. Filtrar por Actor Vial

```bash
GET /api/victimas/?actor_vial=PEATÓN
```

**Valores válidos**:
- `PEATÓN`
- `CONDUCTOR`
- `PASAJERO`
- `CICLISTA`
- `MOTOCICLISTA`

### 5. Filtrar por Edad Exacta

```bash
GET /api/victimas/?edad=25
```

Response: Todas las víctimas de exactamente 25 años

### 6. Filtrar por Rango de Edad

```bash
GET /api/victimas/?edad_min=18&edad_max=65
```

Response: Todas las víctimas entre 18 y 65 años

### Ejemplos Combinados

```bash
GET /api/victimas/?siniestro__fecha_hora__year=2024&condicion=FALLECIDO&sexo=M
```

Response: Hombres fallecidos en siniestros de 2024

```bash
GET /api/victimas/?actor_vial=PEATÓN&edad_min=5&edad_max=17
```

Response: Peatones menores de 18 años

---

## 📈 Integración con Endpoints de Estadísticas

Los filtros funcionan con **TODOS los endpoints**, incluyendo acciones estadísticas:

### Ejemplo 1: Estadísticas de Siniestros Graves

```bash
GET /api/siniestros/por_mes/?grado_severidad=GRAVE&fecha_hora__year=2024
```

Response: Estadísticas mensuales, pero **solo** para siniestros graves de 2024

### Ejemplo 2: Evolución Anual de Víctimas Peatones

```bash
GET /api/victimas/evolucion_anual?actor_vial=PEATÓN
```

Response: Evolución anual de víctimas peatones

### Ejemplo 3: Siniestros por Vía Filtrando por Severidad

```bash
GET /api/siniestros/por_via/?grado_severidad=CRITICO&fecha_hora__year=2024
```

Response: Top 20 de vías ordenadas por siniestros críticos en 2024

---

## 🎯 Ventajas del Sistema

| Aspecto | Ventaja |
|---------|---------|
| **Flexibilidad** | Combina cualquier cantidad de filtros |
| **Reutilizable** | Todos los endpoints usan los mismos filtros |
| **Documentado** | Swagger UI muestra todos los parámetros disponibles |
| **Eficiente** | Los filtros se aplican a nivel de QuerySet (base de datos) |
| **Escalable** | Fácil agregar nuevos filtros en `filters.py` |

---

## 🔗 API Endpoints Principales

### Siniestros
- `GET /api/siniestros/` - Lista (con filtros)
- `GET /api/siniestros/{id}/` - Detalle
- `GET /api/siniestros/kpi_stats/` - KPIs
- `GET /api/siniestros/por_mes/` - Estadísticas mensuales
- `GET /api/siniestros/por_hora/` - Estadísticas por hora
- `GET /api/siniestros/por_severidad/` - Estadísticas por severidad
- `GET /api/siniestros/por_dia_hora/` - Matriz día × hora
- `GET /api/siniestros/por_via/` - Top vías
- `GET /api/siniestros/por_causa_probable/` - Causas probables
- `GET /api/siniestros/por_tipo_siniestro/` - Tipos de siniestro
- `GET /api/siniestros/evolucion_anual/` - Evolución anual

### Víctimas
- `GET /api/victimas/` - Lista (con filtros)
- `GET /api/victimas/{id}/` - Detalle
- `GET /api/victimas/por_sexo/` - Estadísticas por sexo
- `GET /api/victimas/por_actor_vial/` - Estadísticas por actor vial
- `GET /api/victimas/por_edad_sexo/` - Estadísticas por edad y sexo
- `GET /api/victimas/por_mes/` - Estadísticas mensuales
- `GET /api/victimas/por_hora/` - Estadísticas por hora
- `GET /api/victimas/por_dia_hora/` - Matriz día × hora
- `GET /api/victimas/evolucion_anual/` - Evolución anual

---

## 📝 Notas Importantes

1. **Orden de Filtrado**: Los filtros se aplican mediante lógica **AND** (todas las condiciones deben cumplirse)

2. **Case Sensitivity**: 
   - Valores numéricos (year, month, hour): exactos
   - Valores texto (grado_severidad, sexo, etc.): case-sensitive (usa mayúsculas)
   - Búsqueda de vía: case-**insensitive**

3. **Parámetros Nulos**: Si un parámetro de filtro no se proporciona, se ignora

4. **Performance**: Los filtros se aplican a nivel de base de datos usando ORM de Django, lo que asegura buen performance incluso con millones de registros

5. **Combinación con Paginación**: Los filtros funcionan perfectamente con paginación:
   ```bash
   GET /api/siniestros/?fecha_hora__year=2024&limit=50&offset=0
   ```

---

## 🛠️ Archivos Relacionados

- **`siniestros/filters.py`**: Definición de filtros
- **`siniestros/views.py`**: ViewSets con `filterset_class`
- **`visor_backend/settings.py`**: Configuración de django-filter

---

## 📚 Referencias

- [django-filter Documentation](https://django-filter.readthedocs.io/)
- [DRF FilterBackends](https://www.django-rest-framework.org/api-guide/filtering/)
- [Django ORM Lookups](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#field-lookups)
