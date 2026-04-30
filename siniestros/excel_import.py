"""
Módulo para importar datos de siniestros desde archivos Excel o CSV.

Este módulo proporciona funciones para leer archivos Excel/CSV ,
parsear, validar y crear registros de Siniestro y Victima mapeando automáticamente
los campos del CSV al modelo de base de datos.
"""

import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Siniestro, Victima, TipoSiniestro, Causa
import logging

logger = logging.getLogger(__name__)


class ExcelImportError(Exception):
    """Excepción personalizada para errores de importación Excel/CSV."""
    pass


def clean_value(value):
    """
    Limpia valores comunes no válidos del CSV.

    Args:
        value: Valor a limpiar

    Returns:
        Valor limpio o None si no es válido
    """
    if pd.isna(value):
        return None

    value_str = str(value).strip()

    # Valores que deben ser tratados como None/vacío
    invalid_values = ['S/N', 's/n', 'Err:507', '', 'nan', 'NaN', 'None']

    if value_str in invalid_values:
        return None

    return value_str


def parse_fecha_hora(fecha_str, hora_str):
    """
    Combina y parsea fecha y hora del CSV o Excel.

    Args:
        fecha_str: String de fecha (formato: DD/MM/YYYY) o datetime de Excel
        hora_str: String de hora (formato: HH:MM:SS) o time de Excel

    Returns:
        datetime con timezone o None si no se puede parsear
    """
    try:
        import pandas as pd

        # Caso 1: Si fecha_str ya es un datetime (viene de Excel)
        if isinstance(fecha_str, (datetime, pd.Timestamp)):
            fecha_dt = pd.to_datetime(fecha_str)

            # Si hora_str también es datetime/time, extraer la hora
            if isinstance(hora_str, (datetime, pd.Timestamp)):
                hora_dt = pd.to_datetime(hora_str)
                dt = datetime(
                    fecha_dt.year, fecha_dt.month, fecha_dt.day,
                    hora_dt.hour, hora_dt.minute, hora_dt.second
                )
            elif isinstance(hora_str, pd.Timedelta):
                # Pandas a veces lee horas como timedelta
                total_seconds = int(hora_str.total_seconds())
                hora = total_seconds // 3600
                minuto = (total_seconds % 3600) // 60
                segundo = total_seconds % 60
                dt = datetime(
                    fecha_dt.year, fecha_dt.month, fecha_dt.day,
                    hora, minuto, segundo
                )
            elif hora_str and str(hora_str).strip():
                # Intentar parsear hora como string
                hora_parts = str(hora_str).strip().split(':')
                if len(hora_parts) >= 2:
                    hora = int(hora_parts[0])
                    minuto = int(hora_parts[1])
                    segundo = int(hora_parts[2]) if len(hora_parts) > 2 else 0
                    dt = datetime(
                        fecha_dt.year, fecha_dt.month, fecha_dt.day,
                        hora, minuto, segundo
                    )
                else:
                    # Usar solo la fecha, hora 00:00:00
                    dt = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, 0, 0, 0)
            else:
                # Solo fecha, sin hora
                dt = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, 0, 0, 0)

            return timezone.make_aware(dt, timezone.get_current_timezone())

        # Caso 2: Formato string (CSV tradicional)
        # Limpiar valores
        fecha_str = clean_value(fecha_str)
        hora_str = clean_value(hora_str)

        if not fecha_str:
            logger.debug(f"Fecha vacía recibida")
            return None
        if not hora_str:
            logger.debug(f"Hora vacía recibida")
            return None

        # Parsear fecha (formato DD/MM/YYYY)
        fecha_parts = str(fecha_str).strip().split('/')
        if len(fecha_parts) != 3:
            logger.debug(f"Formato de fecha inválido: {fecha_str}")
            return None

        dia, mes, anio = fecha_parts

        # Parsear hora (formato HH:MM:SS)
        hora_parts = str(hora_str).strip().split(':')
        if len(hora_parts) < 2:
            logger.debug(f"Formato de hora inválido: {hora_str}")
            return None

        hora = int(hora_parts[0])
        minuto = int(hora_parts[1])
        segundo = int(hora_parts[2]) if len(hora_parts) > 2 else 0

        # Crear datetime
        dt = datetime(int(anio), int(mes), int(dia), hora, minuto, segundo)
        return timezone.make_aware(dt, timezone.get_current_timezone())

    except (ValueError, AttributeError, IndexError) as e:
        logger.warning(f"Error parseando fecha/hora: fecha={type(fecha_str).__name__}:{fecha_str}, hora={type(hora_str).__name__}:{hora_str} - {e}")
        return None


