// راه‌اندازی نقشه با مرکزیت استان فارس
var map = L.map('map').setView([29.5, 53.0], 7);

// اضافه کردن نقشه پایه OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors | Smart-FIRIS'
}).addTo(map);

// تابع تعیین رنگ بر اساس کلاس خطر
function getColor(riskLevel) {
    switch (riskLevel) {
        case 5: return '#800026'; // بحرانی (قرمز تیره)
        case 4: return '#BD0026'; // خیلی زیاد (قرمز)
        case 3: return '#FC4E2A'; // زیاد (نارنجی)
        case 2: return '#FED976'; // متوسط (زرد)
        default: return '#74c476'; // کم (سبز)
    }
}

// استایل‌دهی به پلی‌گون‌های استان فارس
function style(feature) {
    var risk = (feature.properties && feature.properties.risk) ? feature.properties.risk : 3;
    return {
        fillColor: getColor(risk),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.6
    };
}

// بارگذاری داده‌های استان فارس از فایل GeoJSON
fetch('data/fars.geojson')
    .then(response => {
        if (!response.ok) {
            throw new Error('خطا در بارگذاری فایل داده');
        }
        return response.json();
    })
    .then(data => {
        var geojsonLayer = L.geoJson(data, {
            style: style,
            onEachFeature: function (feature, layer) {
                var name = (feature.properties && (feature.properties.NAME || feature.properties.name || feature.properties.Name)) || 'استان فارس';
                layer.bindPopup('<strong>محدوده: </strong>' + name + '<br><strong>وضعیت پایش: </strong>فعال (Smart-FIRIS)');
            }
        }).addTo(map);

        // تنظیم زوم نقشه به صورت خودکار بر روی محدوده استان فارس
        map.fitBounds(geojsonLayer.getBounds());
    })
    .catch(error => {
        console.error('Error loading geojson:', error);
    });

// راهنمای نقشه (Legend)
var legend = L.control({position: 'bottomright'});
legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'legend');
    var grades = [1, 2, 3, 4, 5];
    var labels = ['خیلی کم', 'کم', 'متوسط', 'زیاد', 'بحرانی'];

    div.innerHTML += '<strong>شاخص خطر حریق</strong><br>';
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<div class="legend-item">' +
            '<span class="color-box" style="background:' + getColor(grades[i]) + '"></span> ' +
            labels[i] + '</div>';
    }
    return div;
};
legend.addTo(map);
