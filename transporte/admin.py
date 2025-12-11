from django.contrib import admin
from django import forms
from .models import LineaBus


class GeoJSONWidget(forms.Textarea):
    """Widget personalizado para editar GeoJSON en el admin."""
    pass


class LineaBusForm(forms.ModelForm):
    """Formulario personalizado para LineaBus con widget de mapa interactivo."""
    class Meta:
        model = LineaBus
        fields = '__all__'
        widgets = {
            'geom': GeoJSONWidget(attrs={
                'class': 'vLargeTextField',
                'placeholder': '{"type": "LineString", "coordinates": [[lng, lat], [lng, lat], ...]}',
                'style': 'width: 100%; height: 300px; font-family: monospace; font-size: 12px; background-color: #f5f5f5;'
            })
        }


@admin.register(LineaBus)
class LineaBusAdmin(admin.ModelAdmin):
    """Configuración admin para el modelo LineaBus."""
    form = LineaBusForm
    list_display = ('nombre', 'color', 'origen', 'destino', 'tarifa_base', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'origen', 'destino')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'color', 'activo', 'geom')
        }),
        ('Ruta y Tarifa', {
            'fields': ('origen', 'destino', 'tarifa_base', 'descripcion')
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
