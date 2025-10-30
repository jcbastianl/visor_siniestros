from django.contrib import admin
from .models import Siniestro, Victima, Causa, TipoSiniestro

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