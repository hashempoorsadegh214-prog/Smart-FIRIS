// نقشه اصلی Smart-FIRIS
var map = L.map('map', {
    center: [29.3, 53.1],
    zoom: 7
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

// لود کردن محدوده و اضافه کردن لایه (اگر موجود باشد)
fetch('data/bounds.json')
    .then(res => res.json())
    .then(meta => {
        L.imageOverlay('data/hazard_overlay.png', meta.bounds, {
            opacity: 0.75
        }).addTo(map);
        map.fitBounds(meta.bounds);
    });
