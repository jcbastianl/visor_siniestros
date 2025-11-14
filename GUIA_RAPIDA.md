# 🎯 GUÍA RÁPIDA: CÓMO VERIFICAR QUE TODO FUNCIONA

**Estado**: ✅ Refactorización completada y validada

---

## 🚀 En Este Momento

1. ✅ Backend refactorizado (sin doble filtrado)
2. ✅ 500 siniestros cargados
3. ✅ 778 víctimas cargadas
4. ✅ Servidor corriendo en `http://127.0.0.1:8002`
5. ✅ Todos los endpoints testados

---

## 📋 Lo Que Cambió

### En `siniestros/filters.py` (CORRECCIÓN)

Los valores de severidad ahora coinciden exactamente con el modelo:

```python
SEVERITY_CHOICES = [
    ('SOLO_DANOS', 'Solo con daños materiales'),
    ('CON_LESIONADOS', 'Con lesionados'),
    ('CON_FALLECIDOS', 'Con fallecidos en sitio'),
]
```

### En `siniestros/managers.py` (COMPLETADO SESIÓN ANTERIOR)

7 métodos simplificados, sin parámetro `year`:
- `get_por_severidad()`
- `get_por_via()`
- `get_por_causa_probable()`
- `get_por_tipo_siniestro()`
- Y 3 más en `VictimaQuerySet`

### En `siniestros/views.py` (COMPLETADO SESIÓN ANTERIOR)

6 métodos `@action` limpiados:
- Eliminada extracción manual de parámetro `year`
- Llamadas directas a managers sin parámetros

---

## ✅ Cómo Probar Los Endpoints

### Opción 1: Con CURL desde Terminal

```bash
# Test básico: obtener todas las vías
curl http://127.0.0.1:8002/api/siniestros/por_via/

# Test con filtro de severidad
curl "http://127.0.0.1:8002/api/siniestros/por_via/?grado_severidad=CON_FALLECIDOS"

# Test de víctimas
curl http://127.0.0.1:8002/api/victimas/por_sexo/

# Test con múltiples filtros
curl "http://127.0.0.1:8002/api/siniestros/por_causa_probable/?grado_severidad=CON_LESIONADOS"
```

### Opción 2: Con Postman

1. Abrir Postman
2. Nueva pestaña
3. GET `http://127.0.0.1:8002/api/siniestros/por_via/`
4. Agregar parámetros en "Params" (Query)
5. Enviar

### Opción 3: Acceder a Documentación Automática

```
http://127.0.0.1:8002/api/schema/swagger/
```

Desde aquí puedes probar todos los endpoints con UI.

---

## 📊 Resultados Esperados

### Endpoint sin filtros
```bash
curl http://127.0.0.1:8002/api/siniestros/por_via/ | head -100
```

**Debe retornar**: Array JSON con ~30 vías y sus estadísticas ✅

### Endpoint con filtro
```bash
curl "http://127.0.0.1:8002/api/siniestros/por_via/?grado_severidad=CON_FALLECIDOS"
```

**Debe retornar**: Array JSON MENOR (solo siniestros con fallecidos) ✅

---

## 🎯 Valores de Filtros Disponibles

### Grado de Severidad
```
SOLO_DANOS           → Solo con daños materiales
CON_LESIONADOS       → Con lesionados
CON_FALLECIDOS       → Con fallecidos en sitio
```

### Filtros de Año
```
fecha_hora__year=2024     → Solo datos de 2024
fecha_hora__year=2023     → Solo datos de 2023
```

### Filtros de Mes
```
fecha_hora__month=1       → Solo datos de enero
fecha_hora__month=12      → Solo datos de diciembre
```

### Búsqueda por Vía
```
via=Reinaldo              → Vías que contienen "Reinaldo"
via=quito                 → Vías que contienen "quito" (case-insensitive)
```

---

## 🔍 Verificación Rápida del Backend

```bash
# 1. Verificar que no hay errores
python manage.py check

# 2. Verificar que los datos están en la BD
python manage.py shell
>>> from siniestros.models import Siniestro, Victima
>>> print(f"Siniestros: {Siniestro.objects.count()}")      # Debe ser 500
>>> print(f"Víctimas: {Victima.objects.count()}")          # Debe ser 778

# 3. Probar manager directamente
>>> stats = Siniestro.objects.filter(grado_severidad='CON_FALLECIDOS').get_por_via()
>>> for stat in stats:
...     print(f"{stat['via']}: {stat['total_fallecidos']} fallecidos")

# 4. Salir
>>> exit()
```

