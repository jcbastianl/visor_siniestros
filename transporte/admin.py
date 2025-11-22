from django.contrib import admin
from .models import LineaBus


@admin.register(LineaBus)
class LineaBusAdmin(admin.ModelAdmin):
    """Configuración admin para el modelo LineaBus."""
    list_display = ('nombre', 'color', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'color', 'activo')
        }),
        ('Coordenadas', {
            'fields': ('coordenadas',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
