/* WariSetu AI (v2 Light Theme - Maharashtra Police IT Cell App Logic) */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Live System Clock
  updateClock();
  setInterval(updateClock, 1000);

  // Tab Navigation Handling
  setupNavigation();

  // Initialize Leaflet Map for Route Corridor
  initRouteMap();

  // Initialize Forecast Chart
  initForecastChart();
});

function updateClock() {
  const clockEl = document.getElementById('sysClock');
  if (!clockEl) return;
  const now = new Date();
  const options = {
    day: '2-digit', month: 'SHORT', year: 'NUMERIC',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  };
  // Format to match government clock style
  const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase();
  const timeStr = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  clockEl.textContent = `${dateStr} ${timeStr} IST`;
}

function setupNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  const views = document.querySelectorAll('.view-section');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-target');

      tabs.forEach(t => t.classList.remove('active'));
      views.forEach(v => v.classList.remove('active'));

      tab.classList.add('active');
      const targetView = document.getElementById(targetId);
      if (targetView) {
        targetView.classList.add('active');
      }

      // Refresh map / chart layout if switching views
      if (targetId === 'view-command' && window.wariMap) {
        setTimeout(() => window.wariMap.invalidateSize(), 150);
      }
      if (targetId === 'view-crowd' && window.forecastChartInstance) {
        setTimeout(() => window.forecastChartInstance.resize(), 150);
      }
    });
  });
}

/* ==================== LEAFLET MAP INITIALIZATION ==================== */
function initRouteMap() {
  const mapElement = document.getElementById('routeMap');
  if (!mapElement) return;

  // Center between Pune and Pandharpur
  const wariMap = L.map('routeMap', {
    center: [18.0000, 74.8000],
    zoom: 9,
    zoomControl: true
  });

  window.wariMap = wariMap;

  // Tile Layer - Clean Light Basemap (OpenStreetMap / CartoDB Positron)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; Maharashtra Police IT &bull; Map data &copy; OpenStreetMap',
    maxZoom: 18
  }).addTo(wariMap);

  // Wari Corridor Coordinates (Alandi -> Pune -> Saswad -> Bhalwani -> Wakhri -> Pandharpur)
  const routePoints = [
    [18.6772, 73.8967], // Alandi
    [18.5204, 73.8567], // Pune City
    [18.3440, 74.0305], // Saswad
    [18.1500, 74.3000], // Jejuri / Lonand corridor
    [17.8900, 75.0200], // Bhalwani
    [17.7280, 75.2950], // Wakhri Phata
    [17.6777, 75.3276]  // Pandharpur Shrine
  ];

  // Draw Heat-shaded Polylines along route
  // Green section (Clear)
  L.polyline(routePoints.slice(0, 3), {
    color: '#2E5B36',
    weight: 6,
    opacity: 0.85
  }).addTo(wariMap).bindPopup('<b>Alandi-Saswad Sector:</b> Normal Pilgrim Density (35-62%)');

  // Orange section (Heavy)
  L.polyline(routePoints.slice(2, 5), {
    color: '#B8551B',
    weight: 7,
    opacity: 0.85
  }).addTo(wariMap).bindPopup('<b>Saswad-Bhalwani Sector:</b> Heavy Density (74%)');

  // Red section (Critical Bottleneck)
  L.polyline(routePoints.slice(4, 7), {
    color: '#9A2525',
    weight: 8,
    opacity: 0.9
  }).addTo(wariMap).bindPopup('<b>Wakhri-Pandharpur Sector:</b> CRITICAL CONGESTION (88-94%)');

  // Palkhi Current Location Marker (Saffron Flag)
  const palkhiIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#D98E2C; color:#FFF; border:1px solid #7A1F1F; padding:4px 8px; font-weight:bold; font-size:10px; border-radius:2px; box-shadow:0 1px 3px rgba(0,0,0,0.3);">🚩 PALKHI (Wakhri)</div>`,
    iconSize: [110, 24],
    iconAnchor: [55, 12]
  });
  L.marker([17.7280, 75.2950], { icon: palkhiIcon }).addTo(wariMap)
    .bindPopup('<b>Sant Tukaram Maharaj Palkhi</b><br>Location: Approaching Wakhri Phata (Km 184)<br>Speed: 3 km/h');

  // Water Tankers Pins
  const waterIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#1D6F8A; color:#FFF; border:1px solid #000; padding:2px 5px; font-size:9px; font-weight:bold; border-radius:2px;">💧 Tanker #09</div>`,
    iconSize: [80, 20]
  });
  L.marker([17.7400, 75.2800], { icon: waterIcon }).addTo(wariMap)
    .bindPopup('<b>Water Tanker #WT-09</b><br>Capacity: 10,000L (80% Full)<br>Stationed: Wakhri Access Rd');

  // Medical Van Pins
  const medIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#9A2525; color:#FFF; border:1px solid #000; padding:2px 5px; font-size:9px; font-weight:bold; border-radius:2px;">🚑 MedVan #02</div>`,
    iconSize: [80, 20]
  });
  L.marker([17.6800, 75.3200], { icon: medIcon }).addTo(wariMap)
    .bindPopup('<b>Mobile Medical Unit #MV-02</b><br>Doctor on duty: Dr. S. P. Deshmukh<br>Location: Pandharpur Entry');
}

