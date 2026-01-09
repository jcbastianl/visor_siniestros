from django.contrib import admin
from .models import LineaBus, Ciclovia
from .forms import LineaBusAdminForm, CicloviaAdminForm


@admin.register(LineaBus)
class LineaBusAdmin(admin.ModelAdmin):
    """Configuracion admin para el modelo LineaBus con color picker."""
    form = LineaBusAdminForm
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


@admin.register(Ciclovia)
class CicloviaAdmin(admin.ModelAdmin):
    """Configuracion admin para el modelo Ciclovia con color picker."""
    form = CicloviaAdminForm
    list_display = ('nombre', 'color', 'longitud_km', 'tipo_separacion', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'tipo_separacion', 'fecha_creacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'color', 'activo')
        }),
        ('Características', {
            'fields': ('longitud_km', 'tipo_separacion')
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

