document.addEventListener('DOMContentLoaded', function () {
    // Buscar todos los mapas por su container ID que seguimos un patrón en el template
    // El patrón en template es: id="map-{{ widget.name }}"
    const mapContainers = document.querySelectorAll('.geojson-map-container');

    mapContainers.forEach(container => {
        const fieldName = container.id.replace('map-', '');
        const textarea = document.getElementById('id_' + fieldName);
        const mapId = container.id;

        if (!textarea) return;

        // Inicializar mapa con Leaflet
        if (typeof L !== 'undefined') {
            const map = L.map(mapId).setView([-3.9932, -79.2044], 13); // Loja, Ecuador

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
                        const polyline = L.polyline(latLngs, { color: 'red', weight: 4 });
                        polyline.addTo(drawnItems);
                        map.fitBounds(polyline.getBounds());
                    }
                }
            } catch (e) {
                console.log('No existing geom data');
            }

            let isDrawing = false;
            let currentLine = null;
            const coordinates = [];

            // Referencias a botones existentes (ya creados en HTML)
            const btnDraw = document.getElementById('btn-draw-' + fieldName);
            const btnClear = document.getElementById('btn-clear-' + fieldName);
            const btnSave = document.getElementById('btn-save-' + fieldName);

            if (btnDraw) {
                btnDraw.addEventListener('click', function (e) {
                    e.preventDefault(); // Prevenir submit del form
                    isDrawing = !isDrawing;
                    this.textContent = isDrawing ? 'Dibujando...' : 'Dibujar Ruta';
                    this.classList.toggle('active', isDrawing); // Para estilos CSS si se desea

                    if (isDrawing) {
                        coordinates.length = 0;
                        drawnItems.clearLayers();
                        currentLine = null;
                        this.style.background = '#FF9800'; // Feedback visual directo
                    } else {
                        this.style.background = '#43a047'; // Volver al color original
                    }
                });
            }

            if (btnClear) {
                btnClear.addEventListener('click', function (e) {
                    e.preventDefault();
                    coordinates.length = 0;
                    isDrawing = false;
                    drawnItems.clearLayers();
                    currentLine = null;
                    if (btnDraw) {
                        btnDraw.textContent = 'Dibujar Ruta';
                        btnDraw.style.background = '#43a047';
                    }
                    textarea.value = '';
                });
            }

            if (btnSave) {
                btnSave.addEventListener('click', function (e) {
                    e.preventDefault();
                    if (coordinates.length >= 2) {
                        const geojson = {
                            type: 'LineString',
                            coordinates: coordinates
                        };
                        textarea.value = JSON.stringify(geojson, null, 2);
                        isDrawing = false;
                        if (btnDraw) {
                            btnDraw.textContent = 'Dibujar Ruta';
                            btnDraw.style.background = '#43a047';
                        }
                        alert('Ruta guardada correctamente (' + coordinates.length + ' puntos)');
                    } else {
                        alert('Debes dibujar al menos 2 puntos para crear una ruta');
                    }
                });
            }

            // Click en el mapa para agregar puntos
            map.on('click', function (e) {
                if (isDrawing) {
                    const latlng = e.latlng;
                    coordinates.push([latlng.lng, latlng.lat]);

                    // Agregar marcador
                    L.circleMarker([latlng.lat, latlng.lng], {
                        radius: 6,
                        fillColor: '#FF5722',
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    }).addTo(drawnItems);

                    // Dibujar línea
                    if (coordinates.length > 1) {
                        if (currentLine) {
                            drawnItems.removeLayer(currentLine);
                        }
                        const latLngs = coordinates.map(coord => [coord[1], coord[0]]);
                        currentLine = L.polyline(latLngs, { color: 'red', weight: 4 });
                        currentLine.addTo(drawnItems);
                    }
                }
            });
        } else {
            console.warn('Leaflet no está cargado.');
        }
    });
});
