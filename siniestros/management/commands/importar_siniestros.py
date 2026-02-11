"""
Comando Django para importar siniestros desde Excel/CSV.

Uso:
    python manage.py importar_siniestros archivo.xlsx --year=2025
    python manage.py importar_siniestros archivo.csv --clear
    python manage.py importar_siniestros archivo.xlsx --validate-only
"""

from django.core.management.base import BaseCommand, CommandError
from siniestros.excel_import import import_from_excel, ExcelImportError
import pandas as pd


class Command(BaseCommand):
    help = 'Importa siniestros desde un archivo Excel o CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Ruta al archivo Excel (.xlsx, .xls) o CSV'
        )
        parser.add_argument(
            '--year',
            type=str,
            default=None,
            help='Filtrar solo registros de este año (ej: --year=2024)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todos los datos existentes antes de importar'
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar el archivo sin importar (muestra columnas y primeras filas)'
        )
        parser.add_argument(
            '--show-columns',
            action='store_true',
            help='Mostrar todas las columnas del archivo'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        year = options['year']
        clear = options['clear']
        validate_only = options['validate_only']
        show_columns = options['show_columns']

        self.stdout.write(self.style.SUCCESS(f'\n📂 Archivo: {file_path}'))

        # Validar que el archivo existe
        import os
        if not os.path.exists(file_path):
            raise CommandError(f'❌ El archivo no existe: {file_path}')

        # Modo validación: Solo revisar el archivo sin importar
        if validate_only or show_columns:
            self.validate_file(file_path, show_columns)
            return

        # Confirmar si va a limpiar datos existentes
        if clear:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  ADVERTENCIA: Se eliminarán TODOS los siniestros y víctimas existentes.'
                )
            )
            confirm = input('¿Estás seguro? Escribe "SI" para confirmar: ')
            if confirm.strip().upper() != 'SI':
                self.stdout.write(self.style.ERROR('❌ Importación cancelada'))
                return

        # Ejecutar importación
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando importación...'))
        if year:
            self.stdout.write(f'📅 Filtrando por año: {year}')
        if clear:
            self.stdout.write(self.style.WARNING('🗑️  Limpiando datos existentes...'))

        try:
            stats = import_from_excel(
                file_path=file_path,
                clear_existing=clear,
                anio_filtro=year
            )

            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS('\n✅ Importación completada!'))
            self.stdout.write(f'\n📊 Resultados:')
            self.stdout.write(f'  • Siniestros creados: {stats["siniestros_creados"]}')
            self.stdout.write(f'  • Víctimas creadas: {stats["victimas_creadas"]}')
            self.stdout.write(f'  • Filas procesadas: {stats["filas_procesadas"]}')

            if stats['errores']:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  Errores: {len(stats["errores"])}')
                )
                if len(stats['errores']) <= 10:
                    for error in stats['errores']:
                        self.stdout.write(f'    - {error}')
                else:
                    for error in stats['errores'][:10]:
                        self.stdout.write(f'    - {error}')
                    self.stdout.write(f'    ... y {len(stats["errores"]) - 10} errores más')

            # Tasa de éxito
            if stats['filas_procesadas'] > 0:
                tasa_exito = (stats['siniestros_creados'] / stats['filas_procesadas']) * 100
                self.stdout.write(f'\n✅ Tasa de éxito: {tasa_exito:.1f}%')

        except ExcelImportError as e:
            raise CommandError(f'❌ Error en la importación: {e}')

    def validate_file(self, file_path, show_all_columns=False):
        """Valida el archivo y muestra información sobre su estructura."""
        self.stdout.write(self.style.SUCCESS('\n🔍 Validando archivo...'))

        try:
            # Leer archivo
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                xl_file = pd.ExcelFile(file_path)
                self.stdout.write(f'📄 Tipo: Excel')
                self.stdout.write(f'📋 Hojas: {len(xl_file.sheet_names)}')
                for sheet_name in xl_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    self.stdout.write(f'   • {sheet_name}: {len(df)} filas')

                # Leer primera hoja para análisis
                df = pd.read_excel(file_path, sheet_name=xl_file.sheet_names[0])
            else:
                df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
                self.stdout.write(f'📄 Tipo: CSV')

            self.stdout.write(f'📊 Filas totales: {len(df)}')
            self.stdout.write(f'📊 Columnas totales: {len(df.columns)}')

            # Columnas requeridas
            columnas_requeridas = ['FECHA', 'HORA', 'LATITUD', 'LONGITUD']
            columnas_importantes = [
                'TIPOLOGÍA', 'CAUSAS', 'RESULTADOS  CONSECUENCIAS',
                'CALLE / AV. PRINCIPAL (1)'
            ]

            self.stdout.write('\n✅ Columnas Requeridas:')
            for col in columnas_requeridas:
                if col in df.columns:
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {col}'))
                else:
                    self.stdout.write(self.style.ERROR(f'   ✗ {col} (FALTA)'))

            self.stdout.write('\n📌 Columnas Importantes:')
            for col in columnas_importantes:
                if col in df.columns:
                    self.stdout.write(f'   ✓ {col}')
                else:
                    self.stdout.write(self.style.WARNING(f'   ? {col} (opcional)'))

            # Mostrar todas las columnas si se solicita
            if show_all_columns:
                self.stdout.write('\n📋 Todas las Columnas:')
                for i, col in enumerate(df.columns, 1):
                    self.stdout.write(f'   {i}. {col}')

            # Mostrar primeras filas
            self.stdout.write('\n📝 Primeras 3 filas (columnas clave):')
            columnas_mostrar = ['FECHA', 'HORA', 'LATITUD', 'LONGITUD', 'TIPOLOGÍA', 'CAUSAS']
            columnas_disponibles = [c for c in columnas_mostrar if c in df.columns]

            self.stdout.write(f'\n{" | ".join(columnas_disponibles)}')
            self.stdout.write('-' * 80)

            for idx, row in df.head(3).iterrows():
                valores = [str(row[col])[:20] for col in columnas_disponibles]
                self.stdout.write(f'{" | ".join(valores)}')

            # Verificar años disponibles
            if 'FECHA' in df.columns:
                self.stdout.write('\n📅 Años disponibles en el archivo:')
                try:
                    # Intentar parsear fechas
                    if df['FECHA'].dtype == 'object':
                        # Formato string DD/MM/YYYY
                        df['año'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce').dt.year
                    else:
                        # Formato datetime de Excel
                        df['año'] = pd.to_datetime(df['FECHA']).dt.year

                    años_count = df['año'].value_counts().sort_index()
                    for año, count in años_count.items():
                        if pd.notna(año):
                            self.stdout.write(f'   • {int(año)}: {count} siniestros')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   No se pudieron parsear las fechas: {e}'))

            self.stdout.write(self.style.SUCCESS('\n✅ Validación completada'))
            self.stdout.write('\n💡 Para importar usa:')
            self.stdout.write(f'   python manage.py importar_siniestros "{file_path}"')
            self.stdout.write(f'   python manage.py importar_siniestros "{file_path}" --year=2025')

        except Exception as e:
            raise CommandError(f'❌ Error leyendo archivo: {e}')