def parse_severidad(resultado_str):
    """
    Mapea RESULTADOS CONSECUENCIAS del CSV a grado_severidad del modelo.

    Args:
        resultado_str: String con resultado/consecuencia

    Returns:
        Valor de Severidad.choices o None
    """
    if not resultado_str:
        return Siniestro.Severidad.SOLO_DANOS  # Default

    resultado_str = clean_value(resultado_str)
    if not resultado_str:
        return Siniestro.Severidad.SOLO_DANOS

    resultado_upper = resultado_str.upper()

    # Mapeo de strings del CSV a choices del modelo
    # Ampliado con más variaciones de texto
    if any(word in resultado_upper for word in [
        'FALLECIDO', 'FALLECIDA', 'MUERTE', 'MUERTO', 'MUERTA',
        'FATAL', 'DECESO', 'ÓBITO', 'OBITO', 'SITIO'
    ]):
        return Siniestro.Severidad.CON_FALLECIDOS
    elif any(word in resultado_upper for word in [
        'HERIDO', 'HERIDA', 'LESIONADO', 'LESIONADA', 'LESION', 'LESIÓN'
    ]):
        return Siniestro.Severidad.CON_LESIONADOS
    else:
        # Log para valores no reconocidos (ayuda a identificar nuevas variaciones)
        if resultado_upper not in ['SOLO DAÑOS', 'SOLO DANOS', 'DAÑOS MATERIALES', 'DANOS MATERIALES', 'MATERIAL']:
            logger.info(f"Severidad no reconocida en RESULTADOS CONSECUENCIAS: '{resultado_str}' - usando SOLO_DANOS como default")
        return Siniestro.Severidad.SOLO_DANOS


def parse_coordenada(coord_str):
    """
    Parsea coordenada (latitud o longitud) del CSV.
    Maneja múltiples formatos:
    - Formato estándar: -3.981058
    - Formato con coma decimal: -3,981058
    - Formato con separadores de miles: -39.871.838 o -3.978.214
    - Valores inválidos: NN, N/A, S/N, etc.

    Args:
        coord_str: String con coordenada

    Returns:
        float o 0.0 si no es válida
    """
    try:
        coord_str = clean_value(coord_str)
        if not coord_str:
            return 0.0

        # Convertir a string para manipulación
        coord_str = str(coord_str).strip()

        # Detectar si usa punto como separador de miles y coma como decimal
        # Ejemplo: -39.871.838,123 o -3.978.214
        if '.' in coord_str and coord_str.count('.') >= 2:
            # Múltiples puntos = separadores de miles
            # Remover todos los puntos y luego convertir coma a punto
            coord_str_normalized = coord_str.replace('.', '').replace(',', '.')
        elif ',' in coord_str and '.' in coord_str:
            # Tiene ambos: asumir punto=miles, coma=decimal
            coord_str_normalized = coord_str.replace('.', '').replace(',', '.')
        else:
            # Solo tiene coma o solo punto: coma → punto
            coord_str_normalized = coord_str.replace(',', '.')

        coord = float(coord_str_normalized)

        # Validar rango razonable para coordenadas en Ecuador
        # Latitud: -5 a 2 aproximadamente
        # Longitud: -81 a -75 aproximadamente
        if coord != 0.0:
            if abs(coord) > 180:  # Coordenada fuera de rango mundial
                logger.debug(f"Coordenada fuera de rango: {coord} (original: '{coord_str}')")
                return 0.0

        return coord
    except (ValueError, AttributeError) as e:
        logger.debug(f"Error parseando coordenada '{coord_str}': {e}")
        return 0.0


