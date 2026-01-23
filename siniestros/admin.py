from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Siniestro, Victima, Causa, TipoSiniestro
from .csv_import import import_csv

@admin.register(Causa)
class CausaAdmin(admin.ModelAdmin):
    # En la lista, mostramos el nombre y si está activo
    list_display = ('nombre', 'activo')
    
    # Añadimos un filtro para ver solo los activos o inactivos
    list_filter = ('activo',)
    
    # Habilitamos la búsqueda por nombre
    search_fields = ('nombre',)
    
    # Acción para "dar de baja" en masa
    def dar_de_baja(self, request, queryset):
        queryset.update(activo=False)
    dar_de_baja.short_description = "Dar de baja las causas seleccionadas"

    # Acción para "reactivar" en masa
    def reactivar(self, request, queryset):
        queryset.update(activo=True)
    reactivar.short_description = "Reactivar las causas seleccionadas"

    actions = [dar_de_baja, reactivar]

@admin.register(TipoSiniestro)
class TipoSiniestroAdmin(admin.ModelAdmin):

    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

    def dar_de_baja(self, request, queryset):
        queryset.update(activo=False)
    dar_de_baja.short_description = "Dar de baja los tipos seleccionados"

    def reactivar(self, request, queryset):
        queryset.update(activo=True)
    reactivar.short_description = "Reactivar los tipos seleccionados"

    actions = [dar_de_baja, reactivar]

class VictimaInline(admin.TabularInline):
    """
    Esto le dice al admin: "Muestra los modelos 'Victima' 
    en formato de tabla dentro de 'Siniestro'".
    """
    model = Victima
    extra = 0 
    
    readonly_fields = ('condicion', 'sexo', 'actor_vial')
    
    fields = ('condicion', 'sexo', 'actor_vial', 'edad')

@admin.register(Siniestro)
class SiniestroAdmin(admin.ModelAdmin):
    """
    Configuración principal del admin de Siniestros.
    """
    inlines = [VictimaInline]

    list_display = ('fecha_hora', 'via', 'grado_severidad', 'tipo_siniestro')
    
    list_filter = ('grado_severidad', 'tipo_siniestro', 'causa_probable', 'fecha_hora')
    
    search_fields = ('via', 'id')
    
    date_hierarchy = 'fecha_hora'
    
    readonly_fields = ('grado_severidad',)
    
    # Agregar botón de importar CSV en el changelist
    change_list_template = 'admin/siniestros/siniestro_changelist.html'
    
    def get_urls(self):
        """Agrega URL personalizada para importar CSV."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name='siniestros_siniestro_import_csv',
            ),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """Vista para manejar la importación de CSV."""
        context = {
            'title': 'Importar Siniestros desde CSV',
            'opts': self.model._meta,
            'has_permission': True,
        }
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            clear_existing = request.POST.get('clear_existing') == 'on'
            
            if not csv_file:
                messages.error(request, 'Por favor seleccione un archivo CSV.')
                return render(request, 'admin/siniestros/csv_upload.html', context)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'El archivo debe ser un CSV.')
                return render(request, 'admin/siniestros/csv_upload.html', context)
            
            try:
                anio_filtro = request.POST.get('anio_filtro')
                results = import_csv(csv_file, clear_existing=clear_existing, anio_filtro=anio_filtro)
                context['results'] = results
                
                if results['errores']:
                    messages.warning(
                        request, 
                        f"Importación completada con {len(results['errores'])} errores. "
                        f"Se crearon {results['siniestros_creados']} siniestros y {results['victimas_creadas']} víctimas."
                    )
                else:
                    messages.success(
                        request,
                        f"Importación exitosa: {results['siniestros_creados']} siniestros y "
                        f"{results['victimas_creadas']} víctimas creados."
                    )
                    
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
        
        return render(request, 'admin/siniestros/csv_upload.html', context)