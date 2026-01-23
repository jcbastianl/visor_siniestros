"""
Módulo para importar datos de siniestros desde archivos CSV.

Este módulo proporciona funciones para parsear, validar y crear
registros de Siniestro y Victima desde un archivo CSV.
"""

import csv
import json
from datetime import datetime
from io import TextIOWrapper
from django.utils import timezone
from .models import Siniestro, Victima, TipoSiniestro, Causa


class CSVImportError(Exception):
    """Excepción personalizada para errores de importación CSV."""
    pass


def parse_datetime(value):
    """
    Parsea una cadena de fecha/hora a un objeto datetime con timezone.
    Formatos soportados:
    - YYYY-MM-DD HH:MM:SS
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DDTHH:MM:SS
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
    ]
    
    value = value.strip()
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except ValueError:
            continue
    
    raise ValueError(f"Formato de fecha inválido: '{value}'. Use YYYY-MM-DD HH:MM:SS")


def get_or_create_tipo_siniestro(nombre):
    """Obtiene o crea un TipoSiniestro por nombre."""
    if not nombre or nombre.strip() == '':
        return None
    
    obj, _ = TipoSiniestro.objects.get_or_create(
        nombre=nombre.strip(),
        defaults={'activo': True}
    )
    return obj


def get_or_create_causa(nombre):
    """Obtiene o crea una Causa por nombre."""
    if not nombre or nombre.strip() == '':
        return None
    
    obj, _ = Causa.objects.get_or_create(
        nombre=nombre.strip(),
        defaults={'activo': True}
    )
    return obj


def validate_severidad(value):
    """Valida y normaliza el grado de severidad."""
    value = value.strip().upper()
    
    valid_values = {
        'CON_FALLECIDOS': Siniestro.Severidad.CON_FALLECIDOS,
        'CON FALLECIDOS': Siniestro.Severidad.CON_FALLECIDOS,
        'FALLECIDOS': Siniestro.Severidad.CON_FALLECIDOS,
        'CON_LESIONADOS': Siniestro.Severidad.CON_LESIONADOS,
        'CON LESIONADOS': Siniestro.Severidad.CON_LESIONADOS,
        'LESIONADOS': Siniestro.Severidad.CON_LESIONADOS,
        'SOLO_DANOS': Siniestro.Severidad.SOLO_DANOS,
        'SOLO DANOS': Siniestro.Severidad.SOLO_DANOS,
        'SOLO_DAÑOS': Siniestro.Severidad.SOLO_DANOS,
        'DANOS': Siniestro.Severidad.SOLO_DANOS,
        'DAÑOS': Siniestro.Severidad.SOLO_DANOS,
    }
    
    if value in valid_values:
        return valid_values[value]
    
    raise ValueError(f"Severidad inválida: '{value}'. Valores permitidos: CON_FALLECIDOS, CON_LESIONADOS, SOLO_DANOS")


def validate_condicion(value):
    """Valida y normaliza la condición de víctima."""
    value = value.strip().upper()
    
    valid_values = {
        'FALLECIDO': Victima.Condicion.FALLECIDO,
        'LESIONADO': Victima.Condicion.LESIONADO,
        'ILESO': Victima.Condicion.ILESO,
    }
    
    if value in valid_values:
        return valid_values[value]
    
    raise ValueError(f"Condición inválida: '{value}'. Valores permitidos: FALLECIDO, LESIONADO, ILESO")


def validate_sexo(value):
    """Valida y normaliza el sexo de víctima."""
    if not value or value.strip() == '':
        return Victima.Sexo.NO_REGISTRA
    
    value = value.strip().upper()
    
    valid_values = {
        'HOMBRE': Victima.Sexo.HOMBRE,
        'H': Victima.Sexo.HOMBRE,
        'M': Victima.Sexo.HOMBRE,
        'MASCULINO': Victima.Sexo.HOMBRE,
        'MUJER': Victima.Sexo.MUJER,
        'F': Victima.Sexo.MUJER,
        'FEMENINO': Victima.Sexo.MUJER,
        'NO_REGISTRA': Victima.Sexo.NO_REGISTRA,
        'NO REGISTRA': Victima.Sexo.NO_REGISTRA,
        '': Victima.Sexo.NO_REGISTRA,
    }
    
    if value in valid_values:
        return valid_values[value]
    
    return Victima.Sexo.NO_REGISTRA


def validate_actor_vial(value):
    """Valida y normaliza el actor vial de víctima."""
    if not value or value.strip() == '':
        return Victima.ActorVial.OTRO
    
    value = value.strip().upper()
    
    valid_values = {
        'PEATON': Victima.ActorVial.PEATON,
        'PEATÓN': Victima.ActorVial.PEATON,
        'MOTOCICLETA': Victima.ActorVial.MOTOCICLETA,
        'MOTO': Victima.ActorVial.MOTOCICLETA,
        'VEH_LIVIANO': Victima.ActorVial.VEH_LIVIANO,
        'VEHICULO': Victima.ActorVial.VEH_LIVIANO,
        'VEHÍCULO': Victima.ActorVial.VEH_LIVIANO,
        'AUTO': Victima.ActorVial.VEH_LIVIANO,
        'CICLISTA': Victima.ActorVial.CICLISTA,
        'BICICLETA': Victima.ActorVial.CICLISTA,
        'SCOOTER': Victima.ActorVial.SCOOTER,
        'OTRO': Victima.ActorVial.OTRO,
    }
    
    if value in valid_values:
        return valid_values[value]
    
    return Victima.ActorVial.OTRO


def parse_victimas_columns(row, max_victimas=20):
    """
    Parsea víctimas desde columnas simples en lugar de JSON.
    Busca columnas victima1_*, victima2_*, etc.
    
    Returns: Lista de diccionarios con datos de víctimas
    """
    victimas_data = []
    i = 1
    
    while True:
        prefix = f'victima{i}_'
        
        # Verificar si existe alguna columna para este índice
        # Buscamos claves que empiecen con el prefijo en la fila actual
        # Pero como row es un diccionario, podemos chequear claves especificas
        # Si no existe 'victimaX_condicion' ni 'victimaX_edad', asumimos que no hay mas
        
        has_data = False
        possible_fields = ['condicion', 'edad', 'sexo', 'actor_vial']
        
        # Verificar si alguna columna de este indice tiene valor
        for field in possible_fields:
            if row.get(f'{prefix}{field}', '').strip():
                 has_data = True
                 break
        
        if not has_data:
            # Si llegamos a victimaX y no tiene datos, intentamos ver si quizas
            # el usuario salto un numero (raro pero posible) o terminamos.
            # Para seguridad, si no encontramos la 1, seguimos. Si encontramos la 1 pero no la 2, paramos.
            if i > 50: # Limite de seguridad absurdo para evitar loop infinito
                break
            
            # Simple check: si no hay condicion ni edad, asumimos fin, SALVO que haya gaps.
            # Asumiremos que son consecutivos.
            break

        # Procesar
        condicion = row.get(f'{prefix}condicion', '').strip()
        # Si hay datos pero no condicion default, podemos poner ILESO o skipear?
        # Mejor procesamos lo que haya.
        
        if not condicion and not has_data:
             i += 1
             continue

        victima = {
            'condicion': condicion if condicion else 'ILESO', # Default si olvidaron condicion
            'edad': None,
            'sexo': '',
            'actor_vial': '',
        }
        
        # Parsear edad (puede estar vacía)
        edad_str = row.get(f'{prefix}edad', '').strip()
        if edad_str:
            try:
                victima['edad'] = int(edad_str)
            except ValueError:
                pass  # Dejar como None si no es un número válido
        
        # Parsear sexo y actor_vial
        victima['sexo'] = row.get(f'{prefix}sexo', '').strip()
        victima['actor_vial'] = row.get(f'{prefix}actor_vial', '').strip()
        
        victimas_data.append(victima)
        i += 1
    
    return victimas_data


def import_csv(csv_file, clear_existing=False, anio_filtro=None):
    """
    Importa datos de siniestros desde un archivo CSV.
    
    Args:
        csv_file: Archivo CSV (puede ser un archivo abierto o un InMemoryUploadedFile)
        clear_existing: Si es True, elimina todos los datos existentes antes de importar
    
    Returns:
        dict con estadísticas de la importación:
        - siniestros_creados: número de siniestros creados
        - victimas_creadas: número de víctimas creadas
        - errores: lista de errores encontrados
        - filas_procesadas: número total de filas procesadas
    """
    
    if clear_existing:
        Victima.objects.all().delete()
        Siniestro.objects.all().delete()
    
    # Manejar diferentes tipos de archivo
    if hasattr(csv_file, 'read'):
        # Es un archivo de Django (InMemoryUploadedFile)
        if hasattr(csv_file, 'seek'):
            csv_file.seek(0)
        
        # Intentar decodificar como UTF-8
        try:
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8-sig')  # utf-8-sig maneja BOM
            lines = content.splitlines()
        except UnicodeDecodeError:
            csv_file.seek(0)
            content = csv_file.read().decode('latin-1')
            lines = content.splitlines()
        
        reader = csv.DictReader(lines)
    else:
        reader = csv.DictReader(csv_file)
    
    stats = {
        'siniestros_creados': 0,
        'victimas_creadas': 0,
        'errores': [],
        'filas_procesadas': 0,
    }
    
    siniestros_batch = []
    victimas_pending = []  # Lista de (índice_siniestro, datos_victimas)
    
    for row_num, row in enumerate(reader, start=2):  # start=2 porque fila 1 es header
        stats['filas_procesadas'] += 1
        
        try:
            # Campos obligatorios
            fecha_hora = parse_datetime(row.get('fecha_hora', ''))
            
            # Filtrar por año si se especificó
            if anio_filtro:
                try:
                    anio_filtro_int = int(anio_filtro)
                    if fecha_hora.year != anio_filtro_int:
                        # Saltar registros que no coincidan con el año
                        continue
                except ValueError:
                    # Si el filtro de año no es un número válido, ignorarlo (o loguearlo)
                    pass

            latitud = float(row.get('latitud', 0))
            longitud = float(row.get('longitud', 0))
            grado_severidad = validate_severidad(row.get('grado_severidad', ''))
            
            # Campos opcionales
            via = row.get('via', '').strip()
            tipo_nombre = row.get('tipo_siniestro', '').strip()
            causa_nombre = row.get('causa_probable', '').strip()
            
            # Crear el siniestro
            siniestro = Siniestro(
                fecha_hora=fecha_hora,
                latitud=latitud,
                longitud=longitud,
                via=via,
                grado_severidad=grado_severidad,
                tipo_siniestro=get_or_create_tipo_siniestro(tipo_nombre),
                causa_probable=get_or_create_causa(causa_nombre),
            )
            
            siniestros_batch.append(siniestro)
            
            # Parsear víctimas desde columnas (victima1_*, victima2_*, etc.)
            victimas_data = parse_victimas_columns(row)
            if victimas_data:
                victimas_pending.append((len(siniestros_batch) - 1, victimas_data))
            
        except Exception as e:
            stats['errores'].append(f"Fila {row_num}: {str(e)}")
            continue
    
    # Guardar siniestros en batch
    if siniestros_batch:
        Siniestro.objects.bulk_create(siniestros_batch)
        stats['siniestros_creados'] = len(siniestros_batch)
        
        # Refrescar los IDs después del bulk_create
        # Necesitamos recuperar los siniestros recién creados
        created_siniestros = list(Siniestro.objects.order_by('-id')[:len(siniestros_batch)])
        created_siniestros.reverse()  # Ordenar del más antiguo al más nuevo
        
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
                            condicion=validate_condicion(v_data.get('condicion', 'ILESO')),
                            sexo=validate_sexo(v_data.get('sexo', '')),
                            actor_vial=validate_actor_vial(v_data.get('actor_vial', '')),
                        )
                        victimas_batch.append(victima)
                    except Exception as e:
                        stats['errores'].append(f"Error en víctima del siniestro {idx + 2}: {str(e)}")
        
        if victimas_batch:
            Victima.objects.bulk_create(victimas_batch)
            stats['victimas_creadas'] = len(victimas_batch)
    
    return stats