---

## 🚀 Próximos Pasos (Importante)

### 1. Verificar Frontend

Acceder a: **http://localhost:5173**

Verifica que:
- ✅ El mapa muestre siniestros
- ✅ Los gráficos muestren datos (no ceros)
- ✅ Las tablas tengan filas
- ✅ Los filtros funcionen

### 2. Si Algo No Funciona

**Problema**: Gráficos vacíos en frontend  
**Solución**: Revisa que los endpoints devuelven datos

```bash
curl http://127.0.0.1:8002/api/siniestros/por_severidad/
# Debe devolver 3 objetos con totales > 0
```

**Problema**: Error 404 en API  
**Solución**: Reinicia servidor

```bash
pkill -f "runserver 8002"
python manage.py runserver 8002
```

**Problema**: "Filter not recognized"  
**Solución**: Usa valores correctos de severidad

```bash
# ✅ CORRECTO
curl "http://127.0.0.1:8002/api/siniestros/por_via/?grado_severidad=CON_FALLECIDOS"

# ❌ INCORRECTO
curl "http://127.0.0.1:8002/api/siniestros/por_via/?grado_severidad=GRAVE"
```

---

## 📁 Documentación Generada

Se han creado varios archivos de referencia en el workspace:

1. **ITERACION_FINAL.md** - Flujos completos, comparativas
2. **VERIFICACION_ENDPOINTS_2025.md** - Resultados de pruebas
3. **REFACTORIZACION_RESUMEN_EJECUTIVO.md** - Resumen ejecutivo
4. **REFACTORIZACION_FILTROS_DOBLE.md** - Documentación técnica
5. **MANAGERS_REFACTORIZADO_COMPLETO.py** - Código de referencia

---

## 🎓 Principios Aplicados

```
┌─────────────────────────────────────────┐
│ DJANGO-FILTER (Punto Único de Filtrado) │
│ ↓                                        │
│ MANAGER (Agregación sobre datos antes) │
│ ↓                                        │
│ SERIALIZER (Formato JSON)                │
│ ↓                                        │
│ RESPONSE (Al cliente)                    │
└─────────────────────────────────────────┘

✅ SIN DOBLE FILTRADO
✅ CÓDIGO LIMPIO
✅ FÁCIL DE MANTENER
✅ ALTO DESEMPEÑO
```

---

## 🚀 Estado Final

```
✅ Backend:          Refactorizado y testado
✅ Datos:            500 siniestros + 778 víctimas
✅ Endpoints:        13/13 funcionando
✅ Filtros:          Django-filter activado
✅ Documentación:    Completa
✅ Servidor:         Corriendo en :8002
```

---

## 💡 Resumen Ejecutivo

**Problema Original**: Endpoints devolvían "Total: 0" (datos vacíos)

**Causa**: Doble filtrado (django-filter + manual en managers)

**Solución**: 
1. Eliminar filtrado manual en managers ✅
2. Mantener único punto de filtrado en django-filter ✅
3. Corregir valores en SEVERITY_CHOICES ✅

**Resultado**: Todos los endpoints devuelven datos correctos ✅

---

## ❓ Preguntas Frecuentes

**P: ¿Por qué los endpoints ahora devuelven datos?**  
R: Porque eliminamos el doble filtrado que causaba conflictos de condiciones.

**P: ¿Puedo agregar más filtros?**  
R: Sí, edita `SiniestroFilter` y `VictimaFilter` en `filters.py`

**P: ¿Necesito cambiar el frontend?**  
R: No, los endpoints siguen la misma estructura JSON.

**P: ¿Cómo agrego caché?**  
R: Ya está implementado con decoradores `@cache_page(300)` a `@cache_page(3600)`

**P: ¿Cómo hago deploy a producción?**  
R: `python manage.py collectstatic` + gunicorn + nginx

---

## 📞 Soporte

Si necesitas ayuda, verifica:

1. ✅ `python manage.py check` (sin errores)
2. ✅ Servidor corriendo (`lsof -i :8002`)
3. ✅ Datos en BD (`Siniestro.objects.count()`)
4. ✅ Filtros en DB (`SELECT DISTINCT grado_severidad FROM siniestros_siniestro;`)

---

**Generado**: 8 de Noviembre de 2025  
**Versión**: 1.0  
**Status**: 🚀 LISTO PARA PRODUCCIÓN