def extract_vehiculos_info(row):
    """
    Extrae información de vehículos de las columnas del CSV.

    Args:
        row: Fila del DataFrame

    Returns:
        dict con información de vehículos
    """
    vehiculos_info = {
        'num_vehiculos': 0,
        'particular': 0,
        'publico': 0,
        'comercial': 0,
        'tipos': []
    }

    try:
        # Número de vehículos involucrados (convertir float a int)
        num_veh = clean_value(row.get('VEHÍCULOS INVOLUCRADOS EN EL SINIESTRO'))
        if num_veh:
            try:
                vehiculos_info['num_vehiculos'] = int(float(num_veh))
            except ValueError:
                pass

        # Cantidades por tipo de servicio (convertir float a int)
        particular = clean_value(row.get('PARTICULAR'))
        if particular:
            try:
                vehiculos_info['particular'] = int(float(particular))
            except ValueError:
                pass

        publico = clean_value(row.get('PÚBLICO'))
        if publico:
            try:
                vehiculos_info['publico'] = int(float(publico))
            except ValueError:
                pass

        comercial = clean_value(row.get('COMERCIAL'))
        if comercial:
            try:
                vehiculos_info['comercial'] = int(float(comercial))
            except ValueError:
                pass

        # Tipos de vehículos (TIPO DE VEHÍCULO REGISTRADO 1-6)
        tipos = []
        for i in range(1, 7):
            tipo_col = f'TIPO DE VEHÍCULO REGISTRADO {i}'
            tipo = clean_value(row.get(tipo_col))
            if tipo and tipo not in tipos:
                tipos.append(tipo)

        vehiculos_info['tipos'] = tipos

    except Exception as e:
        logger.warning(f"Error extrayendo info de vehículos: {e}")

    return vehiculos_info


def parse_victimas(row):
    """
    Extrae información de víctimas de las columnas del CSV.
    Las víctimas están en columnas como:
    - CONDICIÓN60, USUARIO VIAL, EDAD62, SEXO63
    - CONDICIÓN64, USUARIO VIAL65, EDAD69, SEXO70
    etc.

    Args:
        row: Fila del DataFrame

    Returns:
        Lista de diccionarios con datos de víctimas
    """
    victimas_data = []

    # Buscar todas las columnas que empiecen con "CONDICIÓN" (víctimas)
    condicion_cols = [col for col in row.index if col.startswith('CONDICIÓN') and col != 'CONDICION VÍA']

    for condicion_col in condicion_cols:
        condicion = clean_value(row.get(condicion_col))

        if not condicion or condicion.upper() in ['NORMAL', 'ILESO']:
            continue  # Skip si no hay víctima o está ilesa

        # Extraer número de la columna (ej: CONDICIÓN60 → 60)
        try:
            num = condicion_col.replace('CONDICIÓN', '').strip()
            if not num:
                continue
        except:
            continue

        # Buscar columnas relacionadas con este número
        # Nota: las columnas relacionadas no siempre tienen el mismo número
        # Vamos a buscar las más cercanas

        # Buscar USUARIO VIAL más cercano
        usuario_vial = None
        for col in row.index:
            if 'USUARIO VIAL' in col and col.startswith('USUARIO VIAL'):
                usuario_vial = clean_value(row.get(col))
                break

        # Buscar EDAD más cercana
        edad = None
        for col in row.index:
            if col.startswith('EDAD') and col != 'EDAD CONDUCTOR VEHÍCULO':
                edad_str = clean_value(row.get(col))
                if edad_str:
                    try:
                        edad = int(float(edad_str))
                        break
                    except ValueError:
                        pass

        # Buscar SEXO más cercano
        sexo = None
        for col in row.index:
            if col.startswith('SEXO') and col != 'SEXO CONDUCTOR VEHÍCULO':
                sexo = clean_value(row.get(col))
                if sexo:
                    break

        victima_data = {
            'condicion': condicion,
            'usuario_vial': usuario_vial,
            'edad': edad,
            'sexo': sexo
        }

        victimas_data.append(victima_data)

        # Solo procesar la primera víctima por simplicidad
        # (el CSV tiene estructura inconsistente para múltiples víctimas)
        break

    # Si no encontramos víctimas en columnas CONDICIÓN, revisar los contadores
    if not victimas_data:
        num_heridos = clean_value(row.get('NRO. HERIDOS'))
        num_fallecidos = clean_value(row.get('NRO. FALLECIDOS'))

        try:
            if num_heridos:
                heridos = int(num_heridos)
                for _ in range(heridos):
                    victimas_data.append({
                        'condicion': 'LESIONADO',
                        'usuario_vial': None,
                        'edad': None,
                        'sexo': None
                    })
        except ValueError:
            pass

        try:
            if num_fallecidos:
                fallecidos = int(num_fallecidos)
                for _ in range(fallecidos):
                    victimas_data.append({
                        'condicion': 'FALLECIDO',
                        'usuario_vial': None,
                        'edad': None,
                        'sexo': None
                    })
        except ValueError:
            pass

    return victimas_data


