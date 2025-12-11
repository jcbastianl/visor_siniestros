from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import LineaBus


class GeoJSONWidget(forms.Textarea):
    """Widget personalizado para editar GeoJSON con mapa interactivo."""
    
    def render(self, name, value, attrs=None, renderer=None):
        html = f'''
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
        
        <div style="margin-bottom: 10px;">
            <div id="geom-map-{id(self)}" style="width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;"></div>
            
            <div style="background-color: #f5f5f5; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                <strong>📍 Instrucciones:</strong>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                    <li>Click en "🖊️ Dibujar Ruta" para comenzar</li>
                    <li>Haz click en el mapa para añadir puntos a la ruta</li>
                    <li>Click en "✅ Guardar Ruta" cuando hayas terminado</li>
                    <li>Usa "🗑️ Limpiar" para empezar de nuevo</li>
                </ul>
            </div>
        </div>
        
        <textarea name="{name}" {' '.join([f'{k}="{v}"' for k, v in (attrs or {}).items()]) if attrs else ''} 
            id="id_{name}" style="width: 100%; height: 150px; font-family: monospace; font-size: 12px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background-color: #f5f5f5;">{value or ''}</textarea>
        
        <p style="margin-top: 10px; font-size: 11px; color: #666;">
            <strong>Formato GeoJSON LineString:</strong><br>
            {{"type": "LineString", "coordinates": [[lng, lat], [lng, lat], ...]}}
        </p>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const mapId = 'geom-map-{id(self)}';
            const textarea = document.querySelector('textarea[name="{name}"]');
            const mapContainer = document.getElementById(mapId);
            
            if (typeof L === 'undefined') {{
                console.error('Leaflet no está disponible');
                return;
            }}
            
            const map = L.map(mapId).setView([-3.9932, -79.2044], 12); // Loja, Ecuador
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }}).addTo(map);
            
            let drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);
            
            let isDrawing = false;
            let coordinates = [];
            let currentLine = null;
            
            // Cargar datos existentes
            try {{
                const existingData = textarea.value.trim();
                if (existingData) {{
                    const geojson = JSON.parse(existingData);
                    if (geojson.type === 'LineString' && geojson.coordinates.length > 0) {{
                        const latLngs = geojson.coordinates.map(coord => [coord[1], coord[0]]);
                        const polyline = L.polyline(latLngs, {{color: 'red', weight: 3}});
                        polyline.addTo(drawnItems);
                        map.fitBounds(polyline.getBounds());
                        coordinates = JSON.parse(JSON.stringify(geojson.coordinates));
                    }}
                }}
            }} catch (e) {{
                console.log('No existing geom data');
            }}
            
            // Crear controles
            const drawControl = L.Control.extend({{
                onAdd: function() {{
                    const div = L.DomUtil.create('div', 'leaflet-control');
                    div.innerHTML = `
                        <button id="draw-line" style="display: block; width: 140px; margin-bottom: 5px; padding: 8px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            🖊️ Dibujar Ruta
                        </button>
                        <button id="clear-line" style="display: block; width: 140px; margin-bottom: 5px; padding: 8px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            🗑️ Limpiar
                        </button>
                        <button id="finish-line" style="display: block; width: 140px; padding: 8px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            ✅ Guardar Ruta
                        </button>
                    `;
                    return div;
                }}
            }});
            
            new drawControl().addTo(map);
            
            setTimeout(() => {{
                const drawBtn = document.getElementById('draw-line');
                const clearBtn = document.getElementById('clear-line');
                const finishBtn = document.getElementById('finish-line');
                
                if (drawBtn) {{
                    drawBtn.addEventListener('click', function() {{
                        isDrawing = !isDrawing;
                        this.textContent = isDrawing ? '✏️ Dibujando...' : '🖊️ Dibujar Ruta';
                        this.style.background = isDrawing ? '#FF9800' : '#4CAF50';
                        if (isDrawing) {{
                            coordinates = [];
                            if (currentLine) {{
                                drawnItems.removeLayer(currentLine);
                            }}
                            currentLine = null;
                        }}
                    }});
                }}
                
                if (clearBtn) {{
                    clearBtn.addEventListener('click', function() {{
                        coordinates = [];
                        isDrawing = false;
                        if (currentLine) {{
                            drawnItems.removeLayer(currentLine);
                            currentLine = null;
                        }}
                        drawnItems.eachLayer(layer => drawnItems.removeLayer(layer));
                        drawBtn.textContent = '🖊️ Dibujar Ruta';
                        drawBtn.style.background = '#4CAF50';
                        textarea.value = '';
                    }});
                }}
                
                if (finishBtn) {{
                    finishBtn.addEventListener('click', function() {{
                        if (coordinates.length >= 2) {{
                            const geojson = {{
                                type: 'LineString',
                                coordinates: coordinates
                            }};
                            textarea.value = JSON.stringify(geojson, null, 2);
                            isDrawing = false;
                            drawBtn.textContent = '🖊️ Dibujar Ruta';
                            drawBtn.style.background = '#4CAF50';
                            alert('✅ Ruta guardada correctamente');
                        }} else {{
                            alert('⚠️ Debes dibujar al menos 2 puntos para crear una ruta');
                        }}
                    }});
                }}
            }}, 100);
            
            // Click en mapa para agregar puntos
            map.on('click', function(e) {{
                if (isDrawing) {{
                    const latlng = e.latlng;
                    coordinates.push([latlng.lng, latlng.lat]);
                    
                    L.circleMarker([latlng.lat, latlng.lng], {{
                        radius: 5,
                        fillColor: '#FF5722',
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }}).addTo(drawnItems);
                    
                    if (coordinates.length > 1) {{
                        if (currentLine) {{
                            drawnItems.removeLayer(currentLine);
                        }}
                        const latLngs = coordinates.map(coord => [coord[1], coord[0]]);
                        currentLine = L.polyline(latLngs, {{color: 'red', weight: 3}});
                        currentLine.addTo(drawnItems);
                    }}
                }}
            }});
        }});
        </script>
        '''
        return format_html(html)


class LineaBusForm(forms.ModelForm):
    """Formulario personalizado para LineaBus con widget de mapa interactivo."""
    class Meta:
        model = LineaBus
        fields = '__all__'
        widgets = {
            'geom': GeoJSONWidget(attrs={
                'class': 'vLargeTextField',
                'placeholder': '{"type": "LineString", "coordinates": [[lng, lat], [lng, lat], ...]}',
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
