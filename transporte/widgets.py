"""
Widgets personalizados para el admin de transporte.
"""
from django import forms
import json


class ColorPickerWidget(forms.TextInput):
    """Widget de selector de color para campos hexadecimales."""
    
    input_type = 'color'
    
    class Media:
        css = {
            'all': []
        }
    
    def __init__(self, attrs=None):
        default_attrs = {'style': 'width: 60px; height: 40px; padding: 0; border: none; cursor: pointer;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class GeoJSONMapWidget(forms.Widget):
    """Widget de mapa Leaflet para dibujar rutas GeoJSON LineString."""
    
    template_name = 'widgets/geojson_widget.html'
    
    class Media:
        css = {
            'all': [
                'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
            ]
        }
        js = [
            'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
        ]
    
    def format_value(self, value):
        """Formatea el valor para mostrar en el widget."""
        if value is None or value == '':
            return '{}'
        if isinstance(value, dict):
            return json.dumps(value, indent=2) if value else '{}'
        return value
    