def validate_victima_condicion(condicion_str):
    """Valida y normaliza condición de víctima."""
    if not condicion_str:
        return Victima.Condicion.ILESO

    condicion_upper = condicion_str.upper()

    if any(word in condicion_upper for word in ['FALLECIDO', 'MUERTO', 'MUERTE']):
        return Victima.Condicion.FALLECIDO
    elif any(word in condicion_upper for word in ['HERIDO', 'LESIONADO', 'LESION']):
        return Victima.Condicion.LESIONADO
    else:
        return Victima.Condicion.ILESO


def validate_victima_sexo(sexo_str):
    """Valida y normaliza sexo de víctima."""
    if not sexo_str:
        return Victima.Sexo.NO_REGISTRA

    sexo_upper = sexo_str.upper()

    if any(word in sexo_upper for word in ['MASCULINO', 'HOMBRE', 'M', 'H']):
        return Victima.Sexo.HOMBRE
    elif any(word in sexo_upper for word in ['FEMENINO', 'MUJER', 'F']):
        return Victima.Sexo.MUJER
    else:
        return Victima.Sexo.NO_REGISTRA


def validate_victima_actor_vial(actor_str):
    """Valida y normaliza actor vial de víctima."""
    if not actor_str:
        return Victima.ActorVial.OTRO

    actor_upper = actor_str.upper()

    if any(word in actor_upper for word in ['PEATON', 'PEATÓN']):
        return Victima.ActorVial.PEATON
    elif any(word in actor_upper for word in ['MOTOCICLETA', 'MOTO', 'CONDUCTOR']):
        return Victima.ActorVial.MOTOCICLETA
    elif any(word in actor_upper for word in ['VEHICULO', 'VEHÍCULO', 'AUTOMOVIL', 'PASAJERO', 'ACOMPAÑANTE']):
        return Victima.ActorVial.VEH_LIVIANO
    elif any(word in actor_upper for word in ['CICLISTA', 'BICICLETA', 'CICL']):
        return Victima.ActorVial.CICLISTA
    elif any(word in actor_upper for word in ['SCOOTER']):
        return Victima.ActorVial.SCOOTER
    else:
        return Victima.ActorVial.OTRO


