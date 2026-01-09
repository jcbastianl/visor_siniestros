"""
Widgets personalizados para el admin de transporte.
"""
from django import forms


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