/* ==================== CONGESTION FORECAST CHART ==================== */
function initForecastChart() {
  const canvas = document.getElementById('forecastChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  window.forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['19:00 IST', '19:20 IST', '19:40 IST', '20:00 IST', '20:20 IST', '20:40 IST', '21:00 IST'],
      datasets: [
        {
          label: 'Pandharpur Chowk Density %',
          data: [94, 96, 98, 92, 85, 78, 70],
          borderColor: '#9A2525',
          backgroundColor: 'rgba(154, 37, 37, 0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.1,
          pointBackgroundColor: '#9A2525'
        },
        {
          label: 'Wakhri Phata Density %',
          data: [88, 90, 86, 82, 75, 68, 60],
          borderColor: '#D98E2C',
          backgroundColor: 'rgba(217, 142, 44, 0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.1,
          pointBackgroundColor: '#D98E2C'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { family: 'IBM Plex Sans', size: 11 },
            boxWidth: 12
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          grid: { color: '#E5E0D7' },
          ticks: { font: { family: 'IBM Plex Sans', size: 10 } }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: '#E5E0D7' },
          ticks: {
            callback: value => value + '%',
            font: { family: 'IBM Plex Sans', size: 10 }
          }
        }
      }
    }
  });
}

/* ==================== INTERACTIVE HELPERS ==================== */
window.showTranscript = function(caseId) {
  const box = document.getElementById('transcriptBox');
  if (!box) return;

  if (caseId === 'LF-802') {
    box.textContent = `"हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."

[Audio Analysis Summary]:
- Subject: Male, ~68 yrs
- Clothing: White Kurta, Dhoti, White Cap, Tulsi Mala
- Audio Confidence score: High (0.94)
- Vision Cross-Match: CAM-04 Pandharpur Chowk frame #4812 matching features.`;
  } else if (caseId === 'LF-805') {
    box.textContent = `"नमस्कार, माझी मुलगी आनंदिता कुलकर्णी (वय ९ वर्षे) वाखरी नाक्याजवळील गर्दीत हरवली आहे. तिने पिवळा परकर पोलका घातला आहे. हातात सोन्याच्या बांगड्या आहेत."

[Audio Analysis Summary]:
- Subject: Female child, ~9 yrs
- Clothing: Yellow traditional dress (Parkar Polka)
- Audio Confidence score: High (0.91)
- Vision Cross-Match: Scanning CAM-12 & CAM-08 feeds.`;
  } else if (caseId === 'LF-808') {
    box.textContent = `"कंट्रोल रूम, सुनिता पाटील (वय ५४) आळंदी घाटाजवळ दिंडीतून वेगळ्या झाल्या. त्यांनी हिरवी नऊवारी साडी घातली असून डोक्यावर तुळशीचे वृंदावन आहे."

[Audio Analysis Summary]:
- Subject: Female, ~54 yrs
- Clothing: Green Navvari Saree with Tulsi Vrindavan
- Audio Confidence score: Medium (0.87)
- Vision Cross-Match: Search active on Sector 1 cameras.`;
  }
};

window.acknowledgeAlert = function(alertId) {
  const alertEl = document.getElementById(alertId);
  if (!alertEl) return;

  alertEl.classList.add('acknowledged');
  const btn = alertEl.querySelector('.govt-btn');
  if (btn) {
    btn.className = 'govt-btn btn-disabled';
    btn.textContent = 'Acknowledged';
    btn.onclick = null;
  }

  // Update navbar badge if all acknowledged
  const activeBadge = document.querySelector('.nav-tab[data-target="view-medical"] .badge');
  if (activeBadge) {
    activeBadge.textContent = '1 Alert';
  }
};

/* CCTV Modal Handler */
window.openCamModal = function(camId, location, status) {
  const modal = document.getElementById('camModal');
  const modalId = document.getElementById('modalCamId');
  const modalTitle = document.getElementById('modalCamTitle');
  const modalStatus = document.getElementById('modalCamStatus');

  if (modalId) modalId.textContent = camId;
  if (modalTitle) modalTitle.textContent = `CCTV SURVEILLANCE FEED: ${location}`;
  if (modalStatus) modalStatus.textContent = status;

  if (modal) modal.classList.add('open');
};

window.closeCamModal = function() {
  const modal = document.getElementById('camModal');
  if (modal) modal.classList.remove('open');
};
