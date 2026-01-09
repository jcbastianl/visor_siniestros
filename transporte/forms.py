"""
Formularios para el admin de transporte.
"""
from django import forms
from .models import LineaBus, Ciclovia
from .widgets import ColorPickerWidget


class LineaBusAdminForm(forms.ModelForm):
    """Formulario personalizado para LineaBus con color picker."""
    
    class Meta:
        model = LineaBus
        fields = '__all__'
        widgets = {
            'color': ColorPickerWidget(),
        }


class CicloviaAdminForm(forms.ModelForm):
    """Formulario personalizado para Ciclovia con color picker."""
    
    class Meta:
        model = Ciclovia
        fields = '__all__'
        widgets = {
            'color': ColorPickerWidget(),
        }
