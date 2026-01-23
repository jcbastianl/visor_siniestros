"""
Formularios para el admin de transporte.
"""
from django import forms
from .models import LineaBus, Ciclovia
from .widgets import ColorPickerWidget, GeoJSONMapWidget


class LineaBusAdminForm(forms.ModelForm):
    """Formulario personalizado para LineaBus con color picker y mapa."""
    
    class Meta:
        model = LineaBus
        fields = '__all__'
        widgets = {
            'color': ColorPickerWidget(),
            'geom': GeoJSONMapWidget(),
            'paradas': forms.HiddenInput(attrs={'id': 'id_paradas'}),
        }


class CicloviaAdminForm(forms.ModelForm):
    """Formulario personalizado para Ciclovia con color picker y mapa."""
    
    class Meta:
        model = Ciclovia
        fields = '__all__'
        widgets = {
            'color': ColorPickerWidget(),
            'geom': GeoJSONMapWidget(),
        }
