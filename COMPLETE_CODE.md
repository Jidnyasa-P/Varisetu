# VariSetu - Complete Source Code (Line-by-Line)

This document contains the complete, unabridged source code for the **VariSetu (वारी सेतु)** Command Center Dashboard frontend application.

---

## Project Directory Structure

```
VariSetu/
├── .gitignore
├── README.md
├── COMPLETE_CODE.md
└── Frontend/
    ├── package.json
    ├── index.html
    ├── styles.css
    ├── app.js
    └── assets/
        ├── varisetu_logo.png
        ├── warisetu_logo.png
        ├── wari_aerial_procession_1785244820232.jpg
        ├── cctv_wakhri_phata_1785244836537.jpg
        └── palkhi_procession_1785244851342.jpg
```

---

## 1. `Frontend/package.json`

```json
{
  "name": "smart-wari-ai-dashboard",
  "private": true,
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
```

---

## 2. `Frontend/index.html`

```html
<!DOCTYPE html>
<html lang="mr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>वारी सेतु | VARISETU - Maharashtra Police Command Center</title>
  
  <!-- Typography (Google Fonts) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=Tiro+Devanagari+Marathi:ital@0;1&display=swap" rel="stylesheet">
  
  <!-- Leaflet Map CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
  
  <!-- Custom Styles -->
  <link rel="stylesheet" href="styles.css">

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- Leaflet Map JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

  <!-- Top Warli Pattern Woven Strip -->
  <div class="top-warli-border"></div>

  <!-- Government Portal Header -->
  <header class="gov-header">
    <div class="brand-section">
      <img src="assets/varisetu_logo.png" alt="VariSetu Logo" class="brand-logo-img">
      <div class="mh-police-badge">
        <span>म.पो.</span>
        <span style="font-size:7px;">POLICE</span>
      </div>
      <div class="brand-titles">
        <h1 class="brand-marathi">वारी सेतु</h1>
        <span class="brand-english">VARISETU &bull; MAHARASHTRA POLICE IT CELL</span>
      </div>
    </div>

    <div class="header-meta">
      <div class="meta-pill">
        <span class="live-dot"></span>
        <span>SECTOR: PANDHARPUR PILGRIMAGE CORRIDOR</span>
      </div>
      <div class="meta-pill">
        <i data-lucide="clock" style="width:13px; height:13px;"></i>
        <span id="sysClock">28 JUL 2026 18:50:00 IST</span>
      </div>
      <div class="meta-pill" style="border-color: var(--maroon-primary); color: var(--maroon-primary); font-weight:600;">
        <span>PILGRIM COUNT: ~8,45,000</span>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs Bar -->
  <nav class="nav-bar">
    <button class="nav-tab active" data-target="view-command">
      <i data-lucide="layout-dashboard" style="width:14px; height:14px;"></i>
      <span>Main Command Center</span>
    </button>
    <button class="nav-tab" data-target="view-crowd">
      <i data-lucide="users" style="width:14px; height:14px;"></i>
      <span>Crowd Intelligence</span>
      <span class="badge">92% Max Density</span>
    </button>
    <button class="nav-tab" data-target="view-lost">
      <i data-lucide="search" style="width:14px; height:14px;"></i>
      <span>Lost & Found Desk</span>
      <span class="badge" style="background:#B07817; color:#FFF;">4 Active</span>
    </button>
    <button class="nav-tab" data-target="view-medical">
      <i data-lucide="heart-pulse" style="width:14px; height:14px;"></i>
      <span>Medical Alerts</span>
      <span class="badge" style="background:#9A2525; color:#FFF;">2 Alerts</span>
    </button>
    <button class="nav-tab" data-target="view-resources">
      <i data-lucide="truck" style="width:14px; height:14px;"></i>
      <span>Resource Management</span>
    </button>
  </nav>

  <!-- Main App Layout Container -->
  <main class="app-container">

    <!-- ==================== SCREEN 1: MAIN COMMAND CENTER ==================== -->
    <section id="view-command" class="view-section active">
      <div class="section-bar">
        <div class="section-title">
          <i data-lucide="shield-alert" style="width:16px; height:16px;"></i>
          <span>Real-time Operational Command & Surveillance</span>
        </div>
        <div class="section-sub">
          Active Surveillance: 14 CCTVs &bull; Route: Alandi - Dehu - Pune - Wakhri - Pandharpur
        </div>
      </div>

      <div class="command-grid">
        <!-- Left: CCTV surveillance tiles -->
        <div class="cctv-column">
          <div class="panel-header">
            <span>CCTV FEEDS (GRAINY SURVEILLANCE)</span>
            <span style="font-size:10px; color:var(--text-muted);">CLICK FEED TO ENLARGE</span>
          </div>

          <div class="cctv-tile status-heavy" onclick="openCamModal('CAM-12', 'Wakhri Phata Junction Cam 12', 'Heavy Crowd Density (88%)')">
            <img src="assets/cctv_wakhri_phata_1785244836537.jpg" class="cctv-feed-img" alt="CCTV Feed 12">
            <div class="cctv-overlay">
              <div class="cctv-top-info">
                <span class="cctv-cam-id">CAM-12</span>
                <span class="cctv-timestamp">REC 18:50:12</span>
              </div>
              <div class="cctv-bottom-info">
                <span class="cctv-location">Wakhri Phata Junction</span>
                <span class="density-tag orange">HEAVY 88%</span>
              </div>
            </div>
          </div>

          <div class="cctv-tile status-critical" onclick="openCamModal('CAM-04', 'Pandharpur Temple Chowk Cam 04', 'Critical Congestion (94%)')">
            <img src="assets/wari_aerial_procession_1785244820232.jpg" class="cctv-feed-img" alt="CCTV Feed 04">
            <div class="cctv-overlay">
              <div class="cctv-top-info">
                <span class="cctv-cam-id">CAM-04</span>
                <span class="cctv-timestamp">REC 18:50:12</span>
              </div>
              <div class="cctv-bottom-info">
                <span class="cctv-location">Pandharpur Chowk</span>
                <span class="density-tag red">CRITICAL 94%</span>
              </div>
            </div>
          </div>

          <div class="cctv-tile status-moderate" onclick="openCamModal('CAM-08', 'Saswad Highway Checkpoint Cam 08', 'Moderate Flow (62%)')">
            <img src="assets/palkhi_procession_1785244851342.jpg" class="cctv-feed-img" alt="CCTV Feed 08">
            <div class="cctv-overlay">
              <div class="cctv-top-info">
                <span class="cctv-cam-id">CAM-08</span>
                <span class="cctv-timestamp">REC 18:50:10</span>
              </div>
              <div class="cctv-bottom-info">
                <span class="cctv-location">Saswad Corridor</span>
                <span class="density-tag yellow">MODERATE 62%</span>
              </div>
            </div>
          </div>

          <div class="cctv-tile status-normal" onclick="openCamModal('CAM-01', 'Alandi Ghat Section Cam 01', 'Normal Clearance (35%)')">
            <img src="assets/cctv_wakhri_phata_1785244836537.jpg" class="cctv-feed-img" alt="CCTV Feed 01">
            <div class="cctv-overlay">
              <div class="cctv-top-info">
                <span class="cctv-cam-id">CAM-01</span>
                <span class="cctv-timestamp">REC 18:50:08</span>
              </div>
              <div class="cctv-bottom-info">
                <span class="cctv-location">Alandi Ghat Rd</span>
                <span class="density-tag green">NORMAL 35%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Center: Interactive Route Map -->
        <div class="map-container">
          <div id="routeMap"></div>

          <div class="map-controls-overlay">
            <div style="font-weight:700; border-bottom:1px solid var(--border-main); padding-bottom:3px;">ROUTE MAP LEGEND</div>
            <div class="map-legend-item">
              <div class="legend-color-box" style="background:#9A2525;"></div>
              <span>Critical Congestion</span>
            </div>
            <div class="map-legend-item">
              <div class="legend-color-box" style="background:#B8551B;"></div>
              <span>Heavy Density</span>
            </div>
            <div class="map-legend-item">
              <div class="legend-color-box" style="background:#2E5B36;"></div>
              <span>Clear Route</span>
            </div>
            <div class="map-legend-item" style="margin-top:4px;">
              <i data-lucide="droplet" style="width:12px; height:12px; color:#1D6F8A;"></i>
              <span>Water Tanker</span>
            </div>
            <div class="map-legend-item">
              <i data-lucide="cross" style="width:12px; height:12px; color:#9A2525;"></i>
              <span>Medical Van</span>
            </div>
            <div class="map-legend-item">
              <i data-lucide="flag" style="width:12px; height:12px; color:#D98E2C;"></i>
              <span>Palkhi Location</span>
            </div>
          </div>
        </div>

        <!-- Right Column: Plain Stat Panels -->
        <div class="right-col-panel">
          <div class="stat-panel-group">
            <div class="govt-stat-box">
              <div class="stat-label">Lost & Found Desk</div>
              <div class="stat-value">4 Active Cases</div>
              <div class="stat-subtext">2 facial matches flagged by automated engine</div>
            </div>

            <div class="govt-stat-box" style="border-left-color: var(--status-red);">
              <div class="stat-label">Medical Emergencies</div>
              <div class="stat-value" style="color:var(--status-red);">2 Active Alerts</div>
              <div class="stat-subtext">Sector 3 (Wakhri) & Sector 5 (Pandharpur)</div>
            </div>

            <div class="govt-stat-box" style="border-left-color: var(--status-green);">
              <div class="stat-label">Resource Deployment</div>
              <div class="stat-value" style="color:var(--status-green);">12 / 20 Tankers</div>
              <div class="stat-subtext">8 reserves stationed at Pandharpur Depot</div>
            </div>

            <div class="govt-stat-box" style="border-left-color: var(--saffron-gold);">
              <div class="stat-label">Main Palkhi Status</div>
              <div class="stat-value" style="font-size:16px; color:#3B332B;">Sant Tukaram Maharaj Palkhi</div>
              <div class="stat-subtext">Location: Approaching Wakhri Phata (Km 184)</div>
            </div>

            <!-- Mini Photo Texture Box (Grounded Reference) -->
            <div class="panel-card" style="padding:8px;">
              <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:4px;">PILGRIM FLOW FIELD PHOTO</div>
              <img src="assets/palkhi_procession_1785244851342.jpg" style="width:100%; height:110px; object-fit:cover; border:1px solid var(--border-main);" alt="Warkaris">
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Strip: Incident Log Ticker -->
      <div class="incident-ticker-bar">
        <div class="ticker-label">INCIDENT LOG</div>
        <div class="ticker-content">
          <div class="ticker-text" id="incidentLogText">
            [18:48:10] CAM-12 Wakhri Phata: Density peak detected (88%) -- [18:45:22] Medical alert raised at Sector 4: Pilgrim fainting, Ambulance MH-12-PA-4022 dispatched -- [18:41:05] Lost Person Case #LF-802: Facial match confidence 89% on CAM-04 -- [18:38:00] Solapur Highway Diversion Gate 2 opened -- [18:30:15] Water tanker #WT-09 refilled at Wakhri Station.
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SCREEN 2: CROWD INTELLIGENCE ==================== -->
    <section id="view-crowd" class="view-section">
      <div class="section-bar">
        <div class="section-title">
          <i data-lucide="bar-chart-3" style="width:16px; height:16px;"></i>
          <span>Zone Density Analytics & Congestion Forecast</span>
        </div>
        <div class="section-sub">
          Crowd Density Monitoring across 6 Primary Pilgrimage Zones
        </div>
      </div>

      <div class="crowd-view-grid">
        <!-- Left: Zone Density Table -->
        <div class="panel-card" style="padding:0;">
          <div class="panel-header">
            <span>ZONE-WISE CROWD DENSITY TABLE</span>
            <span>UPDATED: JUST NOW</span>
          </div>
          <div class="govt-table-container" style="border:none; margin:0;">
            <table class="govt-table">
              <thead>
                <tr>
                  <th>Zone Name</th>
                  <th>Density %</th>
                  <th>Trend</th>
                  <th>Recommended Action</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Pandharpur Chowk</strong></td>
                  <td><span class="density-tag red">94%</span></td>
                  <td><i data-lucide="trending-up" style="width:12px; height:12px; color:var(--status-red);"></i> Rising</td>
                  <td>Divert pilgrim queue via North Ring Road</td>
                </tr>
                <tr>
                  <td><strong>Wakhri Phata</strong></td>
                  <td><span class="density-tag orange">88%</span></td>
                  <td><i data-lucide="trending-up" style="width:12px; height:12px; color:var(--status-orange);"></i> Steady High</td>
                  <td>Deploy 4 extra police constables to junction</td>
                </tr>
                <tr>
                  <td><strong>Vakhri Naka</strong></td>
                  <td><span class="density-tag yellow">74%</span></td>
                  <td><i data-lucide="minus" style="width:12px; height:12px; color:var(--status-yellow);"></i> Stable</td>
                  <td>Monitor bottleneck near bridge entry</td>
                </tr>
                <tr>
                  <td><strong>Saswad Highway Stop</strong></td>
                  <td><span class="density-tag yellow">62%</span></td>
                  <td><i data-lucide="trending-down" style="width:12px; height:12px; color:var(--status-green);"></i> Easing</td>
                  <td>Normal traffic regulation</td>
                </tr>
                <tr>
                  <td><strong>Tarapur Phata</strong></td>
                  <td><span class="density-tag green">45%</span></td>
                  <td><i data-lucide="trending-down" style="width:12px; height:12px; color:var(--status-green);"></i> Clear</td>
                  <td>Allow local supply vehicle passage</td>
                </tr>
                <tr>
                  <td><strong>Alandi Corridor</strong></td>
                  <td><span class="density-tag green">35%</span></td>
                  <td><i data-lucide="minus" style="width:12px; height:12px; color:var(--status-green);"></i> Low</td>
                  <td>Standard patrol active</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Right: Plain Gridlined Congestion Forecast Chart -->
        <div class="chart-card">
          <div class="chart-title">2-HOUR CONGESTION FORECAST MODEL</div>
          <div style="font-size:11px; color:var(--text-secondary); margin-bottom:12px;">
            Predicted crowd accumulation at Wakhri Phata & Pandharpur Chowk (19:00 - 21:00 IST)
          </div>
          <div style="height: 300px; position: relative;">
            <canvas id="forecastChart"></canvas>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SCREEN 3: LOST & FOUND DESK ==================== -->
    <section id="view-lost" class="view-section">
      <div class="section-bar">
        <div class="section-title">
          <i data-lucide="user-search" style="width:16px; height:16px;"></i>
          <span>Lost & Found Incident Desk (Automated Match)</span>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="govt-btn" onclick="alert('New case entry form initiated.')">
            <i data-lucide="plus" style="width:12px; height:12px;"></i> Register New Case
          </button>
        </div>
      </div>

      <div class="lost-found-grid">
        <!-- Left Column: Plain Table of Active Cases -->
        <div class="govt-table-container">
          <table class="govt-table">
            <thead>
              <tr>
                <th>Photo</th>
                <th>Case ID</th>
                <th>Name</th>
                <th>Age / Gender</th>
                <th>Clothing Description (Marathi & Eng)</th>
                <th>Last Seen Cam</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="photo-placeholder-box">
                    <i data-lucide="user" style="width:18px; height:18px;"></i>
                  </div>
                </td>
                <td><strong>#LF-802</strong></td>
                <td>Maruti Kisan Shinde</td>
                <td>68 / M</td>
                <td>पांढरा कुर्ता, धोती, पांढरी टोपी (White Kurta-Dhoti, Gandhi topi, carrying Tulsi mala)</td>
                <td>CAM-04 (Pandharpur)</td>
                <td><span class="density-tag red">MATCH (89%)</span></td>
                <td>
                  <button class="govt-btn btn-outline" onclick="showTranscript('LF-802')">View Call</button>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="photo-placeholder-box">
                    <i data-lucide="user" style="width:18px; height:18px;"></i>
                  </div>
                </td>
                <td><strong>#LF-805</strong></td>
                <td>Anandita Ramesh Kulkarni</td>
                <td>9 / F</td>
                <td>पिवळा परकर पोलका (Yellow traditional dress, gold bangles)</td>
                <td>CAM-12 (Wakhri)</td>
                <td><span class="density-tag yellow">SEARCHING</span></td>
                <td>
                  <button class="govt-btn btn-outline" onclick="showTranscript('LF-805')">View Call</button>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="photo-placeholder-box">
                    <i data-lucide="user" style="width:18px; height:18px;"></i>
                  </div>
                </td>
                <td><strong>#LF-799</strong></td>
                <td>Dnyaneshwar Mahadev Jadhav</td>
                <td>72 / M</td>
                <td>पांढरा पोशाख, लाल पटका (White dress, red scarf around neck)</td>
                <td>CAM-08 (Saswad)</td>
                <td><span class="density-tag green">REUNITED</span></td>
                <td>
                  <button class="govt-btn btn-disabled">Resolved</button>
                </td>
              </tr>
              <tr>
                <td>
                  <div class="photo-placeholder-box">
                    <i data-lucide="user" style="width:18px; height:18px;"></i>
                  </div>
                </td>
                <td><strong>#LF-808</strong></td>
                <td>Sunita Vitthal Patil</td>
                <td>54 / F</td>
                <td>हिरवी नऊवारी साडी, तुळशीचे वृंदावन डोक्यावर (Green Navvari saree)</td>
                <td>CAM-01 (Alandi)</td>
                <td><span class="density-tag yellow">SEARCHING</span></td>
                <td>
                  <button class="govt-btn btn-outline" onclick="showTranscript('LF-808')">View Call</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right Column: Plain Devanagari Transcript Snippet -->
        <div class="transcript-panel">
          <div style="font-weight:700; color:var(--maroon-primary); font-size:13px; margin-bottom:4px;">
            CALL-TO-CASE PIPELINE TRANSCRIPT
          </div>
          <div style="font-size:11px; color:var(--text-secondary); border-bottom:1px solid var(--border-main); padding-bottom:6px;">
            Helpline 112 Audio Recording Snippet (Deccan Dialect) &bull; Case #LF-802
          </div>

          <div class="transcript-box" id="transcriptBox">
"हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."

[Audio Analysis Summary]:
- Subject: Male, ~68 yrs
- Clothing: White Kurta, Dhoti, White Cap, Tulsi Mala
- Audio Confidence score: High (0.94)
- Vision Cross-Match: CAM-04 Pandharpur Chowk frame #4812 matching features.
          </div>

          <div style="margin-top:12px; display:flex; gap:8px;">
            <button class="govt-btn" onclick="alert('Dispatching mobile patrol team to CAM-04 location.')">
              Dispatch Nearby Volunteer
            </button>
            <button class="govt-btn btn-outline" onclick="alert('PA Announcement request queued for Wakhri Loudspeaker System.')">
              Queue PA Announcement
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SCREEN 4: MEDICAL ALERTS VIEW ==================== -->
    <section id="view-medical" class="view-section">
      <div class="section-bar">
        <div class="section-title">
          <i data-lucide="activity" style="width:16px; height:16px;"></i>
          <span>Medical Emergencies & Heat-Risk Monitoring</span>
        </div>
        <div class="section-sub">
          Active Field Ambulances: 8 &bull; Emergency Response Hubs: 4
        </div>
      </div>

      <div class="medical-view-grid">
        <!-- Left: Plain Card List of Alerts -->
        <div>
          <div class="panel-header" style="margin-bottom:8px;">
            <span>ACTIVE MEDICAL ALERTS</span>
            <span>2 REQUIRING IMMEDIATE ACKNOWLEDGEMENT</span>
          </div>

          <div class="alert-card-item" id="alert-1">
            <div>
              <div style="font-weight:700; color:var(--status-red); font-size:13px;">
                FALL DETECTED / FAINTING PILGRIM
              </div>
              <div style="font-size:11px; color:var(--text-secondary); margin:2px 0;">
                Location: Wakhri Phata Km 184 &bull; Elapsed: 4 mins ago
              </div>
              <div style="font-size:11px; color:var(--text-muted);">
                Assigned Volunteer: Team Bravo (V. R. Kadam)
              </div>
            </div>
            <div>
              <button class="govt-btn" onclick="acknowledgeAlert('alert-1')">Acknowledge Alert</button>
            </div>
          </div>

          <div class="alert-card-item" id="alert-2">
            <div>
              <div style="font-weight:700; color:var(--status-orange); font-size:13px;">
                CROWD HEAT EXHAUSTION RISK (SECTOR 5)
              </div>
              <div style="font-size:11px; color:var(--text-secondary); margin:2px 0;">
                Location: Pandharpur Temple Corridor &bull; Elapsed: 12 mins ago
              </div>
              <div style="font-size:11px; color:var(--text-muted);">
                Assigned Volunteer: Medical Van #MV-02
              </div>
            </div>
            <div>
              <button class="govt-btn" onclick="acknowledgeAlert('alert-2')">Acknowledge Alert</button>
            </div>
          </div>

          <div class="alert-card-item acknowledged">
            <div>
              <div style="font-weight:700; color:var(--status-green); font-size:13px;">
                DEHYDROGENATION ASSIST & REHYDRATION (RESOLVED)
              </div>
              <div style="font-size:11px; color:var(--text-secondary); margin:2px 0;">
                Location: Saswad Rest Stop &bull; Resolved 35 mins ago
              </div>
              <div style="font-size:11px; color:var(--text-muted);">
                Handled by: Red Cross Volunteer Post #3
              </div>
            </div>
            <div>
              <button class="govt-btn btn-disabled">Acknowledged</button>
            </div>
          </div>
        </div>

        <!-- Right: Heat-Risk Readout Box (Plain numbers in bordered box) -->
        <div class="heat-risk-box">
          <div style="font-weight:700; font-family:var(--font-serif); font-size:14px; color:var(--maroon-primary); margin-bottom:8px; border-bottom:1px solid var(--border-main); padding-bottom:4px;">
            HEAT-RISK COMPUTED READOUT
          </div>

          <div class="metric-row">
            <span class="metric-key">Ambient Temperature:</span>
            <span class="metric-val">34° C</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">Relative Humidity:</span>
            <span class="metric-val">72%</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">Computed Risk Index:</span>
            <span class="metric-val" style="color:var(--status-orange);">7.8 / 10 (MODERATE HEAT RISK)</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">Water Stations Active:</span>
            <span class="metric-val">12 Operational</span>
          </div>
          <div class="metric-row">
            <span class="metric-key">ORSL Sachet Supplies:</span>
            <span class="metric-val">14,200 Packets Available</span>
          </div>

          <div style="margin-top:14px; background:var(--bg-subtle); padding:8px; border:1px solid var(--border-main); font-size:11px; color:var(--text-secondary);">
            <strong>Advisory Action:</strong> Trigger mist sprayer vans at Wakhri Junction & increase water distribution post deployment by 20%.
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SCREEN 5: RESOURCE MANAGEMENT ==================== -->
    <section id="view-resources" class="view-section">
      <div class="section-bar">
        <div class="section-title">
          <i data-lucide="layers" style="width:16px; height:16px;"></i>
          <span>Resource Deployment & Route Diversion Control</span>
        </div>
        <div class="section-sub">
          Police Forces, Water Tankers, Food Vans & Medical Units Logistics
        </div>
      </div>

      <div class="resource-grid">
        <!-- Left: Resource Table -->
        <div class="govt-table-container">
          <table class="govt-table">
            <thead>
              <tr>
                <th>Resource Type</th>
                <th>Deployed Count</th>
                <th>Available Count</th>
                <th>Current Key Location</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Water Tankers (10,000L)</strong></td>
                <td>12 Units</td>
                <td>8 Units</td>
                <td>Wakhri Phata & Saswad Stop</td>
                <td><span class="density-tag green">OPTIMAL</span></td>
              </tr>
              <tr>
                <td><strong>Mobile Medical Vans</strong></td>
                <td>6 Units</td>
                <td>2 Units</td>
                <td>Sector 2, 4 & Pandharpur Depot</td>
                <td><span class="density-tag green">ACTIVE</span></td>
              </tr>
              <tr>
                <td><strong>Police Patrol Squads</strong></td>
                <td>45 Squads</td>
                <td>15 Squads</td>
                <td>Pilgrim Highway Corridor</td>
                <td><span class="density-tag green">DEPLOYED</span></td>
              </tr>
              <tr>
                <td><strong>Volunteer Dindi Stewards</strong></td>
                <td>120 Personnel</td>
                <td>30 Personnel</td>
                <td>Palkhi Procession Perimeter</td>
                <td><span class="density-tag green">ACTIVE</span></td>
              </tr>
              <tr>
                <td><strong>Food Distribution Vans</strong></td>
                <td>18 Units</td>
                <td>5 Units</td>
                <td>Bhalwani & Tarapur Phata</td>
                <td><span class="density-tag green">OPTIMAL</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right: Route Status Simple List -->
        <div>
          <div class="panel-header" style="margin-bottom:8px;">
            <span>ROUTE STATUS & DIVERSION LOG</span>
          </div>

          <div class="route-status-item">
            <div>
              <div style="font-weight:600; font-size:12px;">NH-9 Solapur Highway Junction</div>
              <div style="font-size:10px; color:var(--text-secondary);">Main heavy vehicle bypass route</div>
            </div>
            <span class="status-pill diverted">Diverted</span>
          </div>

          <div class="route-status-item">
            <div>
              <div style="font-weight:600; font-size:12px;">Pune-Saswad Pilgrimage Road</div>
              <div style="font-size:10px; color:var(--text-secondary);">Primary Palkhi corridor</div>
            </div>
            <span class="status-pill open">Open (Pilgrims Only)</span>
          </div>

          <div class="route-status-item">
            <div>
              <div style="font-weight:600; font-size:12px;">Wakhri Phata Inner Access Road</div>
              <div style="font-size:10px; color:var(--text-secondary);">Heavy congestion bottleneck zone</div>
            </div>
            <span class="status-pill closed">Closed to Traffic</span>
          </div>

          <div class="route-status-item">
            <div>
              <div style="font-weight:600; font-size:12px;">Pandharpur Temple Ring Road</div>
              <div style="font-size:10px; color:var(--text-secondary);">Emergency ambulance corridor</div>
            </div>
            <span class="status-pill open">Emergency Access</span>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- CCTV Expand Detail Modal -->
  <div class="modal-backdrop" id="camModal">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title" id="modalCamTitle">CCTV CAMERA EXPANDED VIEW</div>
        <button class="close-modal-btn" onclick="closeCamModal()">&times;</button>
      </div>
      <div style="height:360px; background:#000; position:relative; overflow:hidden; border:1px solid #333;">
        <img id="modalCamImg" src="assets/cctv_wakhri_phata_1785244836537.jpg" style="width:100%; height:100%; object-fit:cover;" alt="Cam detail">
        <div class="cctv-overlay">
          <div class="cctv-top-info">
            <span class="cctv-cam-id" id="modalCamId">CAM-12</span>
            <span class="cctv-timestamp" style="color:#00FF66;">LIVE DENSITY FEED</span>
          </div>
          <div class="cctv-bottom-info">
            <span class="cctv-location" id="modalCamStatus" style="background:rgba(0,0,0,0.7); padding:4px 8px;">Density 88%</span>
          </div>
        </div>
      </div>
      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:11px; color:var(--text-secondary);" id="modalCamSub">Bounding Box Analytics Active</span>
        <div style="display:flex; gap:8px;">
          <button class="govt-btn" onclick="alert('PTZ Pan-Tilt-Zoom command dispatched.')">PTZ Control</button>
          <button class="govt-btn btn-outline" onclick="closeCamModal()">Close Window</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Application Logic JavaScript -->
  <script src="app.js"></script>

</body>
</html>
```

