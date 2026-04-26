"""
Configuración del panel de administración de Django para la app ``siniestros``.

Registra los modelos Siniestro, Causa, TipoSiniestro y Victima con
interfaces personalizadas, acciones de borrado lógico e importación
integrada de datos desde archivos CSV/Excel.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Siniestro, Victima, Causa, TipoSiniestro
from .excel_import import import_from_excel
import os
import logging

logger = logging.getLogger(__name__)

# Personalización del sitio admin
admin.site.site_header = 'Visor de Siniestros - Administración'
admin.site.site_title = 'Visor de Siniestros'
admin.site.index_title = 'Panel de Administración'


@admin.register(Causa)
class CausaAdmin(admin.ModelAdmin):
    """Administración del catálogo de causas probables con borrado lógico."""

    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    actions = ['dar_de_baja', 'reactivar']

    @admin.action(description="Dar de baja las causas seleccionadas")
    def dar_de_baja(self, request, queryset):
        """Desactiva las causas seleccionadas (borrado lógico)."""
        queryset.update(activo=False)

    @admin.action(description="Reactivar las causas seleccionadas")
    def reactivar(self, request, queryset):
        """Reactiva las causas que habían sido dadas de baja."""
        queryset.update(activo=True)


@admin.register(TipoSiniestro)
class TipoSiniestroAdmin(admin.ModelAdmin):
    """Administración del catálogo de tipos de siniestro con borrado lógico."""

    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    actions = ['dar_de_baja', 'reactivar']

    @admin.action(description="Dar de baja los tipos seleccionados")
    def dar_de_baja(self, request, queryset):
        """Desactiva los tipos seleccionados (borrado lógico)."""
        queryset.update(activo=False)

    @admin.action(description="Reactivar los tipos seleccionados")
    def reactivar(self, request, queryset):
        """Reactiva los tipos que habían sido dados de baja."""
        queryset.update(activo=True)


class VictimaInline(admin.TabularInline):
    """Víctimas mostradas en línea dentro del detalle de un siniestro."""

    model = Victima
    extra = 0
    readonly_fields = ('condicion', 'sexo', 'actor_vial')
    fields = ('condicion', 'sexo', 'actor_vial', 'edad')


@admin.register(Siniestro)
class SiniestroAdmin(admin.ModelAdmin):
    """
    Configuración del admin de Siniestros.

    Incluye:
    - Vista en línea de víctimas (``VictimaInline``)
    - Importación de datos CSV/Excel a través de vista personalizada
    - Fieldsets organizados por categoría
    - Filtros, búsqueda y jerarquía por fecha
    """

    inlines = [VictimaInline]

    list_display = ('fecha_hora', 'barrio', 'parroquia', 'via', 'grado_severidad', 'tipo_siniestro', 'num_vehiculos_involucrados')
    list_filter = ('grado_severidad', 'tipo_siniestro', 'causa_probable', 'fecha_hora', 'barrio', 'parroquia', 'condicion_calzada')
    search_fields = ('via', 'barrio', 'parroquia', 'direccion_completa', 'id')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('grado_severidad', 'num_heridos', 'num_fallecidos', 'num_vehiculos_involucrados')

    fieldsets = (
        ('Información Básica', {
            'fields': ('fecha_hora', 'grado_severidad', 'tipo_siniestro', 'causa_probable')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud', 'zona', 'barrio', 'parroquia', 'parroquia_rural',
                      'direccion_completa', 'via', 'calle_principal', 'calle_secundaria', 'referencia')
        }),
        ('Condiciones del Evento', {
            'fields': ('condicion_calzada', 'condicion_atmosferica', 'condicion_via',
                      'luz_artificial', 'lugar_en_via', 'senalizacion_existente'),
            'classes': ('collapse',)
        }),
        ('Vehículos', {
            'fields': ('num_vehiculos_involucrados', 'vehiculos_particular', 'vehiculos_publico',
                      'vehiculos_comercial', 'tipos_vehiculos', 'vehiculos_retenidos'),
            'classes': ('collapse',)
        }),
        ('Víctimas y Personas', {
            'fields': ('num_heridos', 'num_fallecidos', 'num_personas_detenidas', 'num_pruebas_alcohotest')
        }),
        ('Daños', {
            'fields': ('tiene_danos_bien_publico', 'descripcion_dano_bien_publico'),
            'classes': ('collapse',)
        }),
    )

    change_list_template = 'admin/siniestros/siniestro_changelist.html'

    def get_urls(self):
        """Agrega la URL personalizada para la vista de importación CSV/Excel."""
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='siniestros_siniestro_import_csv'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        """
        Vista para importar archivos CSV o Excel desde el panel de administración.

        Soporta archivos ``.csv``, ``.xlsx`` y ``.xls``. Guarda el archivo en un
        temporal, invoca ``import_from_excel()`` y muestra los resultados al usuario.

        Args:
            request: HttpRequest de Django.

        Returns:
            HttpResponse con la plantilla de upload y resultados de la importación.
        """
        context = {
            'title': 'Importar Siniestros desde CSV/Excel',
            'opts': self.model._meta,
            'has_permission': True,
        }

        if request.method == 'POST':
            uploaded_file = request.FILES.get('csv_file')
            clear_existing = request.POST.get('clear_existing') == 'on'

            if not uploaded_file:
                messages.error(request, 'Por favor seleccione un archivo.')
                return render(request, 'admin/siniestros/csv_upload.html', context)

            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            allowed_extensions = ['.csv', '.xlsx', '.xls']

            if file_ext not in allowed_extensions:
                messages.error(request, 'El archivo debe ser CSV o Excel (.csv, .xlsx, .xls)')
                return render(request, 'admin/siniestros/csv_upload.html', context)

            try:
                anio_filtro = request.POST.get('anio_filtro')

                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                    for chunk in uploaded_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name

                try:
                    results = import_from_excel(
                        tmp_file_path,
                        clear_existing=clear_existing,
                        anio_filtro=anio_filtro
                    )
                    context['results'] = results

                    if results['errores']:
                        errores_mostrados = results['errores'][:10]
                        mensaje_errores = '<br>'.join(errores_mostrados)
                        if len(results['errores']) > 10:
                            mensaje_errores += f'<br>... y {len(results["errores"]) - 10} errores más'
                        messages.warning(
                            request,
                            f"Importación completada con {len(results['errores'])} errores. "
                            f"Se crearon {results['siniestros_creados']} siniestros y {results['victimas_creadas']} víctimas.<br>"
                            f"Errores:<br>{mensaje_errores}"
                        )
                    else:
                        messages.success(
                            request,
                            f"Importación exitosa. Se crearon {results['siniestros_creados']} siniestros y "
                            f"{results['victimas_creadas']} víctimas."
                        )
                finally:
                    try:
                        os.unlink(tmp_file_path)
                    except OSError:
                        pass

            except Exception as e:
                logger.exception("Error al procesar archivo de importación")
                messages.error(request, f'Error al procesar el archivo: {str(e)}')

        return render(request, 'admin/siniestros/csv_upload.html', context)
