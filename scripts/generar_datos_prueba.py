#!/usr/bin/env python
"""
Genera CSV de siniestros y victimas realistas para importacion masiva.

Basado en scripts/load_demo_data.py (NO MODIFICAR ESE ARCHIVO).
Este script genera el CSV ejemplo_siniestros.csv con la misma logica.

Rango: 2020 a 2026
Volumen: ~4,000 por año (Total ~28,000)
Ubicacion: Loja, Ecuador (Lat: -4.007, Lon: -79.201)

Uso:
    python scripts/generar_datos_prueba.py
"""

import csv
from datetime import datetime, timedelta
from random import randint, choice, uniform
from pathlib import Path


def main():
    # Determinar ruta absoluta del archivo de salida
    BASE_DIR = Path(__file__).resolve().parent.parent
    filename = BASE_DIR / 'scripts' / 'ejemplo_siniestros.csv'
    
    records_per_year = 4000
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    # --- Datos base (IDENTICOS a load_demo_data.py) ---
    tipos = [
        "Choque Vehicular", "Caida", "Accidente Laboral", "Atropellamiento",
        "Volcamiento", "Incendio", "Colision Multiple",
    ]
    
    causas = [
        "Exceso de velocidad", "Imprudencia del conductor", "Distraccion (celular/radio)",
        "Via resbaladiza o mojada", "Falla mecanica", "Visibilidad reducida",
        "Inobservancia de senales", "Estado de embriaguez", "Fatiga del conductor",
        "Mal estado de la via", "Equipo de seguridad deficiente", "Factores externos",
    ]
    
    vias = [
        "Av. Orillas del Zamora", "Av. Cuxibamba", "Av. 8 de Diciembre",
        "Av. Manuel Agustin Aguirre", "Av. Universitaria", "Av. Reinaldo Espinosa",
        "Av. Pio Jaramillo", "Av. Gran Colombia", "Av. Metropolitana",
        "Av. Rosa Hermosa", "Calle Bolivar", "Calle Miguel Riofrio",
        "Calle Ramon Borrero", "Calle 10 de Agosto", "Calle 18 de Noviembre",
        "Calle Sucre", "Calle Quito", "Calle Rocafuerte", "Calle Saraguro",
        "Via Loja - Zamora", "Via Loja - Catamayo", "Ruta 35",
        "Calle Montufar", "Calle Mercadillo", "Av. Isidro Ayora",
        "Calle Colon", "Calle Imbabura", "Calle Azogues",
    ]
    
    severidades = ['CON_FALLECIDOS', 'CON_LESIONADOS', 'SOLO_DANOS']
    
    # Coordenadas base Loja
    LOJA_LAT = -4.007
    LOJA_LON = -79.201
    LAT_VARIATION = 0.030
    LON_VARIATION = 0.030
    
    # Valores para victimas
    sexos = ['HOMBRE', 'MUJER', 'NO_REGISTRA']
    actores_viales = ['PEATON', 'MOTOCICLETA', 'VEH_LIVIANO', 'CICLISTA', 'SCOOTER', 'OTRO']
    
    total_target = len(years) * records_per_year
    print(f"Generando {total_target:,} registros en {filename}...")
    
    # Headers del CSV
    headers = [
        'fecha_hora', 'latitud', 'longitud', 'via', 
        'grado_severidad', 'tipo_siniestro', 'causa_probable',
        # Victima 1
        'victima1_edad', 'victima1_condicion', 'victima1_sexo', 'victima1_actor_vial',
        # Victima 2
        'victima2_edad', 'victima2_condicion', 'victima2_sexo', 'victima2_actor_vial',
        # Victima 3
        'victima3_edad', 'victima3_condicion', 'victima3_sexo', 'victima3_actor_vial',
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for year in years:
            print(f"   Generando datos para el año {year}...")
            
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59)
            
            # Si es el año actual, limitar hasta hoy
            if year == datetime.now().year:
                end_date = datetime.now()
            
            delta_seconds = int((end_date - start_date).total_seconds())
            
            for _ in range(records_per_year):
                # Generar fecha aleatoria
                random_second = randint(0, delta_seconds)
                fecha_hora = start_date + timedelta(seconds=random_second)
                
                # Datos del siniestro
                lat = LOJA_LAT + uniform(-LAT_VARIATION, LAT_VARIATION)
                lng = LOJA_LON + uniform(-LON_VARIATION, LON_VARIATION)
                severidad = choice(severidades)
                
                row = [
                    fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{lat:.6f}",
                    f"{lng:.6f}",
                    choice(vias),
                    severidad,
                    choice(tipos),
                    choice(causas),
                ]
                
                # Generar victimas segun severidad (LOGICA IDENTICA a load_demo_data.py)
                fallecidos = 0
                lesionados = 0
                
                if severidad == 'CON_FALLECIDOS':
                    fallecidos = randint(1, 2)
                    lesionados = randint(0, 2)
                elif severidad == 'CON_LESIONADOS':
                    lesionados = randint(1, 3)
                else:  # SOLO_DANOS
                    if randint(1, 10) == 1:  # 10% tiene un ileso
                        lesionados = 1
                
                victimas = []
                
                # Crear fallecidos
                for _ in range(fallecidos):
                    victimas.append({
                        'edad': randint(18, 85),
                        'condicion': 'FALLECIDO',
                        'sexo': choice(sexos),
                        'actor_vial': choice(actores_viales)
                    })
                
                # Crear lesionados
                for _ in range(lesionados):
                    victimas.append({
                        'edad': randint(5, 80),
                        'condicion': 'LESIONADO',
                        'sexo': choice(sexos),
                        'actor_vial': choice(actores_viales)
                    })
                
                # Agregar victimas al CSV (hasta 3)
                for i in range(3):
                    if i < len(victimas):
                        v = victimas[i]
                        row.extend([v['edad'], v['condicion'], v['sexo'], v['actor_vial']])
                    else:
                        row.extend(['', '', '', ''])
                
                writer.writerow(row)
    
    print("¡Generación completada!")
    print(f"\nArchivo: {filename}")
    print(f"Total registros: {total_target:,}")
    print(f"Años: {years[0]} - {years[-1]}")


if __name__ == '__main__':
    main()
