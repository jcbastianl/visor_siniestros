document.addEventListener('DOMContentLoaded', function() {
    const geomInputs = document.querySelectorAll('textarea[name="geom"]');
    
    geomInputs.forEach((textarea, index) => {
        const containerId = 'geom-map-' + index;
        const container = document.createElement('div');
        container.id = containerId;
        container.style.cssText = 'width: 100%; height: 400px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px;';
        
        textarea.parentElement.insertBefore(container, textarea);
        
        // Inicializar mapa con Leaflet
        if (typeof L !== 'undefined') {
            const map = L.map(containerId).setView([-3.9932, -79.2044], 13); // Loja, Ecuador
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            
            let drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);
            
            // Intentar cargar datos existentes del textarea
            try {
                const existingData = textarea.value.trim();
                if (existingData) {
                    const geojson = JSON.parse(existingData);
                    if (geojson.type === 'LineString' && geojson.coordinates.length > 0) {
                        const latLngs = geojson.coordinates.map(coord => [coord[1], coord[0]]);
                        const polyline = L.polyline(latLngs, {color: 'red', weight: 3});
                        polyline.addTo(drawnItems);
                        map.fitBounds(polyline.getBounds());
                    }
                }
            } catch (e) {
                console.log('No existing geom data');
            }
            
            // Crear controles de dibujo simplificados
            const drawControl = document.createElement('div');
            drawControl.style.cssText = 'position: absolute; top: 10px; right: 10px; z-index: 999; background: white; padding: 10px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
            drawControl.innerHTML = `
                <button id="draw-line-${index}" style="display: block; width: 100%; margin-bottom: 5px; padding: 8px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    Dibujar Ruta
                </button>
                <button id="clear-line-${index}" style="display: block; width: 100%; margin-bottom: 5px; padding: 8px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    Limpiar
                </button>
                <button id="finish-line-${index}" style="display: block; width: 100%; padding: 8px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    Guardar Ruta
                </button>
            `;
            
            const mapContainer = document.getElementById(containerId);
            mapContainer.style.position = 'relative';
            mapContainer.appendChild(drawControl);
            
            let isDrawing = false;
            let currentLine = null;
            const coordinates = [];
            
            document.getElementById(`draw-line-${index}`).addEventListener('click', function() {
                isDrawing = !isDrawing;
                this.textContent = isDrawing ? 'Dibujando... (click en el mapa)' : 'Dibujar Ruta';
                this.style.background = isDrawing ? '#FF9800' : '#4CAF50';
                if (isDrawing) {
                    coordinates.length = 0;
                    if (currentLine) {
                        drawnItems.removeLayer(currentLine);
                    }
                    currentLine = null;
                }
            });
            
            document.getElementById(`clear-line-${index}`).addEventListener('click', function() {
                coordinates.length = 0;
                isDrawing = false;
                if (currentLine) {
                    drawnItems.removeLayer(currentLine);
                    currentLine = null;
                }
                document.getElementById(`draw-line-${index}`).textContent = 'Dibujar Ruta';
                document.getElementById(`draw-line-${index}`).style.background = '#4CAF50';
                textarea.value = '';
            });
            
            document.getElementById(`finish-line-${index}`).addEventListener('click', function() {
                if (coordinates.length >= 2) {
                    const geojson = {
                        type: 'LineString',
                        coordinates: coordinates
                    };
                    textarea.value = JSON.stringify(geojson, null, 2);
                    isDrawing = false;
                    document.getElementById(`draw-line-${index}`).textContent = 'Dibujar Ruta';
                    document.getElementById(`draw-line-${index}`).style.background = '#4CAF50';
                    alert('Ruta guardada correctamente');
                } else {
                    alert('Debes dibujar al menos 2 puntos para crear una ruta');
                }
            });
            
            // Click en el mapa para agregar puntos
            map.on('click', function(e) {
                if (isDrawing) {
                    const latlng = e.latlng;
                    coordinates.push([latlng.lng, latlng.lat]);
                    
                    // Agregar marcador
                    L.circleMarker([latlng.lat, latlng.lng], {
                        radius: 5,
                        fillColor: '#FF5722',
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(drawnItems);
                    
                    // Dibujar línea
                    if (coordinates.length > 1) {
                        if (currentLine) {
                            drawnItems.removeLayer(currentLine);
                        }
                        const latLngs = coordinates.map(coord => [coord[1], coord[0]]);
                        currentLine = L.polyline(latLngs, {color: 'red', weight: 3});
                        currentLine.addTo(drawnItems);
                    }
                }
            });
        } else {
            console.warn('Leaflet no está cargado. El widget de mapa no funcionará.');
        }
    });
});
