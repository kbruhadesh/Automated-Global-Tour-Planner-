/**
 * Map Module — Leaflet.js integration
 * Clean minimal style with dark markers.
 */

const TourMap = (() => {
    let map = null;
    let routeLayer = null;
    let markersLayer = null;
    let animationTimer = null;

    const TILE_URL = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>';
    let tileLayer = null;

    function init() {
        if (map) return;

        map = L.map('map', {
            center: [20, 60],
            zoom: 3,
            minZoom: 2,
            maxZoom: 10,
            zoomControl: true,
            attributionControl: true,
            scrollWheelZoom: true,
        });

        tileLayer = L.tileLayer(TILE_URL, {
            attribution: TILE_ATTR,
            maxZoom: 19,
        }).addTo(map);

        routeLayer = L.layerGroup().addTo(map);
        markersLayer = L.layerGroup().addTo(map);

        setTimeout(() => map.invalidateSize(), 200);
    }

    function clearRoute() {
        if (routeLayer) routeLayer.clearLayers();
        if (markersLayer) markersLayer.clearLayers();
        if (animationTimer) {
            clearInterval(animationTimer);
            animationTimer = null;
        }
    }

    function createMarkerIcon(flag, index, isHome) {
        const bgColor = isHome ? '#111111' : '#ffffff';
        const textColor = isHome ? '#ffffff' : '#111111';
        const borderColor = '#111111';
        const size = isHome ? 38 : 32;

        return L.divIcon({
            className: 'custom-marker',
            html: `
                <div style="
                    width: ${size}px;
                    height: ${size}px;
                    background: ${bgColor};
                    border: 2px solid ${borderColor};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: ${isHome ? '1rem' : '0.85rem'};
                    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                    cursor: pointer;
                    color: ${textColor};
                    font-weight: 600;
                    font-family: 'Inter', sans-serif;
                ">${isHome ? 'H' : (flag || index)}</div>
                ${!isHome ? `<div style="
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    width: 16px;
                    height: 16px;
                    background: #111111;
                    color: white;
                    border-radius: 50%;
                    font-size: 0.55rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: 'Inter', sans-serif;
                ">${index}</div>` : ''}
            `,
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2],
            popupAnchor: [0, -size / 2 - 4],
        });
    }

    function drawRoute(stops, homeCountry, homeCoords) {
        clearRoute();
        if (!map) init();

        const allCoords = [];

        if (homeCoords) {
            const homeMarker = L.marker(homeCoords, {
                icon: createMarkerIcon('H', 0, true),
            }).addTo(markersLayer);

            homeMarker.bindPopup(`
                <div style="font-family: Inter, sans-serif; padding: 4px;">
                    <strong>${homeCountry}</strong><br>
                    <span style="color: #737373; font-size: 0.8rem;">Home Base</span>
                </div>
            `);
            allCoords.push(homeCoords);
        }

        stops.forEach((stop, i) => {
            const coords = [stop.coordinates[0], stop.coordinates[1]];
            allCoords.push(coords);

            const marker = L.marker(coords, {
                icon: createMarkerIcon(stop.flag, i + 1, false),
            }).addTo(markersLayer);

            marker.bindPopup(`
                <div style="font-family: Inter, sans-serif; padding: 4px; min-width: 180px;">
                    <strong>${stop.flag} ${stop.country}</strong><br>
                    <span style="color: #737373; font-size: 0.8rem;">
                        ${stop.start_date} — ${stop.end_date}
                    </span><br>
                    <span style="font-size: 0.83rem;">
                        ${stop.days} days &nbsp;|&nbsp; $${stop.total_cost.toLocaleString()}
                    </span>
                </div>
            `);
        });

        if (homeCoords) allCoords.push(homeCoords);

        animateRoute(allCoords);

        if (allCoords.length > 1) {
            const bounds = L.latLngBounds(allCoords);
            map.fitBounds(bounds, { padding: [50, 50], maxZoom: 6 });
        }
    }

    function animateRoute(coords) {
        if (coords.length < 2) return;

        let segmentIndex = 0;
        const delay = 250;

        function drawNextSegment() {
            if (segmentIndex >= coords.length - 1) {
                clearInterval(animationTimer);
                animationTimer = null;
                return;
            }

            const start = coords[segmentIndex];
            const end = coords[segmentIndex + 1];

            L.polyline([start, end], {
                color: '#111111',
                weight: 1.5,
                opacity: 0.5,
                dashArray: '6, 4',
            }).addTo(routeLayer);

            L.circleMarker(end, {
                radius: 2.5,
                color: '#111111',
                fillColor: '#111111',
                fillOpacity: 0.6,
                weight: 0,
            }).addTo(routeLayer);

            segmentIndex++;
        }

        drawNextSegment();
        animationTimer = setInterval(drawNextSegment, delay);
    }

    function resize() {
        if (map) setTimeout(() => map.invalidateSize(), 100);
    }

    return { init, drawRoute, clearRoute, resize };
})();