---

## 3. `Frontend/styles.css`

```css
/* WariSetu AI (v2 Light Theme - Grounded Government Portal Specification) */

:root {
  --bg-khadi: #F7F3EC;
  --bg-card: #FFFFFF;
  --bg-subtle: #EFECE6;
  --bg-darker: #E5E0D7;
  
  --maroon-primary: #7A1F1F;
  --maroon-dark: #5C1515;
  --maroon-light: #9B2D2D;
  --maroon-bg: #F4EAEB;
  
  --saffron-gold: #D98E2C;
  --saffron-light: #FAF0E1;

  --text-primary: #2B2623;
  --text-secondary: #5A534C;
  --text-muted: #847C74;

  --border-main: #D8D1C5;
  --border-strong: #B5ACA0;
  --border-focus: #7A1F1F;

  /* Earthy Status Palette (Muted, Non-Neon) */
  --status-green: #2E5B36;
  --status-green-bg: #E8F2EA;
  --status-yellow: #B07817;
  --status-yellow-bg: #FAF3E6;
  --status-orange: #B8551B;
  --status-orange-bg: #FAECE5;
  --status-red: #9A2525;
  --status-red-bg: #F9EAEB;

  --font-serif: 'Tiro Devanagari Marathi', 'IBM Plex Serif', Georgia, serif;
  --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-khadi);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 13px;
  line-height: 1.4;
  -webkit-font-smoothing: antialiased;
}

/* Warli Traditional Border Strip */
.top-warli-border {
  height: 8px;
  background-color: var(--maroon-primary);
  background-image: repeating-linear-gradient(
    45deg,
    var(--saffron-gold) 0,
    var(--saffron-gold) 6px,
    var(--maroon-primary) 6px,
    var(--maroon-primary) 14px
  );
  border-bottom: 1px solid var(--maroon-dark);
}

/* Header & Government Branding */
.gov-header {
  background-color: #FFFFFF;
  border-bottom: 2px solid var(--border-strong);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo-img {
  height: 56px;
  width: auto;
  border-radius: 2px;
  border: 1px solid var(--border-main);
  object-fit: contain;
  background-color: var(--bg-khadi);
  padding: 1px;
}

.mh-police-badge {
  width: 44px;
  height: 44px;
  background: var(--maroon-primary);
  color: #FFF;
  border-radius: 2px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 9px;
  border: 1px solid var(--maroon-dark);
  text-align: center;
  line-height: 1.1;
  padding: 2px;
}

.brand-titles {
  display: flex;
  flex-direction: column;
}

.brand-marathi {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 700;
  color: var(--maroon-primary);
  letter-spacing: 0.2px;
  line-height: 1.1;
}

.brand-english {
  font-family: var(--font-sans);
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 12px;
}

.meta-pill {
  background: var(--bg-subtle);
  border: 1px solid var(--border-main);
  padding: 4px 10px;
  border-radius: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: var(--status-green);
  border-radius: 50%;
}

/* Primary Navigation Bar */
.nav-bar {
  background-color: var(--maroon-primary);
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid var(--maroon-dark);
  overflow-x: auto;
}

.nav-tab {
  background: none;
  border: none;
  color: #E2D7D7;
  padding: 10px 16px;
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.nav-tab:hover {
  color: #FFF;
  background-color: rgba(255,255,255,0.06);
}

.nav-tab.active {
  color: #FFF;
  background-color: var(--maroon-dark);
  border-bottom-color: var(--saffron-gold);
}

.nav-tab .badge {
  background-color: var(--saffron-gold);
  color: #000;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 2px;
  font-family: var(--font-mono);
}

/* Main Layout Structure */
.app-container {
  padding: 12px;
  max-width: 1600px;
  margin: 0 auto;
}

.view-section {
  display: none;
}

.view-section.active {
  display: block;
}

/* Section Header */
.section-bar {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 8px 12px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-left: 4px solid var(--maroon-primary);
}

.section-title {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  color: var(--maroon-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-sub {
  font-size: 11px;
  color: var(--text-secondary);
}

/* Screen 1: Main Command Center Layout */
.command-grid {
  display: grid;
  grid-template-columns: 340px 1fr 300px;
  gap: 12px;
  margin-bottom: 12px;
}

@media (max-width: 1280px) {
  .command-grid {
    grid-template-columns: 300px 1fr;
  }
  .right-col-panel {
    grid-column: span 2;
  }
}

@media (max-width: 900px) {
  .command-grid {
    grid-template-columns: 1fr;
  }
  .right-col-panel {
    grid-column: span 1;
  }
}

/* CCTV Panel (Left Column) */
.cctv-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 170px);
  overflow-y: auto;
  padding-right: 2px;
}

.panel-card {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-radius: 2px;
  overflow: hidden;
}

.panel-header {
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border-main);
  padding: 6px 10px;
  font-weight: 600;
  font-size: 12px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cctv-tile {
  background: #0F1215;
  border: 1px solid var(--border-strong);
  border-left-width: 4px;
  position: relative;
  height: 125px;
  overflow: hidden;
  cursor: pointer;
}

.cctv-tile.status-normal { border-left-color: var(--status-green); }
.cctv-tile.status-moderate { border-left-color: var(--status-yellow); }
.cctv-tile.status-heavy { border-left-color: var(--status-orange); }
.cctv-tile.status-critical { border-left-color: var(--status-red); }

.cctv-feed-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: contrast(1.1) brightness(0.9) grayscale(0.2);
  opacity: 0.85;
}

.cctv-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 40%, transparent 60%, rgba(0,0,0,0.7) 100%);
}

.cctv-top-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  color: #FFF;
  font-family: var(--font-mono);
  font-size: 10px;
  text-shadow: 0 1px 2px #000;
}

.cctv-cam-id {
  background: rgba(0,0,0,0.65);
  padding: 2px 4px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 2px;
}

.cctv-timestamp {
  background: rgba(0,0,0,0.65);
  padding: 2px 4px;
  color: #00FF66;
}

.cctv-bottom-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.cctv-location {
  color: #FFF;
  font-size: 11px;
  font-weight: 600;
  text-shadow: 0 1px 3px #000;
}

.density-tag {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 5px;
  border-radius: 2px;
  font-family: var(--font-mono);
}

.density-tag.green { background: var(--status-green); color: #FFF; }
.density-tag.yellow { background: var(--status-yellow); color: #FFF; }
.density-tag.orange { background: var(--status-orange); color: #FFF; }
.density-tag.red { background: var(--status-red); color: #FFF; }

/* Center Route Map */
.map-container {
  height: calc(100vh - 220px);
  min-height: 520px;
  border: 1px solid var(--border-main);
  background: #EAE6DF;
  position: relative;
  border-radius: 2px;
}

#routeMap {
  width: 100%;
  height: 100%;
}

.map-controls-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  background: #FFF;
  border: 1px solid var(--border-strong);
  padding: 8px;
  border-radius: 2px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 11px;
}

.map-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* Stat Panels (Right Column) */
.stat-panel-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.govt-stat-box {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 12px;
  border-radius: 2px;
  border-left: 4px solid var(--maroon-primary);
}

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-sans);
  color: var(--maroon-primary);
  margin: 4px 0 2px 0;
}

.stat-subtext {
  font-size: 11px;
  color: var(--text-muted);
}

/* Incident Log Ticker (Bottom Bar) */
.incident-ticker-bar {
  background: #231F1D;
  color: #EFECE6;
  border: 1px solid #111;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 11px;
  border-radius: 2px;
}

.ticker-label {
  background: var(--maroon-primary);
  color: #FFF;
  padding: 2px 8px;
  font-weight: bold;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  white-space: nowrap;
}

.ticker-content {
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
}

.ticker-text {
  display: inline-block;
  animation: scrollTicker 35s linear infinite;
}

@keyframes scrollTicker {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}

/* Government Plain Tables */
.govt-table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-radius: 2px;
  overflow-x: auto;
  margin-bottom: 12px;
}

.govt-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 12px;
}

.govt-table th {
  background: var(--bg-subtle);
  color: var(--text-primary);
  font-weight: 600;
  border-bottom: 2px solid var(--border-strong);
  padding: 8px 12px;
  white-space: nowrap;
}

.govt-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-main);
  vertical-align: middle;
}

.govt-table tr:hover {
  background-color: var(--bg-khadi);
}

/* Rectangular Government Buttons */
.govt-btn {
  background-color: var(--maroon-primary);
  color: #FFFFFF;
  border: 1px solid var(--maroon-dark);
  padding: 5px 12px;
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: none;
  transition: background-color 0.1s ease;
}

.govt-btn:hover {
  background-color: var(--maroon-dark);
}

.govt-btn.btn-outline {
  background-color: transparent;
  color: var(--maroon-primary);
  border-color: var(--maroon-primary);
}

.govt-btn.btn-outline:hover {
  background-color: var(--maroon-bg);
}

.govt-btn.btn-disabled {
  background-color: #D6D1C7;
  border-color: #C2BBB0;
  color: #7A746B;
  cursor: not-allowed;
}

/* Screen 2: Crowd Intelligence Layout */
.crowd-view-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 1024px) {
  .crowd-view-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 14px;
  border-radius: 2px;
}

.chart-title {
  font-family: var(--font-serif);
  font-size: 14px;
  font-weight: 700;
  color: var(--maroon-primary);
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border-main);
  padding-bottom: 4px;
}

/* Screen 3: Lost & Found Desk */
.lost-found-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
}

@media (max-width: 1024px) {
  .lost-found-grid {
    grid-template-columns: 1fr;
  }
}

.photo-placeholder-box {
  width: 36px;
  height: 36px;
  background: var(--bg-darker);
  border: 1px solid var(--border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.transcript-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-left: 4px solid var(--saffron-gold);
  padding: 14px;
  border-radius: 2px;
}

.transcript-box {
  background: var(--bg-khadi);
  border: 1px solid var(--border-main);
  padding: 10px;
  font-family: var(--font-serif);
  font-size: 13px;
  line-height: 1.6;
  color: #3B332B;
  margin-top: 8px;
  white-space: pre-line;
}

/* Screen 4: Medical Alerts Layout */
.medical-view-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
}

@media (max-width: 1024px) {
  .medical-view-grid {
    grid-template-columns: 1fr;
  }
}

.alert-card-item {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-left: 4px solid var(--status-red);
  padding: 12px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-card-item.acknowledged {
  border-left-color: var(--status-green);
  opacity: 0.85;
}

.heat-risk-box {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 14px;
  border-radius: 2px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-main);
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-key {
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-val {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--text-primary);
}

/* Screen 5: Resource Management */
.resource-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
}

@media (max-width: 1024px) {
  .resource-grid {
    grid-template-columns: 1fr;
  }
}

.route-status-item {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 10px 12px;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-pill {
  padding: 2px 8px;
  font-size: 10px;
  font-weight: bold;
  border-radius: 2px;
  text-transform: uppercase;
  font-family: var(--font-mono);
}

.status-pill.open { background: var(--status-green-bg); color: var(--status-green); border: 1px solid var(--status-green); }
.status-pill.closed { background: var(--status-red-bg); color: var(--status-red); border: 1px solid var(--status-red); }
.status-pill.diverted { background: var(--status-yellow-bg); color: var(--status-yellow); border: 1px solid var(--status-yellow); }

/* Modal Styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.6);
  z-index: 2000;
  display: none;
  align-items: center;
  justify-content: center;
}

.modal-backdrop.open {
  display: flex;
}

.modal-content {
  background: #FFF;
  border: 2px solid var(--maroon-primary);
  width: 90%;
  max-width: 800px;
  padding: 16px;
  border-radius: 2px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-main);
  padding-bottom: 8px;
  margin-bottom: 12px;
}

.modal-title {
  font-family: var(--font-serif);
  font-size: 16px;
  color: var(--maroon-primary);
  font-weight: 700;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-secondary);
  cursor: pointer;
}
```

---

## 4. `Frontend/app.js`

```javascript
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
```
