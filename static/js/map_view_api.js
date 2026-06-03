// using api to get data of cases of disease in different areas and display them on the
// map using leaflet.js

const defaultMapCenter = [36.7783, -119.4179];
let map;

function createMap() {
    map = L.map('map').setView(defaultMapCenter, 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

// function to get data from api and display on map
function getDataAndDisplayOnMap() {
    // make an api call to get data of cases of disease in different areas
    fetch('/api/get_cases_data/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Could not load case data');
            }
            return response.json();
        })
        .then(data => {
            // data is an array of objects with properties: area, cases, latitude, longitude
            const markers = [];

            data.forEach(item => {
                const latitude = Number(item.latitude);
                const longitude = Number(item.longitude);

                if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
                    return;
                }

                // create a marker for each area and add it to the map
                const marker = L.marker([latitude, longitude]).addTo(map);
                // bind a popup to the marker to show the number of cases in that area
                marker.bindPopup(`<b>${item.area}</b><br>Cases: ${item.cases}`);
                markers.push(marker);
            });

            if (markers.length > 0) {
                const markerGroup = L.featureGroup(markers);
                map.fitBounds(markerGroup.getBounds(), {
                    padding: [30, 30],
                    maxZoom: 10
                });
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

// call the function to get data and display on map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    createMap();
    getDataAndDisplayOnMap();
});
