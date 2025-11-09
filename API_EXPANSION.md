# 📊 Expansión de API - Nuevos Endpoints Estadísticos

## 🎯 Objetivo

Expandir la API de Django existente con nuevos endpoints estadísticos requeridos por el dashboard.

---

## 📋 Cambios Implementados

### 1. **`siniestros/managers.py`**

#### Nuevos métodos en `SiniestroQuerySet`:

- **`get_por_via(year=None)`**: Agrupa siniestros por vía (Top 20)
  - Retorna: `via`, `total_siniestros`, `total_lesionados`, `total_fallecidos`
  - Caso de uso: Gráfico de barras por vía

- **`get_por_causa_probable(year=None)`**: Agrupa siniestros por causa probable
  - Retorna: `id`, `causa`, `total_siniestros`, `total_lesionados`, `total_fallecidos`
  - Caso de uso: Tabla de causas

- **`get_por_tipo_siniestro(year=None)`**: Agrupa siniestros por tipo
  - Retorna: `id`, `tipo`, `total_siniestros`, `total_lesionados`, `total_fallecidos`
  - Caso de uso: Tabla de tipos

- **`get_evolucion_anual()`**: Evolución anual de siniestros
  - Retorna: `ano`, `total_siniestros`, `total_lesionados`, `total_fallecidos`
  - Caso de uso: Gráfico de línea anual

#### Nuevos métodos en `VictimaQuerySet`:

- **`get_evolucion_anual()`**: Evolución anual de víctimas
  - Retorna: `ano`, `total`
  - Caso de uso: Gráfico de línea anual de víctimas

#### Delegados agregados en managers:
- `SiniestroManager.get_por_via()`
- `SiniestroManager.get_por_causa_probable()`
- `SiniestroManager.get_por_tipo_siniestro()`
- `SiniestroManager.get_evolucion_anual()`
- `VictimaManager.get_evolucion_anual()`

---

### 2. **`siniestros/serializers.py`**

#### Nuevos serializers:

```python
class ViaStatSerializer(serializers.Serializer):
    """Estadísticas por vía"""
    via = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()

class CausaProbableStatSerializer(serializers.Serializer):
    """Estadísticas por causa probable"""
    id = serializers.IntegerField()
    causa = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()

class TipoSiniestroStatSerializer(serializers.Serializer):
    """Estadísticas por tipo de siniestro"""
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()

class EvolucionAnualSiniestrosSerializer(serializers.Serializer):
    """Evolución anual de siniestros"""
    ano = serializers.IntegerField()
    total_siniestros = serializers.IntegerField()
    total_lesionados = serializers.IntegerField()
    total_fallecidos = serializers.IntegerField()

class EvolucionAnualVictimasSerializer(serializers.Serializer):
    """Evolución anual de víctimas"""
    ano = serializers.IntegerField()
    total = serializers.IntegerField()
```

---

### 3. **`siniestros/views.py`**

#### Nuevos endpoints en `SiniestroViewSet`:

| Endpoint | Método | Descripción | Parámetros |
|----------|--------|-------------|-----------|
| `/api/siniestros/por_via/` | GET | Top 20 vías con estadísticas | `?year=YYYY` |
| `/api/siniestros/por_causa_probable/` | GET | Causas probables con totales | `?year=YYYY` |
| `/api/siniestros/por_tipo_siniestro/` | GET | Tipos de siniestro con totales | `?year=YYYY` |
| `/api/siniestros/evolucion_anual/` | GET | Evolución anual de siniestros | (sin parámetros) |

#### Nuevo endpoint en `VictimaViewSet`:

| Endpoint | Método | Descripción | Parámetros |
|----------|--------|-------------|-----------|
| `/api/victimas/evolucion_anual/` | GET | Evolución anual de víctimas | (sin parámetros) |

#### Características:

- ✅ **Documentación automática** con `@extend_schema` (Swagger/OpenAPI)
- ✅ **Caching automático** (5 minutos para estadísticas anuales, 1 hora para evolución)
- ✅ **Validación de parámetros** con helper `_validate_year()`
- ✅ **Respuestas estructuradas** con serializers específicos

---

## 🧪 Ejemplos de Uso

### Obtener estadísticas por vía (2024)
```bash
curl http://127.0.0.1:8002/api/siniestros/por_via/?year=2024
```

**Respuesta:**
```json
[
  {
    "via": "Av. Corrientes",
    "total_siniestros": 45,
    "total_lesionados": 67,
    "total_fallecidos": 12
  },
  ...
]
```

### Obtener evolución anual de siniestros
```bash
curl http://127.0.0.1:8002/api/siniestros/evolucion_anual/
```

**Respuesta:**
```json
[
  {
    "ano": 2023,
    "total_siniestros": 150,
    "total_lesionados": 230,
    "total_fallecidos": 45
  },
  {
    "ano": 2024,
    "total_siniestros": 250,
    "total_lesionados": 380,
    "total_fallecidos": 75
  },
  ...
]
```

---

## 🏗️ Arquitectura

La solución mantiene la arquitectura existente:

```
URL → ViewSet (@action) → Manager (queryset method) → QuerySet (lógica) → Serializer → JSON
```

**Ventajas:**
- ✅ Separación de responsabilidades
- ✅ Lógica reutilizable en managers
- ✅ Fácil testing
- ✅ Caching centralizado
- ✅ Documentación automática

---

## 📊 Casos de Uso en el Dashboard

1. **Gráfico de Barras por Vía**: `/api/siniestros/por_via/?year=2024`
2. **Tabla de Causas**: `/api/siniestros/por_causa_probable/?year=2024`
3. **Tabla de Tipos**: `/api/siniestros/por_tipo_siniestro/?year=2024`
4. **Gráfico de Línea Anual**: 
   - Siniestros: `/api/siniestros/evolucion_anual/`
   - Víctimas: `/api/victimas/evolucion_anual/`

---

## ✅ Verificación

Todos los endpoints han sido verificados y funcionan correctamente:

```
✓ /api/siniestros/por_via/?year=2024 -> 200 (10 items)
✓ /api/siniestros/por_causa_probable/?year=2024 -> 200 (12 items)
✓ /api/siniestros/por_tipo_siniestro/?year=2024 -> 200 (7 items)
✓ /api/siniestros/evolucion_anual/ -> 200 (3 items)
✓ /api/victimas/evolucion_anual/ -> 200 (3 items)
```

---

## 🚀 Próximos Pasos

1. **Frontend Integration**: Conectar los nuevos endpoints con los componentes React
2. **Gráficos**: Integrar bibliotecas como `recharts` o `chart.js` para visualizar datos
3. **Filtros Avanzados**: Añadir filtros por causa/tipo en los endpoints existentes
4. **Paginación**: Considerar paginación para tablas grandes