def import_from_excel(file_path, clear_existing=False, anio_filtro=None):
    """
    Importa datos de siniestros desde un archivo Excel o CSV.

    Args:
        file_path: Ruta al archivo Excel o CSV
        clear_existing: Si es True, elimina todos los datos existentes antes de importar
        anio_filtro: Si se especifica, solo importa datos de ese año

    Returns:
        dict con estadísticas de la importación
    """
    if clear_existing:
        logger.info("Eliminando datos existentes...")
        Victima.objects.all().delete()
        Siniestro.objects.all().delete()

    # Leer archivo Excel o CSV
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            # EXCEL: Leer TODAS las hojas y combinarlas
            logger.info("Detectado archivo Excel. Leyendo todas las hojas...")
            xl_file = pd.ExcelFile(file_path)
            logger.info(f"Hojas encontradas: {xl_file.sheet_names}")

            dfs = []
            for sheet_name in xl_file.sheet_names:
                logger.info(f"Leyendo hoja: {sheet_name}")
                sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)
                logger.info(f"  - {len(sheet_df)} filas en '{sheet_name}'")
                dfs.append(sheet_df)

            # Combinar todas las hojas
            df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Total después de combinar hojas: {len(df)} filas")
        else:
            # CSV: Intentar diferentes encodings
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='latin-1', low_memory=False)
                except:
                    df = pd.read_csv(file_path, encoding='cp1252', low_memory=False)
    except Exception as e:
        raise ExcelImportError(f"Error leyendo archivo: {e}")

    logger.info(f"Archivo leído: {len(df)} filas, {len(df.columns)} columnas")

    # DEBUG: Ver las primeras coordenadas leídas
    logger.debug(f"Primeras 3 coordenadas leídas:")
    for i in range(min(3, len(df))):
        lat = df.iloc[i].get('LATITUD')
        lon = df.iloc[i].get('LONGITUD')
        logger.debug(f"  Fila {i+1}: LAT='{lat}' LON='{lon}'")

    stats = {
        'siniestros_creados': 0,
        'victimas_creadas': 0,
        'errores': [],
        'filas_procesadas': 0,
    }

    siniestros_batch = []
    victimas_pending = []

    for idx, row in df.iterrows():
        stats['filas_procesadas'] += 1

        try:
            # Parsear fecha y hora
            fecha_hora = parse_fecha_hora(row.get('FECHA'), row.get('HORA'))
            if not fecha_hora:
                stats['errores'].append(f"Fila {idx + 2}: Fecha/hora inválida")
                continue

            # Filtrar por año si se especificó
            if anio_filtro:
                try:
                    if fecha_hora.year != int(anio_filtro):
                        continue
                except ValueError:
                    pass

            # Parsear coordenadas
            lat_raw = row.get('LATITUD')
            lon_raw = row.get('LONGITUD')
            latitud = parse_coordenada(lat_raw)
            longitud = parse_coordenada(lon_raw)

            if latitud == 0.0 or longitud == 0.0:
                # Log detallado para debugging
                logger.warning(f"Fila {idx + 2}: Coordenadas inválidas - lat_raw='{lat_raw}', lon_raw='{lon_raw}', latitud={latitud}, longitud={longitud}")
                stats['errores'].append(f"Fila {idx + 2}: Coordenadas inválidas")
                continue

            # Parsear severidad
            grado_severidad = parse_severidad(row.get('RESULTADOS  CONSECUENCIAS'))

            # Campos básicos
            via = clean_value(row.get('CALLE / AV. PRINCIPAL (1)')) or ''

            # Tipo y causa
            tipo_nombre = clean_value(row.get('TIPOLOGÍA'))
            causa_nombre = clean_value(row.get('CAUSAS'))

            tipo_siniestro = None
            if tipo_nombre:
                tipo_siniestro, _ = TipoSiniestro.objects.get_or_create(
                    nombre=tipo_nombre,
                    defaults={'activo': True}
                )

            causa_probable = None
            if causa_nombre:
                causa_probable, _ = Causa.objects.get_or_create(
                    nombre=causa_nombre,
                    defaults={'activo': True}
                )

            # Ubicación detallada
            zona = clean_value(row.get('ZONA')) or ''
            barrio = clean_value(row.get('BARRIO')) or ''
            parroquia = clean_value(row.get('PARROQUIA URBANA')) or ''
            parroquia_rural = clean_value(row.get('PARROQUIA RURAL')) or ''
            direccion_completa = clean_value(row.get('DIRECCION REGISTRADA COMPLETA')) or ''
            calle_principal = clean_value(row.get('CALLE / AV. PRINCIPAL (1)')) or ''
            calle_secundaria = clean_value(row.get('CALLE / AV. PRINCIPAL (2)')) or ''
            referencia = clean_value(row.get('REFERENCIA')) or ''

            # Condiciones
            condicion_calzada = clean_value(row.get('CONDICIÓN CALZADA')) or ''
            condicion_atmosferica = clean_value(row.get('CONDICIÓN ATMOSFÉRICA SINET')) or ''
            condicion_via = clean_value(row.get('CONDICION VÍA')) or ''
            luz_artificial = clean_value(row.get('LUZ ARTIFICIAL')) or ''
            lugar_en_via = clean_value(row.get('LUGAR EN LA VÍA')) or ''
            senalizacion_existente = clean_value(row.get('SEÑALIZACIÓN EXISTENTE')) or ''

            # Vehículos
            vehiculos_info = extract_vehiculos_info(row)
            tipos_vehiculos_str = ', '.join(vehiculos_info['tipos'])

            # Contadores (convertir float a int)
            num_heridos_raw = clean_value(row.get('NRO. HERIDOS'))
            num_heridos = int(float(num_heridos_raw)) if num_heridos_raw else 0

            num_fallecidos_raw = clean_value(row.get('NRO. FALLECIDOS'))
            num_fallecidos = int(float(num_fallecidos_raw)) if num_fallecidos_raw else 0

            num_alcohotest_raw = clean_value(row.get('NRO. PRUEBAS DE ALCOHOTEST'))
            num_alcohotest = int(float(num_alcohotest_raw)) if num_alcohotest_raw else 0

            num_detenidos_raw = clean_value(row.get('PERSONAS DETENIDAS'))
            num_detenidos = int(float(num_detenidos_raw)) if num_detenidos_raw else 0

            vehiculos_retenidos_raw = clean_value(row.get('VEHÍCULOS RETENIDOS'))
            vehiculos_retenidos = int(float(vehiculos_retenidos_raw)) if vehiculos_retenidos_raw else 0

            # Daños al bien público
            danos_bien_publico = clean_value(row.get('DAÑOS OCASIONADOS AL BIEN PÚBLICO'))
            tiene_danos = danos_bien_publico == 'SI' if danos_bien_publico else False
            descripcion_dano = clean_value(row.get('DESCRIPCIÓN DAÑO AL BIEN PÚBLICO')) or ''

            # VALIDACIÓN CRÍTICA: La severidad debe coincidir con los contadores de víctimas
            # Esto corrige inconsistencias donde el texto no coincide con los números
            if num_fallecidos > 0:
                # Si hay fallecidos, SIEMPRE debe ser CON_FALLECIDOS
                grado_severidad = Siniestro.Severidad.CON_FALLECIDOS
            elif num_heridos > 0:
                # Si hay heridos pero no fallecidos, debe ser CON_LESIONADOS
                grado_severidad = Siniestro.Severidad.CON_LESIONADOS
            else:
                # Sin víctimas, debe ser SOLO_DANOS
                grado_severidad = Siniestro.Severidad.SOLO_DANOS

            # Crear siniestro
            siniestro = Siniestro(
                fecha_hora=fecha_hora,
                latitud=latitud,
                longitud=longitud,
                via=via,
                grado_severidad=grado_severidad,
                tipo_siniestro=tipo_siniestro,
                causa_probable=causa_probable,
                # Ubicación
                zona=zona,
                barrio=barrio,
                parroquia=parroquia,
                parroquia_rural=parroquia_rural,
                direccion_completa=direccion_completa,
                calle_principal=calle_principal,
                calle_secundaria=calle_secundaria,
                referencia=referencia,
                # Condiciones
                condicion_calzada=condicion_calzada,
                condicion_atmosferica=condicion_atmosferica,
                condicion_via=condicion_via,
                luz_artificial=luz_artificial,
                lugar_en_via=lugar_en_via,
                senalizacion_existente=senalizacion_existente,
                # Vehículos
                num_vehiculos_involucrados=vehiculos_info['num_vehiculos'],
                vehiculos_particular=vehiculos_info['particular'],
                vehiculos_publico=vehiculos_info['publico'],
                vehiculos_comercial=vehiculos_info['comercial'],
                tipos_vehiculos=tipos_vehiculos_str,
                # Contadores
                num_heridos=num_heridos,
                num_fallecidos=num_fallecidos,
                num_pruebas_alcohotest=num_alcohotest,
                num_personas_detenidas=num_detenidos,
                vehiculos_retenidos=vehiculos_retenidos,
                # Daños
                tiene_danos_bien_publico=tiene_danos,
                descripcion_dano_bien_publico=descripcion_dano,
                # Datos adicionales (TODO: agregar más info si es necesario)
                datos_adicionales={}
            )

            siniestros_batch.append(siniestro)

            # Parsear víctimas
            victimas_data = parse_victimas(row)
            if victimas_data:
                victimas_pending.append((len(siniestros_batch) - 1, victimas_data))

        except Exception as e:
            stats['errores'].append(f"Fila {idx + 2}: {str(e)}")
            logger.error(f"Error en fila {idx + 2}: {e}", exc_info=True)
            continue

    # Guardar siniestros en batch
    if siniestros_batch:
        Siniestro.objects.bulk_create(siniestros_batch)
        stats['siniestros_creados'] = len(siniestros_batch)
        logger.info(f"Siniestros creados: {stats['siniestros_creados']}")

        # Recuperar siniestros recién creados
        created_siniestros = list(Siniestro.objects.order_by('-id')[:len(siniestros_batch)])
        created_siniestros.reverse()

        # Crear víctimas
        victimas_batch = []
        for idx, victimas_data in victimas_pending:
            if idx < len(created_siniestros):
                siniestro = created_siniestros[idx]
                for v_data in victimas_data:
                    try:
                        victima = Victima(
                            siniestro=siniestro,
                            edad=v_data.get('edad'),
                            condicion=validate_victima_condicion(v_data.get('condicion')),
                            sexo=validate_victima_sexo(v_data.get('sexo')),
                            actor_vial=validate_victima_actor_vial(v_data.get('usuario_vial')),
                        )
                        victimas_batch.append(victima)
                    except Exception as e:
                        stats['errores'].append(f"Error creando víctima: {str(e)}")

        if victimas_batch:
            Victima.objects.bulk_create(victimas_batch)
            stats['victimas_creadas'] = len(victimas_batch)
            logger.info(f"Víctimas creadas: {stats['victimas_creadas']}")

    logger.info(f"Importación completada: {stats}")
    return stats
