from django.contrib import admin
from .models import LineaBus


@admin.register(LineaBus)
class LineaBusAdmin(admin.ModelAdmin):
    """Configuración admin para el modelo LineaBus."""
    list_display = ('nombre', 'color', 'origen', 'destino', 'tarifa_base', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'origen', 'destino')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'color', 'activo')
        }),
        ('Ruta y Tarifa', {
            'fields': ('origen', 'destino', 'tarifa_base', 'descripcion')
        }),
        ('Geometría', {
            'fields': ('geom',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
