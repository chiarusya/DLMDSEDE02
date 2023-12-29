let map = L.map('map').setView([18.5, 13.75], 3); // Set initial map view

// Load and add the tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 12,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
//     maxZoom: 12,
//     attribution: '© OpenStreetMap contributors, © CARTO'
// }).addTo(map);

function resetMapZoom() {
    // Set to default zoom and center. Replace with your default values
    map.setView([18.5, 13.75], 3);
}


function updateUTCTime() {
    var now = new Date();
    var hours = now.getUTCHours().toString().padStart(2, '0');
    var minutes = now.getUTCMinutes().toString().padStart(2, '0');
    var timeStr = hours + ':' + minutes;
    document.getElementById('utc-time').textContent = timeStr;
}

// Update time every minute
setInterval(updateUTCTime, 60000);

// Set the initial time
updateUTCTime();

let aircraftIcon = L.icon({
    iconUrl: 'airplane.png',  // Path to the aircraft icon image
    iconSize: [19, 19],  // Size of the icon
    iconAnchor: [19, 19]  // Anchor point of the icon
});

let ws = new WebSocket("ws://localhost:6789"); // Change to the WebSocket server URL

let markers = {};  // Object to hold markers for each flight

ws.onmessage = function(event) {
    let data = JSON.parse(event.data);
    let lat = data.latitude;
    let lon = data.longitude;
    let heading = data.heading;
    let flight_number = data.flight_number;
    // let ac_type = data.ac_type;
    // let dep_stn = data.dep_stn;
    // let arr_stn = data.arr_stn;

    // Check if the marker already exists
    if (markers[flight_number]) {
        markers[flight_number].setLatLng([lat, lon]);
        markers[flight_number].setRotationAngle(heading);
        markers[flight_number].bindTooltip(`${flight_number}`);

    } else {
        markers[flight_number] = L.marker([lat, lon], {icon: aircraftIcon})
        .bindTooltip(`${flight_number}`)    
        .addTo(map)
        .setRotationAngle(heading);
        
    }
};
