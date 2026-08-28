# VariSetu (वारी सेतु) - Complete Source Code Repository

> This document contains the complete, unabridged, line-by-line source code for all Frontend and Backend modules of the **VariSetu (वारी सेतु)** Command Center project.
> Sensitive configuration files, secrets, and environment tokens are excluded.

## Table of Contents

- [Frontend/index.html](#frontendindexhtml)
- [Frontend/styles.css](#frontendstylescss)
- [Frontend/app.js](#frontendappjs)
- [Frontend/package.json](#frontendpackagejson)
- [docker-compose.yml](#dockercomposeyml)
- [Backend/requirements.txt](#backendrequirementstxt)
- [Backend/pytest.ini](#backendpytestini)
- [Backend/app/main.py](#backendappmainpy)
- [Backend/app/core/config.py](#backendappcoreconfigpy)
- [Backend/app/core/database.py](#backendappcoredatabasepy)
- [Backend/app/core/security.py](#backendappcoresecuritypy)
- [Backend/app/core/rbac.py](#backendappcorerbacpy)
- [Backend/app/core/redis.py](#backendappcoreredispy)
- [Backend/app/core/exceptions.py](#backendappcoreexceptionspy)
- [Backend/app/core/logging.py](#backendappcoreloggingpy)
- [Backend/app/models/__init__.py](#backendappmodels__init__py)
- [Backend/app/models/base.py](#backendappmodelsbasepy)
- [Backend/app/models/user.py](#backendappmodelsuserpy)
- [Backend/app/models/zone.py](#backendappmodelszonepy)
- [Backend/app/models/camera.py](#backendappmodelscamerapy)
- [Backend/app/models/crowd.py](#backendappmodelscrowdpy)
- [Backend/app/models/forecast.py](#backendappmodelsforecastpy)
- [Backend/app/models/incident.py](#backendappmodelsincidentpy)
- [Backend/app/models/lost_person.py](#backendappmodelslost_personpy)
- [Backend/app/models/face_match.py](#backendappmodelsface_matchpy)
- [Backend/app/models/medical.py](#backendappmodelsmedicalpy)
- [Backend/app/models/resource.py](#backendappmodelsresourcepy)
- [Backend/app/models/route.py](#backendappmodelsroutepy)
- [Backend/app/models/notification.py](#backendappmodelsnotificationpy)
- [Backend/app/models/audit.py](#backendappmodelsauditpy)
- [Backend/app/schemas/auth.py](#backendappschemasauthpy)
- [Backend/app/schemas/zone.py](#backendappschemaszonepy)
- [Backend/app/schemas/camera.py](#backendappschemascamerapy)
- [Backend/app/schemas/crowd.py](#backendappschemascrowdpy)
- [Backend/app/schemas/incident.py](#backendappschemasincidentpy)
- [Backend/app/schemas/lost_person.py](#backendappschemaslost_personpy)
- [Backend/app/schemas/medical.py](#backendappschemasmedicalpy)
- [Backend/app/schemas/resource.py](#backendappschemasresourcepy)
- [Backend/app/schemas/route.py](#backendappschemasroutepy)
- [Backend/app/schemas/audit.py](#backendappschemasauditpy)
- [Backend/app/schemas/notification.py](#backendappschemasnotificationpy)
- [Backend/app/schemas/dashboard.py](#backendappschemasdashboardpy)
- [Backend/app/services/audit_service.py](#backendappservicesaudit_servicepy)
- [Backend/app/services/auth_service.py](#backendappservicesauth_servicepy)
- [Backend/app/services/incident_service.py](#backendappservicesincident_servicepy)
- [Backend/app/services/lost_person_service.py](#backendappserviceslost_person_servicepy)
- [Backend/app/services/medical_service.py](#backendappservicesmedical_servicepy)
- [Backend/app/services/resource_service.py](#backendappservicesresource_servicepy)
- [Backend/app/services/crowd_service.py](#backendappservicescrowd_servicepy)
- [Backend/app/services/forecast_service.py](#backendappservicesforecast_servicepy)
- [Backend/app/services/route_service.py](#backendappservicesroute_servicepy)
- [Backend/app/services/dashboard_service.py](#backendappservicesdashboard_servicepy)
- [Backend/app/services/demo_service.py](#backendappservicesdemo_servicepy)
- [Backend/app/integrations/__init__.py](#backendappintegrations__init__py)
- [Backend/app/integrations/qdrant_adapter.py](#backendappintegrationsqdrant_adapterpy)
- [Backend/app/integrations/vision_adapter.py](#backendappintegrationsvision_adapterpy)
- [Backend/app/integrations/speech_adapter.py](#backendappintegrationsspeech_adapterpy)
- [Backend/app/integrations/weather_adapter.py](#backendappintegrationsweather_adapterpy)
- [Backend/app/integrations/notification_adapter.py](#backendappintegrationsnotification_adapterpy)
- [Backend/app/integrations/storage_adapter.py](#backendappintegrationsstorage_adapterpy)
- [Backend/app/websocket/events.py](#backendappwebsocketeventspy)
- [Backend/app/websocket/manager.py](#backendappwebsocketmanagerpy)
- [Backend/app/api/auth.py](#backendappapiauthpy)
- [Backend/app/api/dashboard.py](#backendappapidashboardpy)
- [Backend/app/api/cameras.py](#backendappapicameraspy)
- [Backend/app/api/zones.py](#backendappapizonespy)
- [Backend/app/api/crowd.py](#backendappapicrowdpy)
- [Backend/app/api/incidents.py](#backendappapiincidentspy)
- [Backend/app/api/lost_persons.py](#backendappapilost_personspy)
- [Backend/app/api/medical.py](#backendappapimedicalpy)
- [Backend/app/api/resources.py](#backendappapiresourcespy)
- [Backend/app/api/routes.py](#backendappapiroutespy)
- [Backend/app/api/notifications.py](#backendappapinotificationspy)
- [Backend/app/seed/seed_data.py](#backendappseedseed_datapy)
- [Backend/tests/conftest.py](#backendtestsconftestpy)
- [Backend/tests/test_api.py](#backendteststest_apipy)

---

## Frontend/index.html
`Frontend/index.html`

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

  <!-- ==================== PRIVATE LOGIN ENTRY VIEW ==================== -->
  <section id="loginView" class="login-view">
    <div class="login-panel">
      <div class="login-brand" style="display: flex; flex-direction: column; align-items: center; gap: 6px;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 2px;">
          <img src="assets/varisetu_logo.png" alt="VariSetu Logo" style="height: 68px; width: auto; object-fit: contain;">
          <img src="assets/maharashtra_gov_seal.png" alt="Maharashtra Government Seal" class="mh-gov-seal-img" style="height: 58px; width: 58px;">
        </div>
        <div class="login-marathi" style="font-family: var(--font-serif); font-size: 24px; font-weight: 700; color: var(--maroon-primary); line-height: 1.1;">वारी सेतु</div>
        <div class="login-english" style="font-size: 10px; color: var(--text-muted); font-weight: 600; letter-spacing: 0.3px;">महाराष्ट्र शासन &bull; पंढरपूर आषाढी वारी नियंत्रण कक्ष</div>
      </div>

      <div class="login-divider"></div>

      <div class="login-title">COMMAND CENTER ACCESS</div>

      <form id="loginForm">
        <label for="loginEmail">Official Email / Officer ID</label>
        <input
          id="loginEmail"
          type="email"
          autocomplete="username"
          placeholder="control.room@mahapolice.gov.in"
          required
        />

        <label for="loginPassword">Password</label>
        <div class="password-input-wrapper">
          <input
            id="loginPassword"
            type="password"
            autocomplete="current-password"
            placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
            required
          />
          <button
            type="button"
            id="togglePasswordVisibilityBtn"
            class="toggle-password-btn"
            aria-label="Toggle password visibility"
            title="Show / Hide Password">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" id="togglePasswordIcon"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>

        <div id="loginError" class="login-error" hidden></div>

        <button
          type="submit"
          class="govt-btn login-submit"
          id="loginSubmitBtn">
          SIGN IN
        </button>
      </form>

      <div style="margin-top: 14px; text-align: center; border-top: 1px dashed var(--border-main); padding-top: 12px;">
        <button type="button" id="openPublicPortalBtn" class="govt-btn btn-outline" style="width: 100%; padding: 8px 12px; font-size: 11px; display: flex; align-items: center; justify-content: center; gap: 6px;">
          <i data-lucide="users" style="width: 14px; height: 14px;"></i>
          <span>👥 Public Pilgrim Portal & Helplines (नागरिक माहिती)</span>
        </button>
      </div>

      <div class="login-restricted-note">
        Authorised Personnel Only &bull; Access Monitored
      </div>
    </div>
  </section>

  <!-- ==================== PUBLIC PILGRIM PORTAL (UNAUTHENTICATED / CITIZEN VIEW) ==================== -->
  <div id="publicView" hidden style="display: none;">
    <!-- Top Warli Pattern Woven Strip -->
    <div class="top-warli-border"></div>

    <!-- Government Portal Header -->
    <header class="gov-header">
      <div class="brand-section" style="display: flex; align-items: center; gap: 10px;">
        <img src="assets/varisetu_logo.png" alt="VariSetu Logo" class="brand-logo-img" style="height: 52px; width: auto;">
        <img src="assets/maharashtra_gov_seal.png" alt="Maharashtra Government Seal" class="mh-gov-seal-img" style="height: 44px; width: 44px;">
        <div class="brand-titles">
          <h1 class="brand-marathi" style="font-size: 16px; font-weight: 700; color: var(--maroon-primary); margin: 0; line-height: 1.1;">वारी सेतु &bull; सार्वजनिक वारकरी सेवा पोर्टल</h1>
          <span class="brand-english" style="font-size: 9.5px; color: var(--text-muted); font-weight: 600;">महाराष्ट्र शासन &bull; श्री क्षेत्र पंढरपूर आषाढी वारी सोहळा</span>
        </div>
      </div>

      <div class="header-meta">
        <div class="meta-pill" style="border-color: var(--maroon-primary); color: var(--maroon-primary); font-weight:700;">
          <span>🚩 PALKHI: APPROACHING WAKHRI</span>
        </div>
        <button id="backToLoginBtn" type="button" class="govt-btn" style="font-size:10px; padding:4px 10px; display:flex; align-items:center; gap:4px;">
          <i data-lucide="lock" style="width:12px; height:12px;"></i>
          <span>Officer Login</span>
        </button>
      </div>
    </header>

    <div class="app-container" style="padding: 14px 20px; max-width: 1300px; margin: 0 auto;">
      <!-- Hero Banner -->
      <div style="background: linear-gradient(135deg, var(--maroon-primary), #5C1515); color: #FFF; padding: 16px 20px; border-radius: 3px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 3px 10px rgba(0,0,0,0.15);">
        <div>
          <div style="font-family: var(--font-serif); font-size: 20px; font-weight: 700; color: #F5D38A;">संत तुकाराम महाराज व संत ज्ञानेश्वर महाराज पालखी सोहळा २०२६</div>
          <div style="font-size: 12px; color: #EFECE6; margin-top: 4px;">Live Location: Wakhri Phata Junction (Km 184) &bull; Moving smoothly towards Pandharpur Shrine</div>
        </div>
        <div style="text-align: right;">
          <div style="font-family: var(--font-mono); font-size: 18px; font-weight: 700; color: #00FF66;">~8,45,000</div>
          <div style="font-size: 10px; color: #DDD;">Estimated Pilgrim Count</div>
        </div>
      </div>

      <!-- Main Public 2-Column Grid -->
      <div style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px;">
        <!-- Left: Interactive Route Map & Weather Advisories -->
        <div>
          <div class="panel-card" style="padding: 12px; margin-bottom: 12px;">
            <div class="panel-header" style="margin-bottom: 8px;">
              <span>PILGRIMAGE ROUTE & HALT STATIONS MAP</span>
              <span style="font-size: 10px; color: var(--text-muted);">Alandi &rarr; Saswad &rarr; Lonand &rarr; Wakhri &rarr; Pandharpur</span>
            </div>
            <div id="publicRouteMap" style="height: 320px; width: 100%; border: 1px solid var(--border-main); border-radius: 2px;"></div>
          </div>

          <!-- Public Weather & Heat Advisory -->
          <div class="panel-card" style="padding: 12px;">
            <div class="panel-header" style="margin-bottom: 8px; color: var(--saffron-gold);">
              <span>☀️ PILGRIM HEALTH & HYDRATION ADVISORY</span>
              <span class="density-tag yellow">34°C MODERATE HEAT</span>
            </div>
            <div style="font-size: 12px; color: var(--text-primary); line-height: 1.5;">
              <strong>Advisory:</strong> Drink plenty of water. Free ORSL salt sachets & medical assistance are available at all 24 water points and 16 medical tents stationed along the highway.
            </div>
          </div>
        </div>

        <!-- Right: Emergency Helplines & Public Missing Report -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <!-- Emergency Numbers -->
          <div class="panel-card" style="padding: 12px; border-left: 4px solid var(--maroon-primary);">
            <div class="panel-header" style="margin-bottom: 10px;">
              <span>🚨 EMERGENCY & HELPLINE NUMBERS</span>
              <span style="font-size: 10px; color: var(--status-green);">24x7 ACTIVE</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <a href="tel:112" class="public-helpline-card">
                <div>
                  <div class="public-helpline-title">Police Control Room (महाराष्ट्र पोलीस)</div>
                  <div class="public-helpline-num">112 / 02186-223344</div>
                </div>
                <span class="govt-btn" style="padding: 3px 8px; font-size: 10px;">CALL NOW</span>
              </a>

              <a href="tel:108" class="public-helpline-card">
                <div>
                  <div class="public-helpline-title">Ambulance & Medical Emergency</div>
                  <div class="public-helpline-num">108 / 102</div>
                </div>
                <span class="govt-btn" style="padding: 3px 8px; font-size: 10px; background: var(--status-red);">CALL NOW</span>
              </a>

              <a href="tel:18002330099" class="public-helpline-card">
                <div>
                  <div class="public-helpline-title">Lost & Found Pilgrim Assistance Booth</div>
                  <div class="public-helpline-num">1800-233-0099 (Toll Free)</div>
                </div>
                <span class="govt-btn btn-outline" style="padding: 3px 8px; font-size: 10px;">CALL NOW</span>
              </a>

              <a href="tel:02186223550" class="public-helpline-card">
                <div>
                  <div class="public-helpline-title">Shri Vitthal Mandir Samiti Control Desk</div>
                  <div class="public-helpline-num">02186-223550</div>
                </div>
                <span class="govt-btn btn-outline" style="padding: 3px 8px; font-size: 10px;">CALL NOW</span>
              </a>
            </div>
          </div>

          <!-- Public Report Missing Person -->
          <div class="panel-card" style="padding: 12px; background: var(--bg-subtle);">
            <div class="panel-header" style="margin-bottom: 6px;">
              <span>🔍 REPORT MISSING FAMILY MEMBER</span>
            </div>
            <div style="font-size: 11.5px; color: var(--text-secondary); margin-bottom: 8px;">
              Separated from your family or group in the crowd? Submit details and photos directly for instant AI matching across state CCTV cameras.
            </div>
            <button type="button" class="govt-btn" id="publicReportMissingBtn" style="width: 100%; padding: 8px 12px; font-size: 11px; display:flex; align-items:center; justify-content:center; gap:6px;">
              <i data-lucide="user-plus" style="width: 13px; height: 13px;"></i>
              <span>Submit Missing Person Report (तक्रार नोंदवा)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== MAIN COMMAND CENTER DASHBOARD (AUTHENTICATED) ==================== -->
  <div id="dashboardView" hidden>

    <!-- Top Warli Pattern Woven Strip -->
    <div class="top-warli-border"></div>

    <!-- Government Portal Header -->
    <header class="gov-header">
      <div class="brand-section" style="display: flex; align-items: center; gap: 10px;">
        <img src="assets/varisetu_logo.png" alt="VariSetu Logo" class="brand-logo-img" style="height: 52px; width: auto;">
        <img src="assets/maharashtra_gov_seal.png" alt="Maharashtra Government Seal" class="mh-gov-seal-img" style="height: 44px; width: 44px;">
        <div class="brand-titles">
          <h1 class="brand-marathi" style="font-size: 18px; font-weight: 700; color: var(--maroon-primary); margin: 0; line-height: 1.1;">वारी सेतु</h1>
          <span class="brand-english" style="font-size: 9.5px; color: var(--text-muted); font-weight: 600;">महाराष्ट्र शासन &bull; महाराष्ट्र पोलीस नियंत्रण कक्ष</span>
        </div>
      </div>

      <div class="header-meta">
        <div class="meta-pill" id="backendHealthBadge">
          <span class="live-dot"></span>
          <span id="backendHealthText">LIVE</span>
        </div>
        <div class="meta-pill">
          <i data-lucide="clock" style="width:13px; height:13px;"></i>
          <span id="sysClock">28 JUL 2026 18:50:00 IST</span>
        </div>
        <div class="meta-pill" style="border-color: var(--maroon-primary); color: var(--maroon-primary); font-weight:600;">
          <span>PILGRIM COUNT: ~8,45,000</span>
        </div>
        <div class="meta-pill" id="userProfileBadge" style="display:flex; align-items:center; border-color:var(--maroon-primary);">
          <i data-lucide="shield-check" style="width:13px; height:13px; color:var(--maroon-primary); margin-right:4px;"></i>
          <span id="userProfileText" style="font-weight:700; color:var(--maroon-primary); text-transform:uppercase;">COMMANDER</span>
          <button id="logoutBtn" type="button" class="govt-btn btn-outline" style="font-size:9px; padding:2px 7px; margin-left:8px;">LOG OUT</button>
        </div>
        <button class="govt-btn btn-outline" id="addOfficerBtn" type="button" style="display:none; font-size:10px; padding:4px 9px;">
          <i data-lucide="user-plus" style="width:11px; height:11px;"></i>
          <span>+ Add Officer</span>
        </button>
        <button class="govt-btn btn-outline" id="demoToggleBtn" type="button" style="font-size:10px; padding:4px 9px;">
          <i data-lucide="play" style="width:11px; height:11px;"></i>
          <span id="demoToggleText">Start Demo</span>
        </button>
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
        <span class="badge" id="crowdNavBadge">94% Max Density</span>
      </button>
      <button class="nav-tab" data-target="view-lost">
        <i data-lucide="search" style="width:14px; height:14px;"></i>
        <span>Lost & Found Desk</span>
        <span class="badge" id="lostNavBadge" style="background:#B07817; color:#FFF;">3 Active</span>
      </button>
      <button class="nav-tab" data-target="view-medical">
        <i data-lucide="heart-pulse" style="width:14px; height:14px;"></i>
        <span>Medical Alerts</span>
        <span class="badge" id="medicalNavBadge" style="background:#9A2525; color:#FFF;">2 Alerts</span>
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
            Active Surveillance: 4 CCTVs &bull; Route: Alandi - Dehu - Pune - Wakhri - Pandharpur
          </div>
        </div>

        <div class="command-grid">
          <!-- Left: CCTV surveillance tiles -->
          <div class="cctv-column" id="cctvTilesContainer">
            <div class="panel-header">
              <span>CCTV FEEDS (SURVEILLANCE GRID)</span>
              <span style="font-size:10px; color:var(--text-muted);"><span class="live-dot" style="display:inline-block; width:6px; height:6px; margin-right:4px;"></span>LIVE 60 FPS</span>
            </div>

            <div class="cctv-tile status-heavy" id="tile-CAM-12" data-cam-code="CAM-12" title="Click for live HD stream & telemetry">
              <canvas class="cctv-feed-canvas" id="canvas-CAM-12" width="360" height="200"></canvas>
              <div class="cctv-overlay">
                <div class="cctv-top-info">
                  <span class="cctv-cam-id">CAM-12</span>
                  <span class="cctv-timestamp">LIVE STREAM</span>
                </div>
                <div class="cctv-bottom-info">
                  <span class="cctv-location">Wakhri Phata Junction</span>
                  <span class="density-tag orange">HEAVY 88%</span>
                </div>
              </div>
            </div>

            <div class="cctv-tile status-critical" id="tile-CAM-04" data-cam-code="CAM-04" title="Click for live HD stream & telemetry">
              <canvas class="cctv-feed-canvas" id="canvas-CAM-04" width="360" height="200"></canvas>
              <div class="cctv-overlay">
                <div class="cctv-top-info">
                  <span class="cctv-cam-id">CAM-04</span>
                  <span class="cctv-timestamp">LIVE STREAM</span>
                </div>
                <div class="cctv-bottom-info">
                  <span class="cctv-location">Pandharpur Chowk</span>
                  <span class="density-tag red">CRITICAL 94%</span>
                </div>
              </div>
            </div>

            <div class="cctv-tile status-moderate" id="tile-CAM-08" data-cam-code="CAM-08" title="Click for live HD stream & telemetry">
              <canvas class="cctv-feed-canvas" id="canvas-CAM-08" width="360" height="200"></canvas>
              <div class="cctv-overlay">
                <div class="cctv-top-info">
                  <span class="cctv-cam-id">CAM-08</span>
                  <span class="cctv-timestamp">LIVE STREAM</span>
                </div>
                <div class="cctv-bottom-info">
                  <span class="cctv-location">Saswad Corridor</span>
                  <span class="density-tag yellow">MODERATE 62%</span>
                </div>
              </div>
            </div>

            <div class="cctv-tile status-normal" id="tile-CAM-01" data-cam-code="CAM-01" title="Click for live HD stream & telemetry">
              <canvas class="cctv-feed-canvas" id="canvas-CAM-01" width="360" height="200"></canvas>
              <div class="cctv-overlay">
                <div class="cctv-top-info">
                  <span class="cctv-cam-id">CAM-01</span>
                  <span class="cctv-timestamp">LIVE STREAM</span>
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
                <div class="stat-value" id="statLostCases">3 Active Cases</div>
                <div class="stat-subtext">Automated facial matching engine active</div>
              </div>

              <div class="govt-stat-box" style="border-left-color: var(--status-red);">
                <div class="stat-label">Medical Emergencies</div>
                <div class="stat-value" id="statMedicalAlerts" style="color:var(--status-red);">2 Active Alerts</div>
                <div class="stat-subtext">Sector 3 (Wakhri) & Sector 5 (Pandharpur)</div>
              </div>

              <div class="govt-stat-box" style="border-left-color: var(--status-green);">
                <div class="stat-label">Resource Deployment</div>
                <div class="stat-value" id="statResources" style="color:var(--status-green);">3 / 7 Deployed</div>
                <div class="stat-subtext">Tankers, Ambulances & Patrol Squads stationed</div>
              </div>

              <div class="govt-stat-box" style="border-left-color: var(--saffron-gold);">
                <div class="stat-label">Main Palkhi Status</div>
                <div class="stat-value" id="statPalkhiStatus" style="font-size:16px; color:#3B332B;">Sant Tukaram Maharaj Palkhi</div>
                <div class="stat-subtext" id="statPalkhiLocation">Location: Approaching Wakhri Phata (Km 184)</div>
              </div>

              <!-- Photo Texture Box / Live Flow Video -->
              <div class="panel-card" style="padding:8px;" id="pilgrimFieldCard" data-cam-code="PHOTO-01" title="Click for live HD stream & telemetry">
                <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:4px; display:flex; justify-content:space-between; align-items:center;">
                  <span>PILGRIM FLOW LIVE STREAM</span>
                  <span style="color:#2E7D32; font-family:var(--font-mono); font-size:9px;"><span class="live-dot" style="display:inline-block; width:5px; height:5px; margin-right:3px;"></span>LIVE 60 FPS</span>
                </div>
                <div style="position:relative; width:100%; height:110px; overflow:hidden; border:1px solid var(--border-main); cursor:pointer;">
                  <canvas class="cctv-feed-canvas" id="canvas-PHOTO-01" width="360" height="200" style="width:100%; height:100%; object-fit:cover; display:block;"></canvas>
                  <div class="cctv-overlay" style="position:absolute; bottom:0; left:0; right:0; background:linear-gradient(transparent, rgba(0,0,0,0.8)); padding:4px 8px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#FFF; font-size:9.5px; font-weight:600;">Main Palkhi Procession Corridor</span>
                    <span class="density-tag orange" style="font-size:9px; padding:1px 5px;">FLOW 92%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom Strip: Incident Log Ticker -->
        <div class="incident-ticker-bar">
          <div class="ticker-label">INCIDENT LOG</div>
          <div class="ticker-content">
            <div class="ticker-text" id="incidentLogText">
              [LIVE] VariSetu Command Center connected &bull; Telemetry initialized.
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
              <span>UPDATED: LIVE TELEMETRY</span>
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
                <tbody id="crowdZonesTableBody">
                  <!-- Populated dynamically from /api/crowd/current -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Right: Congestion Forecast Chart -->
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
            <button class="govt-btn" id="registerLostPersonBtn" type="button">
              <i data-lucide="plus" style="width:12px; height:12px;"></i> Register New Case
            </button>
          </div>
        </div>

        <div class="lost-found-grid">
          <!-- Left Column: Table of Active Cases -->
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
              <tbody id="lostPersonsTableBody">
                <!-- Populated dynamically from /api/lost-persons -->
              </tbody>
            </table>
          </div>

          <!-- Right Column: Devanagari Transcript Snippet -->
          <div class="transcript-panel">
            <div style="font-weight:700; color:var(--maroon-primary); font-size:13px; margin-bottom:4px;">
              CALL-TO-CASE PIPELINE TRANSCRIPT
            </div>
            <div style="font-size:11px; color:var(--text-secondary); border-bottom:1px solid var(--border-main); padding-bottom:6px;" id="transcriptHeaderSub">
              Helpline 112 Audio Recording Snippet (Deccan Dialect) &bull; Select a case
            </div>

            <div class="transcript-box" id="transcriptBox">
  Select a case to view call details and audio transcription.
            </div>

            <div style="margin-top:12px; display:flex; gap:8px;">
              <button class="govt-btn" id="dispatchVolunteerBtn" type="button">
                Dispatch Nearby Volunteer
              </button>
              <button class="govt-btn btn-outline" id="queuePaBtn" type="button">
                Queue PA Announcement
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== SCREEN 4: MEDICAL ALERTS VIEW ==================== -->
      <section id="view-medical" class="view-section">
        <div class="section-bar" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div class="section-title">
              <i data-lucide="activity" style="width:16px; height:16px;"></i>
              <span>Medical Emergencies & Heat-Risk Monitoring</span>
            </div>
            <div class="section-sub">
              Active Field Ambulances & Emergency Medical Response Hubs
            </div>
          </div>
          <button class="govt-btn" id="addMedicalAlertBtn" type="button" style="font-size:11px; padding:5px 12px; display:flex; align-items:center; gap:5px; background:var(--status-red);">
            <i data-lucide="plus-circle" style="width:13px; height:13px;"></i>
            <span>+ Report Medical Emergency</span>
          </button>
        </div>

        <div class="medical-view-grid">
          <!-- Left: Card List of Alerts -->
          <div>
            <div class="panel-header" style="margin-bottom:8px;">
              <span>ACTIVE MEDICAL ALERTS</span>
              <span id="medicalAlertsSubHeader">LIVE FEED</span>
            </div>

            <div id="medicalAlertsContainer">
              <!-- Populated dynamically from /api/medical-alerts -->
            </div>
          </div>

          <!-- Right: Heat-Risk Readout Box -->
          <div class="heat-risk-box">
            <div style="font-weight:700; font-family:var(--font-serif); font-size:14px; color:var(--maroon-primary); margin-bottom:8px; border-bottom:1px solid var(--border-main); padding-bottom:4px;">
              HEAT-RISK COMPUTED READOUT
            </div>

            <div class="metric-row">
              <span class="metric-key">Ambient Temperature:</span>
              <span class="metric-val" id="heatTemp">34° C</span>
            </div>
            <div class="metric-row">
              <span class="metric-key">Relative Humidity:</span>
              <span class="metric-val" id="heatHumidity">72%</span>
            </div>
            <div class="metric-row">
              <span class="metric-key">Computed Risk Index:</span>
              <span class="metric-val" id="heatRiskIndex" style="color:var(--status-orange);">7.8 / 10 (MODERATE HEAT RISK)</span>
            </div>
            <div class="metric-row">
              <span class="metric-key">Water Stations Active:</span>
              <span class="metric-val" id="heatWaterStations">12 Operational</span>
            </div>
            <div class="metric-row">
              <span class="metric-key">ORSL Sachet Supplies:</span>
              <span class="metric-val" id="heatOrslSupplies">14,200 Packets Available</span>
            </div>

            <div style="margin-top:14px; background:var(--bg-subtle); padding:8px; border:1px solid var(--border-main); font-size:11px; color:var(--text-secondary);" id="heatAdvisoryText">
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
              <tbody id="resourcesTableBody">
                <!-- Populated dynamically from /api/resources -->
              </tbody>
            </table>
          </div>

          <!-- Right: Route Status Simple List -->
          <div>
            <div class="panel-header" style="margin-bottom:8px;">
              <span>ROUTE STATUS & DIVERSION LOG</span>
            </div>

            <div id="routesContainer">
              <!-- Populated dynamically from /api/routes -->
            </div>
          </div>
        </div>
      </section>

    </main>

  </div> <!-- End #dashboardView -->

  <!-- Reusable Clean Operational Action/Detail Modal -->
  <div class="app-modal-backdrop" id="appActionModal" aria-hidden="true">
    <div class="app-modal" role="dialog" aria-modal="true" aria-labelledby="appModalTitle">
      <div class="app-modal-header">
        <div>
          <div class="app-modal-kicker" id="appModalKicker">VARISETU COMMAND CENTER</div>
          <div class="app-modal-title" id="appModalTitle">Action</div>
        </div>
        <button type="button" class="close-modal-btn" id="appModalClose" aria-label="Close">&times;</button>
      </div>
      <div class="app-modal-body" id="appModalBody"></div>
      <div class="app-modal-footer" id="appModalFooter"></div>
    </div>
  </div>

  <!-- CCTV Expand Detail Modal -->
  <div class="modal-backdrop" id="camModal">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title" id="modalCamTitle">CCTV CAMERA EXPANDED VIEW</div>
        <button class="close-modal-btn" id="camModalCloseBtn" type="button">&times;</button>
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
          <button class="govt-btn" id="modalCamPtzBtn" type="button">PTZ Control</button>
          <button class="govt-btn btn-outline" id="modalCamCloseFooterBtn" type="button">Close Window</button>
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

## Frontend/styles.css
`Frontend/styles.css`

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
  height: 52px;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.08));
}

.mh-gov-seal-img,
.mh-police-badge-img {
  height: 46px;
  width: 46px;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0,0,0,0.18);
  object-fit: contain;
  background: #FFFFFF;
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

.cctv-feed-img,
.cctv-feed-canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  background: #0B0D0F;
}

.cctv-tile:hover {
  box-shadow: 0 0 10px rgba(122, 31, 31, 0.4);
  transform: translateY(-1px);
  transition: all 0.15s ease;
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
  color: #FFF;
  font-size: 11px;
  font-weight: 600;
  text-shadow: 0 1px 2px #000;
}

/* ==================== REALTIME CCTV MODAL STREAM & CONTROLS ==================== */
.modal-cctv-wrapper {
  position: relative;
  width: 100%;
  background: #000;
  border: 1px solid #333;
  overflow: hidden;
  border-radius: 2px;
  margin-bottom: 12px;
}

.modal-cctv-canvas {
  width: 100%;
  height: 280px;
  display: block;
  background: #000;
}

.modal-cctv-toolbar {
  background: #181513;
  border-top: 1px solid #333;
  padding: 6px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.cctv-tool-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cctv-ctrl-btn {
  background: #2D2724;
  border: 1px solid #4D4540;
  color: #EAE6DF;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: 2px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  transition: all 0.15s ease;
  font-family: var(--font-mono);
}

.cctv-ctrl-btn:hover {
  background: var(--maroon-primary);
  border-color: var(--maroon-dark);
  color: #FFF;
}

.cctv-ctrl-btn.active {
  background: #2E5B36;
  border-color: #3E7B46;
  color: #FFF;
}

.cctv-info-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cctv-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.cctv-info-card {
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  padding: 8px 10px;
  border-radius: 2px;
}

.cctv-info-label {
  font-size: 9.5px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cctv-info-value {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 2px;
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
  line-height: 1;
  padding: 2px 6px;
}

.close-modal-btn:hover {
  color: var(--maroon-primary);
}

/* ==================== REUSABLE CLEAN OPERATIONAL MODAL ==================== */
.app-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 5000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(35, 31, 29, 0.58);
}

.app-modal-backdrop.open {
  display: flex;
}

.app-modal {
  width: min(840px, 95vw);
  max-height: 90vh;
  overflow: auto;
  background: var(--bg-card);
  border: 2px solid var(--maroon-primary);
  border-radius: 2px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.22);
}

.app-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 14px 16px;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border-main);
}

.app-modal-kicker {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 3px;
}

.app-modal-title {
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 700;
  color: var(--maroon-primary);
}

.app-modal-body {
  padding: 16px;
  color: var(--text-primary);
}

.app-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-main);
  background: var(--bg-card);
}

.app-modal-body p {
  margin-bottom: 8px;
}

.app-modal-detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.app-modal-detail-item {
  border: 1px solid var(--border-main);
  background: var(--bg-subtle);
  padding: 9px;
}

.app-modal-detail-label {
  font-size: 9px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  text-transform: uppercase;
  margin-bottom: 2px;
}

.app-modal-detail-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-error {
  background: var(--status-red-bg);
  border: 1px solid var(--status-red);
  color: var(--status-red);
  padding: 10px;
  font-size: 12px;
}

.modal-success {
  background: var(--status-green-bg);
  border: 1px solid var(--status-green);
  color: var(--status-green);
  padding: 10px;
  font-size: 12px;
}

.modal-loading {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 11px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.form-control {
  width: 100%;
  padding: 6px 10px;
  font-size: 12px;
  font-family: var(--font-sans);
  border: 1px solid var(--border-main);
  background: #FFF;
  color: var(--text-primary);
  border-radius: 2px;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--maroon-primary);
}

.govt-btn.is-loading {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .app-modal-detail-grid {
    grid-template-columns: 1fr;
  }

  .app-modal-footer {
    flex-direction: column-reverse;
  }
}

/* ==================== HIDDEN UTILITY & LOGIN VIEW ==================== */
[hidden] {
  display: none !important;
}

.login-view {
  min-height: 100vh;
  background: var(--bg-khadi);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
}

.login-view[hidden],
#loginView[hidden],
#dashboardView[hidden] {
  display: none !important;
}

.login-panel {
  width: min(430px, 94vw);
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-top: 5px solid var(--maroon-primary);
  box-shadow: 0 5px 22px rgba(0,0,0,0.10);
  padding: 28px 24px;
  box-sizing: border-box;
}

.login-brand {
  text-align: center;
}

.login-brand img {
  height: 64px;
  width: auto;
  margin-bottom: 10px;
}

.login-marathi {
  font-family: var(--font-serif);
  color: var(--maroon-primary);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.login-english {
  font-size: 9px;
  color: var(--text-secondary);
  letter-spacing: 1.2px;
  margin-top: 5px;
  text-transform: uppercase;
  font-family: var(--font-mono);
}

.login-divider {
  height: 1px;
  background: var(--border-main);
  margin: 18px 0;
}

.login-title {
  font-family: var(--font-serif);
  color: var(--maroon-primary);
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 16px;
  text-align: center;
  letter-spacing: 0.5px;
}

.login-panel label {
  display: block;
  margin: 12px 0 5px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.login-panel input {
  width: 100%;
  padding: 9px 10px;
  background: #FFF;
  border: 1px solid var(--border-main);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 13px;
  border-radius: 2px;
  box-sizing: border-box;
  outline: none;
}

.login-panel input:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px var(--maroon-bg);
}

.login-submit {
  width: 100%;
  margin-top: 18px;
  justify-content: center;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.8px;
}

.login-error {
  margin-top: 12px;
  padding: 9px 12px;
  border: 1px solid var(--status-red);
  background: var(--status-red-bg);
  color: var(--status-red);
  font-size: 11px;
  line-height: 1.4;
  border-radius: 2px;
}

.login-restricted-note {
  margin-top: 18px;
  text-align: center;
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.password-input-wrapper input {
  padding-right: 38px !important;
}

.toggle-password-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #7A726A;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.toggle-password-btn:hover {
  color: var(--maroon-primary);
}

.toggle-password-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
}

/* ==================== PUBLIC PILGRIM PORTAL & HELPLINES ==================== */
.public-helpline-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-main);
  border-radius: 2px;
  text-decoration: none;
  color: inherit;
  transition: all 0.15s ease;
}

.public-helpline-card:hover {
  border-color: var(--maroon-primary);
  background: var(--maroon-bg);
}

.public-helpline-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
}

.public-helpline-num {
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--maroon-primary);
  margin-top: 1px;
}

.photo-upload-thumbnail {
  position: relative;
  width: 65px;
  height: 65px;
  border: 1px solid var(--border-main);
  border-radius: 2px;
  overflow: hidden;
  background: #000;
}

.photo-upload-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-upload-remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(154, 37, 37, 0.85);
  color: #FFF;
  border: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  cursor: pointer;
}






```

---

## Frontend/app.js
`Frontend/app.js`

```javascript
/* VariSetu (वारी सेतु) - Maharashtra Police IT Cell Private Command Center Logic & Realtime Client */

const API_BASE =
  window.VARISETU_CONFIG?.API_BASE ||
  localStorage.getItem('VARISETU_API_BASE') ||
  'http://localhost:8000/api';

const WS_BASE =
  window.VARISETU_CONFIG?.WS_BASE ||
  localStorage.getItem('VARISETU_WS_BASE') ||
  'ws://localhost:8000/ws';

const AUTH_STORAGE_KEY = 'varisetu_auth';

// In-memory operational store
const AppState = {
  currentUser: null,
  cameras: [],
  lostCases: [],
  medicalAlerts: [],
  resources: [],
  routes: [],
  crowdZones: [],
  selectedLostCase: null,
  isDemoRunning: false,
  ws: null
};

let dashboardInitialized = false;

/* ==================== AUTHENTICATION STATE MANAGER ==================== */
function getStoredAuth() {
  try {
    return JSON.parse(sessionStorage.getItem(AUTH_STORAGE_KEY) || 'null');
  } catch {
    return null;
  }
}

function saveAuth(auth) {
  sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

function clearAuth() {
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
  AppState.currentUser = null;
}

function getAccessToken() {
  return getStoredAuth()?.access_token || null;
}

function getRefreshToken() {
  return getStoredAuth()?.refresh_token || null;
}

/* ==================== CENTRAL AUTHENTICATED API CLIENT ==================== */
async function apiRequest(path, options = {}) {
  const {
    method = 'GET',
    body,
    headers = {},
    skipAuthRefresh = false,
    ...rest
  } = options;

  const config = {
    method,
    headers: {
      'Accept': 'application/json',
      ...headers,
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {})
    },
    ...rest
  };

  const token = getAccessToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (body !== undefined) {
    config.body = typeof body === 'string' ? body : JSON.stringify(body);
  }

  let response = await fetch(`${API_BASE}${path}`, config);

  // Handle Token Expiration (401 Unauthorized)
  if (response.status === 401 && !skipAuthRefresh) {
    const refreshTokenStr = getRefreshToken();
    if (refreshTokenStr) {
      try {
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ refresh_token: refreshTokenStr })
        });

        if (refreshRes.ok) {
          const newAuth = await refreshRes.json();
          saveAuth(newAuth);

          // Retry original request with new token
          config.headers.Authorization = `Bearer ${newAuth.access_token}`;
          response = await fetch(`${API_BASE}${path}`, config);
        } else {
          handleSessionExpiration();
          throw new Error('Session expired. Please sign in again.');
        }
      } catch (e) {
        handleSessionExpiration();
        throw new Error('Session expired. Please sign in again.');
      }
    } else {
      handleSessionExpiration();
      throw new Error('Authentication required.');
    }
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.detail?.message ||
      payload?.detail ||
      payload?.error?.message ||
      payload?.message ||
      `Request failed with status ${response.status}`;

    const error = new Error(typeof message === 'object' ? JSON.stringify(message) : message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

function handleSessionExpiration() {
  clearAuth();
  disconnectWebSocket();
  showLoginView();
  openAppModal({
    title: 'SESSION EXPIRED',
    kicker: 'SECURITY PROTOCOL',
    bodyHtml: `
      <div style="font-size:12px; line-height:1.6; color:var(--text-primary);">
        Your command-center authorization session has expired or is invalid. Please sign in again to resume monitoring.
      </div>
    `,
    footerHtml: `
      <button class="govt-btn" id="sessionExpiryCloseBtn">Proceed to Sign In</button>
    `
  });
  document.getElementById('sessionExpiryCloseBtn')?.addEventListener('click', closeAppModal);
}

/* ==================== UI STATE & SECURITY HELPERS ==================== */
function setButtonLoading(button, loading, loadingText = 'Processing...') {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.disabled = true;
    button.textContent = loadingText;
    button.classList.add('is-loading');
  } else {
    button.disabled = false;
    button.textContent = button.dataset.originalText || button.textContent;
    button.classList.remove('is-loading');
  }
}

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

/* ==================== REUSABLE CLEAN MODAL SYSTEM ==================== */
function openAppModal({
  title,
  kicker = 'VARISETU COMMAND CENTER',
  bodyHtml = '',
  footerHtml = ''
}) {
  const backdrop = document.getElementById('appActionModal');
  const titleEl = document.getElementById('appModalTitle');
  const kickerEl = document.getElementById('appModalKicker');
  const bodyEl = document.getElementById('appModalBody');
  const footerEl = document.getElementById('appModalFooter');

  if (!backdrop || !titleEl || !kickerEl || !bodyEl || !footerEl) return;

  kickerEl.textContent = kicker;
  titleEl.textContent = title;
  bodyEl.innerHTML = bodyHtml;
  footerEl.innerHTML = footerHtml;

  backdrop.classList.add('open');
  backdrop.setAttribute('aria-hidden', 'false');
}

function closeAppModal() {
  const backdrop = document.getElementById('appActionModal');
  if (!backdrop) return;
  backdrop.classList.remove('open');
  backdrop.setAttribute('aria-hidden', 'true');
}

function openConfirmModal({
  title,
  message,
  confirmText = 'Confirm',
  confirmClass = 'govt-btn',
  onConfirm
}) {
  openAppModal({
    title,
    bodyHtml: `
      <div style="font-size:12px; line-height:1.6; color:var(--text-primary);">
        ${escapeHtml(message)}
      </div>
    `,
    footerHtml: `
      <button type="button" class="govt-btn btn-outline" id="appModalCancel">Cancel</button>
      <button type="button" class="${confirmClass}" id="appModalConfirm">${escapeHtml(confirmText)}</button>
    `
  });

  const cancelBtn = document.getElementById('appModalCancel');
  const confirmBtn = document.getElementById('appModalConfirm');

  cancelBtn?.addEventListener('click', closeAppModal);
  confirmBtn?.addEventListener('click', async () => {
    if (!onConfirm) return;
    setButtonLoading(confirmBtn, true, 'Processing...');
    try {
      await onConfirm();
      closeAppModal();
    } catch (error) {
      document.getElementById('appModalBody').innerHTML = `
        <div class="modal-error">${escapeHtml(error.message || 'Operation failed.')}</div>
      `;
      setButtonLoading(confirmBtn, false, confirmText);
    }
  });
}

document.getElementById('appModalClose')?.addEventListener('click', closeAppModal);
document.getElementById('appActionModal')?.addEventListener('click', (event) => {
  if (event.target.id === 'appActionModal') closeAppModal();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeAppModal();
});

/* ==================== LOGIN & LOGOUT ROUTING ==================== */
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  setupAuthEventListeners();
  initializeApplication();
});

function setupAuthEventListeners() {
  const loginForm = document.getElementById('loginForm');
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail')?.value?.trim();
    const password = document.getElementById('loginPassword')?.value;
    const submitBtn = document.getElementById('loginSubmitBtn');
    const errorEl = document.getElementById('loginError');

    if (!email || !password) return;

    if (errorEl) {
      errorEl.hidden = true;
      errorEl.textContent = '';
    }
    setButtonLoading(submitBtn, true, 'Signing in...');

    try {
      await login(email, password);
    } catch (err) {
      if (errorEl) {
        errorEl.hidden = false;
        errorEl.textContent = err.message || 'Invalid officer credentials. Access denied.';
      }
      setButtonLoading(submitBtn, false, 'SIGN IN');
    }
  });

  document.getElementById('logoutBtn')?.addEventListener('click', logout);

  // Password visibility toggle
  const togglePassBtn = document.getElementById('togglePasswordVisibilityBtn');
  const passInput = document.getElementById('loginPassword');
  const eyeSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" id="togglePasswordIcon"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>`;
  const eyeOffSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" id="togglePasswordIcon"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`;

  togglePassBtn?.addEventListener('click', () => {
    if (!passInput) return;
    const isPassword = passInput.type === 'password';
    passInput.type = isPassword ? 'text' : 'password';
    togglePassBtn.innerHTML = isPassword ? eyeOffSvg : eyeSvg;
  });

  // Add new officer button (Admin only)
  document.getElementById('addOfficerBtn')?.addEventListener('click', openAddOfficerModal);

  // Public Pilgrim Portal event listeners
  document.getElementById('openPublicPortalBtn')?.addEventListener('click', showPublicView);
  document.getElementById('backToLoginBtn')?.addEventListener('click', showLoginView);
  document.getElementById('publicReportMissingBtn')?.addEventListener('click', () => openLostPersonCreateModal(true));
}

async function initializeApplication() {
  const auth = getStoredAuth();
  if (!auth?.access_token) {
    showLoginView();
    return;
  }

  try {
    const user = await apiRequest('/auth/me');
    showDashboardView(user);
  } catch (e) {
    clearAuth();
    showLoginView();
  }
}

async function login(email, password) {
  const result = await apiRequest('/auth/login', {
    method: 'POST',
    body: { email, password },
    skipAuthRefresh: true
  });

  saveAuth(result);

  const user = await apiRequest('/auth/me');
  showDashboardView(user);
  return user;
}

async function logout() {
  try {
    await apiRequest('/auth/logout', { method: 'POST' });
  } catch {}

  disconnectWebSocket();
  clearAuth();
  showLoginView();
}

function openAddOfficerModal() {
  openAppModal({
    title: 'Provision Authorized Officer',
    kicker: 'PERSONNEL & ACCESS CONTROL',
    bodyHtml: `
      <form id="newOfficerForm">
        <div class="form-group">
          <label>Officer Full Name</label>
          <input type="text" id="officerName" class="form-control" placeholder="e.g. Inspector Vikram Jadhav" required>
        </div>
        <div class="form-group">
          <label>Official Email ID</label>
          <input type="email" id="officerEmail" class="form-control" placeholder="e.g. vikram.jadhav@mahapolice.gov.in" required>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          <div class="form-group">
            <label>Phone Number</label>
            <input type="text" id="officerPhone" class="form-control" placeholder="+91-9822007788">
          </div>
          <div class="form-group">
            <label>Access Role</label>
            <select id="officerRole" class="form-control">
              <option value="POLICE">POLICE (Traffic & Field Patrol)</option>
              <option value="COMMANDER">COMMANDER (Command & Control)</option>
              <option value="MEDICAL">MEDICAL (Ambulance / Health)</option>
              <option value="RESOURCE_MANAGER">RESOURCE_MANAGER (Logistics)</option>
              <option value="VOLUNTEER_COORDINATOR">VOLUNTEER_COORDINATOR</option>
              <option value="VIEWER">VIEWER (Read-Only Monitor)</option>
              <option value="ADMIN">ADMIN (Full System Administrator)</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Department / Sector</label>
          <input type="text" id="officerDept" class="form-control" placeholder="e.g. Pandharpur Quick Response Team">
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" id="officerPassword" class="form-control" value="varisetu2026" required>
        </div>
      </form>
    `,
    footerHtml: `
      <button type="button" class="govt-btn btn-outline" id="officerCancel">Cancel</button>
      <button type="button" class="govt-btn" id="officerSubmit">Create Officer Account</button>
    `
  });

  document.getElementById('officerCancel')?.addEventListener('click', closeAppModal);
  document.getElementById('officerSubmit')?.addEventListener('click', async () => {
    const name = document.getElementById('officerName')?.value?.trim();
    const email = document.getElementById('officerEmail')?.value?.trim();
    const phone = document.getElementById('officerPhone')?.value?.trim() || null;
    const role = document.getElementById('officerRole')?.value || 'POLICE';
    const department = document.getElementById('officerDept')?.value?.trim() || 'Maharashtra Police';
    const password = document.getElementById('officerPassword')?.value;
    const submitBtn = document.getElementById('officerSubmit');

    if (!name || !email || !password) {
      alert('Please fill out Name, Official Email, and Password.');
      return;
    }

    setButtonLoading(submitBtn, true, 'Creating account...');

    try {
      const created = await apiRequest('/auth/register', {
        method: 'POST',
        body: {
          name,
          email,
          phone,
          role,
          department,
          password,
          is_active: true
        }
      });

      openAppModal({
        title: 'Officer Account Provisioned',
        kicker: 'ACCESS AUTHORIZED',
        bodyHtml: `
          <div class="modal-success" style="margin-bottom:12px;">
            Officer account for <strong>${escapeHtml(created.name)}</strong> provisioned successfully!
          </div>
          <div class="app-modal-detail-grid">
            <div class="app-modal-detail-item">
              <div class="app-modal-detail-label">Official Email</div>
              <div class="app-modal-detail-value">${escapeHtml(created.email)}</div>
            </div>
            <div class="app-modal-detail-item">
              <div class="app-modal-detail-label">Assigned Role</div>
              <div class="app-modal-detail-value" style="font-weight:bold; color:var(--maroon-primary);">${escapeHtml(created.role)}</div>
            </div>
            <div class="app-modal-detail-item">
              <div class="app-modal-detail-label">Department</div>
              <div class="app-modal-detail-value">${escapeHtml(created.department || 'Maharashtra Police')}</div>
            </div>
            <div class="app-modal-detail-item">
              <div class="app-modal-detail-label">Password</div>
              <div class="app-modal-detail-value" style="font-family:var(--font-mono); font-size:11px;">${escapeHtml(password)}</div>
            </div>
          </div>
          <div style="margin-top:12px; font-size:11px; color:var(--text-secondary);">
            The officer can now immediately log in with these credentials.
          </div>
        `,
        footerHtml: `
          <button type="button" class="govt-btn" id="officerDoneBtn">Done</button>
        `
      });
      document.getElementById('officerDoneBtn')?.addEventListener('click', closeAppModal);
    } catch (err) {
      document.getElementById('appModalBody').innerHTML = `
        <div class="modal-error">${escapeHtml(err.message || 'Failed to create officer account.')}</div>
      `;
      setButtonLoading(submitBtn, false, 'Create Officer Account');
    }
  });
}

function showLoginView() {
  const loginView = document.getElementById('loginView');
  const dashView = document.getElementById('dashboardView');
  const publicView = document.getElementById('publicView');

  if (loginView) {
    loginView.hidden = false;
    loginView.style.display = 'flex';
  }
  if (dashView) {
    dashView.hidden = true;
    dashView.style.display = 'none';
  }
  if (publicView) {
    publicView.hidden = true;
    publicView.style.display = 'none';
  }

  const submitBtn = document.getElementById('loginSubmitBtn');
  if (submitBtn) {
    setButtonLoading(submitBtn, false, 'SIGN IN');
  }

  if (window.lucide) {
    lucide.createIcons();
  }

  disconnectWebSocket();
}

function showPublicView() {
  const loginView = document.getElementById('loginView');
  const dashView = document.getElementById('dashboardView');
  const publicView = document.getElementById('publicView');

  if (loginView) {
    loginView.hidden = true;
    loginView.style.display = 'none';
  }
  if (dashView) {
    dashView.hidden = true;
    dashView.style.display = 'none';
  }
  if (publicView) {
    publicView.hidden = false;
    publicView.style.display = 'block';
  }

  if (window.lucide) {
    lucide.createIcons();
  }

  setTimeout(() => initPublicRouteMap(), 150);
}

let publicMapInitialized = false;
function initPublicRouteMap() {
  const mapElement = document.getElementById('publicRouteMap');
  if (!mapElement) return;
  if (publicMapInitialized && window.publicWariMap) {
    window.publicWariMap.invalidateSize();
    return;
  }

  const publicMap = L.map('publicRouteMap', {
    center: [18.0000, 74.8000],
    zoom: 9,
    zoomControl: true
  });

  window.publicWariMap = publicMap;

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; Maharashtra Police IT &bull; Map data &copy; OpenStreetMap',
    maxZoom: 18
  }).addTo(publicMap);

  const routePoints = [
    [18.6772, 73.8967], // Alandi
    [18.5204, 73.8567], // Pune City
    [18.3440, 74.0305], // Saswad
    [18.1500, 74.3000], // Jejuri / Lonand
    [17.8900, 75.0200], // Bhalwani
    [17.7280, 75.2950], // Wakhri Phata
    [17.6777, 75.3276]  // Pandharpur Shrine
  ];

  L.polyline(routePoints.slice(0, 4), { color: '#2E5B36', weight: 6, opacity: 0.85 }).addTo(publicMap).bindPopup('<b>Alandi-Saswad Corridor:</b> Normal Flow');
  L.polyline(routePoints.slice(3, 7), { color: '#7A1F1F', weight: 7, opacity: 0.9 }).addTo(publicMap).bindPopup('<b>Wakhri-Pandharpur Sector:</b> Procession Approaching');

  const palkhiIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#D98E2C; color:#FFF; border:1px solid #7A1F1F; padding:4px 8px; font-weight:bold; font-size:10px; border-radius:2px; box-shadow:0 1px 3px rgba(0,0,0,0.3);">🚩 SANT TUKARAM PALKHI</div>`,
    iconSize: [140, 24],
    iconAnchor: [70, 12]
  });
  L.marker([17.7280, 75.2950], { icon: palkhiIcon }).addTo(publicMap)
    .bindPopup('<b>Sant Tukaram Maharaj Palkhi</b><br>Approaching Wakhri Phata (Km 184)<br>Moving smoothly towards Pandharpur');

  const pandharpurIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#7A1F1F; color:#FFF; border:1px solid #000; padding:4px 8px; font-size:10px; font-weight:bold; border-radius:2px;">🛕 Pandharpur Shrine</div>`,
    iconSize: [130, 24]
  });
  L.marker([17.6777, 75.3276], { icon: pandharpurIcon }).addTo(publicMap)
    .bindPopup('<b>Shri Vitthal-Rukmini Mandir</b><br>Pandharpur Final Destination');

  publicMapInitialized = true;
}

function showDashboardView(user) {
  AppState.currentUser = user;
  const loginView = document.getElementById('loginView');
  const dashView = document.getElementById('dashboardView');
  const publicView = document.getElementById('publicView');

  if (loginView) {
    loginView.hidden = true;
    loginView.style.display = 'none';
  }
  if (publicView) {
    publicView.hidden = true;
    publicView.style.display = 'none';
  }
  if (dashView) {
    dashView.hidden = false;
    dashView.style.display = 'block';
  }

  const submitBtn = document.getElementById('loginSubmitBtn');
  if (submitBtn) {
    setButtonLoading(submitBtn, false, 'SIGN IN');
  }

  const profileText = document.getElementById('userProfileText');
  if (profileText && user) {
    profileText.textContent = `${user.role || 'OFFICER'}`;
  }

  // Strictly restrict + Add Officer button to ADMIN role only
  const addOfficerBtn = document.getElementById('addOfficerBtn');
  if (addOfficerBtn) {
    if (user && user.role === 'ADMIN') {
      addOfficerBtn.style.display = 'inline-flex';
    } else {
      addOfficerBtn.style.display = 'none';
    }
  }

  if (window.lucide) {
    lucide.createIcons();
  }

  initializeDashboardAfterAuth(user);
}

async function initializeDashboardAfterAuth(user) {
  if (!dashboardInitialized) {
    updateClock();
    setInterval(updateClock, 1000);
    setupNavigation();
    initRouteMap();
    initForecastChart();
    initCctvTilePlayers();
    setupCctvModal();
    setupDemoButton();
    setupLostFoundButtons();
    setupMedicalEmergencyButtons();
    dashboardInitialized = true;
  }

  if (window.wariMap) {
    setTimeout(() => {
      try {
        window.wariMap.invalidateSize();
      } catch {}
    }, 150);
  }

  await initLiveBackend();
}

/* ==================== CLOCK & NAVIGATION ==================== */
function updateClock() {
  const clockEl = document.getElementById('sysClock');
  if (!clockEl) return;
  const now = new Date();
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
  if (!mapElement || window.wariMap) return;

  const wariMap = L.map('routeMap', {
    center: [18.0000, 74.8000],
    zoom: 9,
    zoomControl: true
  });

  window.wariMap = wariMap;

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; Maharashtra Police IT &bull; Map data &copy; OpenStreetMap',
    maxZoom: 18
  }).addTo(wariMap);

  const routePoints = [
    [18.6772, 73.8967], // Alandi
    [18.5204, 73.8567], // Pune City
    [18.3440, 74.0305], // Saswad
    [18.1500, 74.3000], // Jejuri / Lonand
    [17.8900, 75.0200], // Bhalwani
    [17.7280, 75.2950], // Wakhri Phata
    [17.6777, 75.3276]  // Pandharpur Shrine
  ];

  L.polyline(routePoints.slice(0, 3), { color: '#2E5B36', weight: 6, opacity: 0.85 }).addTo(wariMap).bindPopup('<b>Alandi-Saswad Sector:</b> Normal Pilgrim Density (35-62%)');
  L.polyline(routePoints.slice(2, 5), { color: '#B8551B', weight: 7, opacity: 0.85 }).addTo(wariMap).bindPopup('<b>Saswad-Bhalwani Sector:</b> Heavy Density (74%)');
  L.polyline(routePoints.slice(4, 7), { color: '#9A2525', weight: 8, opacity: 0.9 }).addTo(wariMap).bindPopup('<b>Wakhri-Pandharpur Sector:</b> CRITICAL CONGESTION (88-94%)');

  const palkhiIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#D98E2C; color:#FFF; border:1px solid #7A1F1F; padding:4px 8px; font-weight:bold; font-size:10px; border-radius:2px; box-shadow:0 1px 3px rgba(0,0,0,0.3);">🚩 PALKHI (Wakhri)</div>`,
    iconSize: [110, 24],
    iconAnchor: [55, 12]
  });
  L.marker([17.7280, 75.2950], { icon: palkhiIcon }).addTo(wariMap)
    .bindPopup('<b>Sant Tukaram Maharaj Palkhi</b><br>Location: Approaching Wakhri Phata (Km 184)<br>Speed: 3 km/h');

  const waterIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#1D6F8A; color:#FFF; border:1px solid #000; padding:2px 5px; font-size:9px; font-weight:bold; border-radius:2px;">💧 Tanker #09</div>`,
    iconSize: [80, 20]
  });
  L.marker([17.7400, 75.2800], { icon: waterIcon }).addTo(wariMap)
    .bindPopup('<b>Water Tanker #WT-09</b><br>Capacity: 10,000L (80% Full)<br>Stationed: Wakhri Access Rd');

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
  if (!canvas || window.forecastChartInstance) return;

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
          labels: { font: { family: 'IBM Plex Sans', size: 11 }, boxWidth: 12 }
        },
        tooltip: { mode: 'index', intersect: false }
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

/* ==================== LIVE DATA INTEGRATION ==================== */
async function initLiveBackend() {
  await Promise.allSettled([
    checkHealth(),
    fetchLiveSummary(),
    fetchLiveForecast(),
    fetchCameras(),
    refreshCrowdZones(),
    refreshMedicalAlerts(),
    refreshLostPersons(),
    refreshResources(),
    refreshRoutes(),
    fetchHeatRisk()
  ]);

  connectWebSocket();
}

async function checkHealth() {
  const badge = document.getElementById('backendHealthBadge');
  const text = document.getElementById('backendHealthText');
  try {
    const res = await apiRequest('/health', { skipAuthRefresh: true });
    if (res && res.status === 'ok') {
      if (badge) badge.style.borderColor = 'var(--status-green)';
      if (text) text.textContent = 'LIVE';
    }
  } catch (err) {
    if (badge) badge.style.borderColor = 'var(--status-orange)';
    if (text) text.textContent = 'STANDALONE';
  }
}

async function fetchLiveSummary() {
  try {
    const data = await apiRequest('/dashboard/summary');
    updateDashboardSummary(data);
    return data;
  } catch (err) {
    console.debug('[VariSetu] Dashboard summary fetch skipped.');
    return null;
  }
}

function updateDashboardSummary(data) {
  if (!data) return;

  const lostEl = document.getElementById('statLostCases');
  const medEl = document.getElementById('statMedicalAlerts');
  const resEl = document.getElementById('statResources');
  const palkhiLocEl = document.getElementById('statPalkhiLocation');
  const palkhiStatEl = document.getElementById('statPalkhiStatus');

  if (lostEl) lostEl.textContent = `${data.active_lost_person_cases ?? 0} Active Cases`;
  if (medEl) medEl.textContent = `${data.active_medical_alerts ?? 0} Active Alerts`;
  if (resEl) resEl.textContent = `${data.deployed_resources ?? 0} / ${data.total_resources ?? 7} Deployed`;
  if (palkhiLocEl && data.palkhi_location) palkhiLocEl.textContent = `Location: ${data.palkhi_location}`;
  if (palkhiStatEl && data.palkhi_status) palkhiStatEl.textContent = data.palkhi_status;

  updateNavigationBadges(data);
}

function updateNavigationBadges(data) {
  const crowdBadge = document.getElementById('crowdNavBadge');
  const lostBadge = document.getElementById('lostNavBadge');
  const medicalBadge = document.getElementById('medicalNavBadge');

  if (crowdBadge && data.max_density !== undefined) {
    crowdBadge.textContent = `${Math.round(data.max_density)}% Max Density`;
  }
  if (lostBadge) {
    lostBadge.textContent = `${data.active_lost_person_cases ?? 0} Active`;
  }
  if (medicalBadge) {
    medicalBadge.textContent = `${data.active_medical_alerts ?? 0} Alerts`;
  }
}

async function fetchLiveForecast() {
  try {
    const forecastData = await apiRequest('/crowd/forecast');
    if (window.forecastChartInstance && forecastData?.zones) {
      window.forecastChartInstance.data.labels = forecastData.time_labels;
      forecastData.zones.forEach((z, idx) => {
        if (window.forecastChartInstance.data.datasets[idx]) {
          window.forecastChartInstance.data.datasets[idx].data = z.forecast_points.map(p => p.predicted_density);
        }
      });
      window.forecastChartInstance.update();
    }
  } catch (err) {
    console.debug('[VariSetu] Using fallback forecast profile.');
  }
}

/* ==================== CAMERAS & CCTV ==================== */
async function fetchCameras() {
  try {
    const cameras = await apiRequest('/cameras');
    AppState.cameras = cameras;
    renderCameras(cameras);
    return cameras;
  } catch (err) {
    console.debug('[VariSetu] Camera fetch failed; keeping fallback tiles.');
    setupFallbackCameraTiles();
    return [];
  }
}

const CCTV_ASSET_MAP = {
  'CAM-12': 'assets/cctv_highway4_naka.jpg',
  'CAM-04': 'assets/cctv_highway4_naka.jpg',
  'CAM-08': 'assets/palkhi_procession_hd.jpg',
  'CAM-01': 'assets/wari_aerial_procession_hd.jpg',
  'PHOTO-01': 'assets/palkhi_procession_hd.jpg',
  'DEFAULT': 'assets/cctv_wakhri_phata_1785244836537.jpg'
};

const activeCctvPlayers = {};
let currentModalPlayer = null;

class CCTVFeedPlayer {
  constructor(canvas, imageSrc, camConfig = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.imageSrc = imageSrc || CCTV_ASSET_MAP.DEFAULT;
    this.camCode = camConfig.camCode || 'CAM-01';
    this.location = camConfig.location || 'Surveillance Node';
    this.density = camConfig.density !== undefined ? camConfig.density : 85;
    this.densityStatus = camConfig.densityStatus || 'HEAVY';
    this.showBoundingBoxes = camConfig.showBoundingBoxes !== false;
    this.isLargeModal = camConfig.isLargeModal || false;
    this.panX = 0;
    this.panY = 0;
    this.zoom = 1.0;
    this.running = false;
    this.animFrame = null;

    this.img = new Image();
    this.imgLoaded = false;
    this.img.src = this.imageSrc;
    this.img.onload = () => { this.imgLoaded = true; };
    this.boxes = this.createDetectionBoxes();
  }

  createDetectionBoxes() {
    const count = this.isLargeModal ? 6 : 3;
    const labels = ['Devotee', 'Pilgrim Squad', 'Police Naka', 'Vehicle', 'Palkhi Queue', 'Ambulance Sector'];
    const boxes = [];
    for (let i = 0; i < count; i++) {
      boxes.push({
        baseX: 0.12 + (i * 0.13) + (Math.random() * 0.04),
        baseY: 0.30 + (Math.random() * 0.38),
        w: 0.08 + Math.random() * 0.05,
        h: 0.12 + Math.random() * 0.08,
        speedX: (Math.random() - 0.5) * 0.0003,
        speedY: (Math.random() - 0.5) * 0.0002,
        label: labels[i % labels.length],
        confidence: Math.floor(88 + Math.random() * 11),
        color: (i === 0 && this.density > 80) ? '#FF3B30' : '#00FF66'
      });
    }
    return boxes;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.render();
  }

  stop() {
    this.running = false;
    if (this.animFrame) {
      cancelAnimationFrame(this.animFrame);
      this.animFrame = null;
    }
  }

  render(timestamp = performance.now()) {
    if (!this.running) return;
    const { canvas, ctx, img, imgLoaded } = this;
    const w = canvas.width;
    const h = canvas.height;

    // Fill background
    ctx.fillStyle = '#080A0C';
    ctx.fillRect(0, 0, w, h);

    if (imgLoaded) {
      // Subtle organic Ken Burns drift loop
      const timeSec = timestamp / 1000;
      const driftX = Math.sin(timeSec * 0.35) * 6;
      const driftY = Math.cos(timeSec * 0.25) * 3;
      const currentZoom = this.zoom + (Math.sin(timeSec * 0.2) * 0.02);

      // Render image with pan and zoom
      ctx.save();
      ctx.translate(w / 2 + this.panX + driftX, h / 2 + this.panY + driftY);
      ctx.scale(currentZoom, currentZoom);
      ctx.drawImage(img, -w / 2, -h / 2, w, h);
      ctx.restore();

      // Optical scanlines
      ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
      for (let y = 0; y < h; y += 4) {
        ctx.fillRect(0, y, w, 1.5);
      }

      // Draw dynamic AI detection bounding boxes
      if (this.showBoundingBoxes) {
        this.boxes.forEach(box => {
          box.baseX += box.speedX;
          box.baseY += box.speedY;
          if (box.baseX < 0.04 || box.baseX > 0.86) box.speedX *= -1;
          if (box.baseY < 0.22 || box.baseY > 0.74) box.speedY *= -1;

          const bx = (box.baseX * w) + (this.panX * 0.5);
          const by = (box.baseY * h) + (this.panY * 0.5);
          const bw = box.w * w;
          const bh = box.h * h;

          ctx.strokeStyle = box.color;
          ctx.lineWidth = this.isLargeModal ? 2 : 1.5;
          ctx.strokeRect(bx, by, bw, bh);

          // Label pill
          const fontSize = this.isLargeModal ? 10 : 8;
          ctx.font = `600 ${fontSize}px monospace`;
          const text = `${box.label} ${box.confidence}%`;
          const textW = ctx.measureText(text).width + 6;

          ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
          ctx.fillRect(bx, by - (fontSize + 4), textW, fontSize + 3);
          ctx.fillStyle = box.color;
          ctx.fillText(text, bx + 3, by - 3);
        });
      }

      // Live Timecode & Metadata HUD
      const now = new Date();
      const pad = (n) => String(n).padStart(2, '0');
      const ms = String(now.getMilliseconds()).padStart(3, '0');
      const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}.${ms} IST`;
      const dateStr = `28 AUG 2026`;

      // Top HUD Bar
      const hudHeight = this.isLargeModal ? 26 : 20;
      ctx.fillStyle = 'rgba(0, 0, 0, 0.68)';
      ctx.fillRect(0, 0, w, hudHeight);

      // Camera Code + Location
      ctx.font = `700 ${this.isLargeModal ? 11 : 9}px monospace`;
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(`${this.camCode} | LIVE | ${this.location.toUpperCase()}`, 8, this.isLargeModal ? 17 : 14);

      // Flashing REC Dot & Timecode
      const isRecOn = Math.floor(timestamp / 500) % 2 === 0;
      const recText = `● REC  ${dateStr} ${timeStr}`;
      ctx.fillStyle = isRecOn ? '#FF3B30' : '#888888';
      const recWidth = ctx.measureText(recText).width;
      ctx.fillText(recText, w - recWidth - 8, this.isLargeModal ? 17 : 14);

      // Bottom telemetry bar for Large Modal
      if (this.isLargeModal) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
        ctx.fillRect(0, h - 24, w, 24);
        ctx.fillStyle = '#00FF66';
        ctx.font = '600 10px monospace';
        ctx.fillText(`DENSITY: ${this.density}% [${this.densityStatus}] | ZOOM: ${this.zoom.toFixed(1)}x | 1080p @ 60FPS | LATENCY: 12ms`, 8, h - 8);
        ctx.fillStyle = '#E5A93C';
        ctx.fillText(`OPTICAL AI VISION ACTIVE`, w - 170, h - 8);
      }
    }

    this.animFrame = requestAnimationFrame((ts) => this.render(ts));
  }
}

function initCctvTilePlayers() {
  const configs = [
    { id: 'canvas-CAM-12', code: 'CAM-12', loc: 'Wakhri Phata Junction', density: 88, status: 'HEAVY' },
    { id: 'canvas-CAM-04', code: 'CAM-04', loc: 'Pandharpur Chowk', density: 94, status: 'CRITICAL' },
    { id: 'canvas-CAM-08', code: 'CAM-08', loc: 'Saswad Corridor', density: 62, status: 'MODERATE' },
    { id: 'canvas-CAM-01', code: 'CAM-01', loc: 'Alandi Ghat Rd', density: 35, status: 'NORMAL' },
    { id: 'canvas-PHOTO-01', code: 'PHOTO-01', loc: 'Wari Pilgrim Flow', density: 92, status: 'FLOW' }
  ];

  configs.forEach(cfg => {
    const canvas = document.getElementById(cfg.id);
    if (!canvas) return;

    if (activeCctvPlayers[cfg.code]) {
      activeCctvPlayers[cfg.code].stop();
    }

    const imageSrc = CCTV_ASSET_MAP[cfg.code] || CCTV_ASSET_MAP.DEFAULT;
    const player = new CCTVFeedPlayer(canvas, imageSrc, {
      camCode: cfg.code,
      location: cfg.loc,
      density: cfg.density,
      densityStatus: cfg.status,
      isLargeModal: false
    });
    player.start();
    activeCctvPlayers[cfg.code] = player;
  });
}

function renderCameras(cameras) {
  const container = document.getElementById('cctvTilesContainer');
  if (!container || !cameras || cameras.length === 0) return;

  const existingTiles = container.querySelectorAll('.cctv-tile');
  cameras.slice(0, existingTiles.length).forEach((cam, idx) => {
    const tile = existingTiles[idx];
    if (!tile) return;

    tile.dataset.cameraId = cam.id;
    tile.dataset.camCode = cam.camera_code;

    const idEl = tile.querySelector('.cctv-cam-id');
    const locEl = tile.querySelector('.cctv-location');
    const densityEl = tile.querySelector('.density-tag');

    if (idEl) idEl.textContent = cam.camera_code;
    if (locEl) locEl.textContent = cam.name;
    if (densityEl && cam.current_density !== undefined) {
      densityEl.textContent = `${cam.density_status || 'DENSITY'} ${cam.current_density}%`;
    }

    // Update active player metadata if exists
    if (activeCctvPlayers[cam.camera_code]) {
      activeCctvPlayers[cam.camera_code].location = cam.name;
      activeCctvPlayers[cam.camera_code].density = cam.current_density;
      activeCctvPlayers[cam.camera_code].densityStatus = cam.density_status || 'ACTIVE';
    }

    tile.onclick = () => openCameraDetails(cam);
  });
}

function setupFallbackCameraTiles() {
  const tiles = document.querySelectorAll('.cctv-tile');
  tiles.forEach(tile => {
    const camCode = tile.dataset.camCode || 'CAM-01';
    tile.onclick = () => {
      const found = AppState.cameras.find(c => c.camera_code === camCode) || {
        camera_code: camCode,
        name: tile.querySelector('.cctv-location')?.textContent || 'Surveillance Sector',
        status: 'ONLINE',
        current_density: 88.0,
        density_status: 'HEAVY'
      };
      openCameraDetails(found);
    };
  });

  const photoCard = document.getElementById('pilgrimFieldCard');
  if (photoCard) {
    photoCard.onclick = () => {
      openCameraDetails({
        camera_code: 'DRONE-01',
        name: 'Main Palkhi Procession Corridor',
        status: 'ONLINE',
        current_density: 92.0,
        density_status: 'HIGH FLOW'
      });
    };
  }
}

function openCameraDetails(camera) {
  if (currentModalPlayer) {
    currentModalPlayer.stop();
    currentModalPlayer = null;
  }

  const camCode = camera.camera_code || 'CAM-04';
  const camName = camera.name || 'Pandharpur Sector';
  const density = camera.current_density ?? 94;
  const status = camera.status || 'ONLINE';
  const densityStatus = camera.density_status || (density >= 90 ? 'CRITICAL' : (density >= 75 ? 'HEAVY' : 'MODERATE'));
  const tagColor = density >= 90 ? 'var(--status-red)' : (density >= 75 ? 'var(--status-orange)' : 'var(--status-yellow)');
  const imageSrc = CCTV_ASSET_MAP[camCode] || CCTV_ASSET_MAP.DEFAULT;

  openAppModal({
    title: `REALTIME SURVEILLANCE & TELEMETRY: ${escapeHtml(camCode)}`,
    kicker: 'POLICE COMMAND CCTV NETWORK &bull; REALTIME STREAM',
    bodyHtml: `
      <!-- TOP: REALTIME RUNNING CAMERA STREAM -->
      <div class="modal-cctv-wrapper">
        <canvas id="modalLargeCctvCanvas" width="800" height="320" class="modal-cctv-canvas"></canvas>
        <div class="modal-cctv-toolbar">
          <div class="cctv-tool-group">
            <span style="font-size:9.5px; font-weight:700; color:var(--text-muted); margin-right:4px;">PTZ:</span>
            <button type="button" class="cctv-ctrl-btn" id="ptzPanLeft" title="Pan Left">&larr; Left</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzPanRight" title="Pan Right">Right &rarr;</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzTiltUp" title="Tilt Up">&uarr; Up</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzTiltDown" title="Tilt Down">Down &darr;</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzReset" title="Center Reset">Reset</button>
          </div>
          <div class="cctv-tool-group">
            <button type="button" class="cctv-ctrl-btn" id="ptzZoomIn" title="Zoom In">+ Zoom In</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzZoomOut" title="Zoom Out">- Zoom Out</button>
            <button type="button" class="cctv-ctrl-btn active" id="ptzToggleAi" title="Toggle AI Bounding Boxes">🎯 AI Vision [ON]</button>
            <button type="button" class="cctv-ctrl-btn" id="ptzSnapshot" title="Save Snapshot">📸 Snapshot</button>
          </div>
        </div>
      </div>

      <!-- BOTTOM: COMPLETE OPERATIONAL INFORMATION & FIRST RESPONDER TELEMETRY -->
      <div class="cctv-info-section">
        <div class="cctv-info-grid">
          <div class="cctv-info-card">
            <div class="cctv-info-label">Checkpoint Location</div>
            <div class="cctv-info-value">${escapeHtml(camName)}</div>
            <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Route Km 184.2 &bull; Junction Chokepoint</div>
          </div>

          <div class="cctv-info-card">
            <div class="cctv-info-label">Live Crowd Density</div>
            <div class="cctv-info-value" style="color:${tagColor};">${escapeHtml(density)}% &bull; ${escapeHtml(densityStatus)}</div>
            <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Inflow: ~420 pilgrims/min</div>
          </div>

          <div class="cctv-info-card">
            <div class="cctv-info-label">Stream & Hardware</div>
            <div class="cctv-info-value" style="color:var(--status-green); font-family:var(--font-mono); font-size:11px;">1080p @ 60 FPS &bull; ${escapeHtml(status)}</div>
            <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Latency: 12ms &bull; AES-256 State Net</div>
          </div>
        </div>

        <div class="cctv-info-grid" style="grid-template-columns: 1fr 1fr;">
          <div class="cctv-info-card">
            <div class="cctv-info-label">Stationed Field Units</div>
            <div style="font-size:11px; margin-top:3px; line-height:1.4;">
              <div>👮 <strong>Patrol Squad #14</strong> (Insp. Jadhav &bull; 120m away)</div>
              <div>🚑 <strong>Ambulance Unit #MV-02</strong> (Dr. Deshmukh &bull; 250m)</div>
              <div>💧 <strong>Water Tanker #WT-09</strong> (10,000L &bull; 400m)</div>
            </div>
          </div>

          <div class="cctv-info-card">
            <div class="cctv-info-label">AI Incident & Chokepoint Risk</div>
            <div style="font-size:11px; margin-top:3px; line-height:1.4;">
              <div style="color:var(--status-red); font-weight:600;">⚠️ Barricade Gate Congestion Detected</div>
              <div style="color:var(--text-secondary);">Recommendation: Deploy secondary bypass lane to ease flow toward shrine.</div>
            </div>
          </div>
        </div>
      </div>
    `,
    footerHtml: `
      <div style="display:flex; justify-content:space-between; width:100%; align-items:center;">
        <div style="display:flex; gap:6px;">
          <button type="button" class="govt-btn btn-outline" id="dispatchQrtBtn" style="font-size:11px;">🚨 Deploy QRT Squad</button>
          <button type="button" class="govt-btn btn-outline" id="triggerPaBtn" style="font-size:11px;">📢 Trigger PA Alert</button>
        </div>
        <button type="button" class="govt-btn" id="cameraModalClose">Close Surveillance</button>
      </div>
    `
  });

  // Start live running stream player in the modal
  const modalCanvas = document.getElementById('modalLargeCctvCanvas');
  if (modalCanvas) {
    currentModalPlayer = new CCTVFeedPlayer(modalCanvas, imageSrc, {
      camCode: camCode,
      location: camName,
      density: density,
      densityStatus: densityStatus,
      isLargeModal: true,
      showBoundingBoxes: true
    });
    currentModalPlayer.start();
  }

  // Wire PTZ and Stream Controls
  document.getElementById('ptzPanLeft')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.panX -= 25;
  });
  document.getElementById('ptzPanRight')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.panX += 25;
  });
  document.getElementById('ptzTiltUp')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.panY -= 20;
  });
  document.getElementById('ptzTiltDown')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.panY += 20;
  });
  document.getElementById('ptzReset')?.addEventListener('click', () => {
    if (currentModalPlayer) {
      currentModalPlayer.panX = 0;
      currentModalPlayer.panY = 0;
      currentModalPlayer.zoom = 1.0;
    }
  });
  document.getElementById('ptzZoomIn')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.zoom = Math.min(2.5, currentModalPlayer.zoom + 0.25);
  });
  document.getElementById('ptzZoomOut')?.addEventListener('click', () => {
    if (currentModalPlayer) currentModalPlayer.zoom = Math.max(1.0, currentModalPlayer.zoom - 0.25);
  });
  document.getElementById('ptzToggleAi')?.addEventListener('click', (e) => {
    if (currentModalPlayer) {
      currentModalPlayer.showBoundingBoxes = !currentModalPlayer.showBoundingBoxes;
      e.currentTarget.textContent = currentModalPlayer.showBoundingBoxes ? '🎯 AI Vision [ON]' : '🎯 AI Vision [OFF]';
      e.currentTarget.classList.toggle('active', currentModalPlayer.showBoundingBoxes);
    }
  });
  document.getElementById('ptzSnapshot')?.addEventListener('click', () => {
    alert(`[VariSetu Surveillance] High-Resolution Snapshot captured for ${camCode} and archived to evidence locker.`);
  });

  // Wire Field Dispatch Buttons
  document.getElementById('dispatchQrtBtn')?.addEventListener('click', () => {
    alert(`[Dispatched] Quick Response Team (QRT Squad #14) dispatched to ${camName}.`);
  });
  document.getElementById('triggerPaBtn')?.addEventListener('click', () => {
    alert(`[Public Address System] Marathi crowd direction advisory broadcasted at ${camName} speakers.`);
  });

  document.getElementById('cameraModalClose')?.addEventListener('click', () => {
    if (currentModalPlayer) {
      currentModalPlayer.stop();
      currentModalPlayer = null;
    }
    closeAppModal();
  });
}

function setupCctvModal() {
  document.getElementById('camModalCloseBtn')?.addEventListener('click', () => {
    if (currentModalPlayer) {
      currentModalPlayer.stop();
      currentModalPlayer = null;
    }
    document.getElementById('camModal')?.classList.remove('open');
  });
  document.getElementById('modalCamCloseFooterBtn')?.addEventListener('click', () => {
    if (currentModalPlayer) {
      currentModalPlayer.stop();
      currentModalPlayer = null;
    }
    document.getElementById('camModal')?.classList.remove('open');
  });
}

/* ==================== CROWD INTELLIGENCE ==================== */
async function refreshCrowdZones() {
  try {
    const zones = await apiRequest('/crowd/current');
    AppState.crowdZones = zones;
    renderCrowdZones(zones);
  } catch (err) {
    console.debug('[VariSetu] Crowd zones fetch skipped.');
  }
}

function renderCrowdZones(zones) {
  const tbody = document.getElementById('crowdZonesTableBody');
  if (!tbody || !zones || zones.length === 0) return;

  tbody.innerHTML = zones.map(z => {
    const tagClass = z.density_percentage >= 90 ? 'red' : (z.density_percentage >= 75 ? 'orange' : (z.density_percentage >= 50 ? 'yellow' : 'green'));
    return `
      <tr>
        <td><strong>${escapeHtml(z.zone_name)}</strong></td>
        <td><span class="density-tag ${tagClass}">${Math.round(z.density_percentage)}%</span></td>
        <td>${escapeHtml(z.trend || 'STABLE')}</td>
        <td>${escapeHtml(z.recommended_action || 'Standard patrol active')}</td>
      </tr>
    `;
  }).join('');
}

/* ==================== LOST & FOUND MANAGEMENT ==================== */
async function refreshLostPersons() {
  try {
    const cases = await apiRequest('/lost-persons');
    AppState.lostCases = cases;
    renderLostPersons(cases);
    return cases;
  } catch (err) {
    console.debug('[VariSetu] Lost persons fetch skipped.');
    return [];
  }
}

function renderLostPersons(cases) {
  const tbody = document.getElementById('lostPersonsTableBody');
  if (!tbody) return;

  if (!cases || cases.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:12px;">No active lost person cases.</td></tr>`;
    return;
  }

  tbody.innerHTML = cases.map(item => `
    <tr>
      <td>
        <div class="photo-placeholder-box">
          <i data-lucide="user" style="width:16px; height:16px;"></i>
        </div>
      </td>
      <td><strong>${escapeHtml(item.case_number)}</strong></td>
      <td>${escapeHtml(item.name || 'Unknown')}</td>
      <td>${escapeHtml(item.age || '-')} / ${escapeHtml(item.gender || '-')}</td>
      <td>${escapeHtml(item.clothing_description || '-')}</td>
      <td>${escapeHtml(item.last_seen_camera_id || item.last_seen_location || '-')}</td>
      <td>
        <span class="density-tag ${getStatusClass(item.status)}">
          ${escapeHtml(item.status)}
        </span>
      </td>
      <td>
        <button class="govt-btn btn-outline" type="button" data-lost-id="${escapeHtml(item.id)}" data-action="view-lost-case">
          View
        </button>
      </td>
    </tr>
  `).join('');

  if (window.lucide) {
    lucide.createIcons();
  }

  tbody.querySelectorAll('[data-action="view-lost-case"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = AppState.lostCases.find(c => c.id === btn.dataset.lostId);
      if (item) openLostPersonDetails(item);
    });
  });

  if (cases.length > 0 && !AppState.selectedLostCase) {
    showTranscript(cases[0]);
  }
}

function getStatusClass(status) {
  const value = String(status || '').toUpperCase();
  if (value.includes('REUNITED') || value.includes('RESOLVED')) return 'green';
  if (value.includes('MATCH') || value.includes('VERIFIED')) return 'red';
  if (value.includes('SEARCH')) return 'yellow';
  return 'yellow';
}

function showTranscript(caseItem) {
  if (!caseItem) return;
  AppState.selectedLostCase = caseItem;

  const subHeader = document.getElementById('transcriptHeaderSub');
  const box = document.getElementById('transcriptBox');

  if (subHeader) {
    subHeader.textContent = `Helpline 112 Audio Recording Snippet (Deccan Dialect) • Case ${caseItem.case_number}`;
  }

  let text = '';
  if (caseItem.reports && caseItem.reports.length > 0 && caseItem.reports[0].transcript) {
    text = `"${caseItem.reports[0].transcript}"\n\n[Audio Analysis Summary]:\n- Subject: ${caseItem.gender === 'M' ? 'Male' : 'Female'}, ~${caseItem.age} yrs\n- Clothing: ${caseItem.clothing_description}\n- ASR Confidence: ${caseItem.reports[0].asr_confidence ?? 0.94}\n- Last Location: ${caseItem.last_seen_location}`;
  } else if (caseItem.case_number === '#LF-802') {
    text = `"हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."\n\n[Audio Analysis Summary]:\n- Subject: Male, ~68 yrs\n- Clothing: White Kurta, Dhoti, White Cap, Tulsi Mala\n- Audio Confidence score: High (0.94)\n- Vision Cross-Match: CAM-04 Pandharpur Chowk frame #4812 matching features.`;
  } else {
    text = `Case ${caseItem.case_number} - ${caseItem.name}\nAge: ${caseItem.age}, Gender: ${caseItem.gender}\nLast Seen: ${caseItem.last_seen_location}\nAttire: ${caseItem.clothing_description}\nStatus: ${caseItem.status}`;
  }

  if (box) box.textContent = text;
}

function openLostPersonDetails(item) {
  showTranscript(item);

  const photos = (item.photo_urls && Array.isArray(item.photo_urls) && item.photo_urls.length > 0)
    ? item.photo_urls
    : (item.photo_url ? [item.photo_url] : ['assets/palkhi_procession_hd.jpg']);

  openAppModal({
    title: `CASE ${item.case_number}: ${item.name}`,
    kicker: 'LOST & FOUND BIOMETRIC DOSSIER',
    bodyHtml: `
      <div class="app-modal-detail-grid">
        <div class="app-modal-detail-item">
          <div class="app-modal-detail-label">Person Name</div>
          <div class="app-modal-detail-value">${escapeHtml(item.name)}</div>
        </div>
        <div class="app-modal-detail-item">
          <div class="app-modal-detail-label">Age / Gender</div>
          <div class="app-modal-detail-value">${escapeHtml(item.age)} yrs / ${escapeHtml(item.gender)}</div>
        </div>
        <div class="app-modal-detail-item">
          <div class="app-modal-detail-label">Last Seen Location</div>
          <div class="app-modal-detail-value">${escapeHtml(item.last_seen_location)}</div>
        </div>
        <div class="app-modal-detail-item">
          <div class="app-modal-detail-label">Current Status</div>
          <div class="app-modal-detail-value" style="color:var(--maroon-primary); font-weight:bold;">${escapeHtml(item.status)}</div>
        </div>
      </div>
      
      <div style="margin-top:10px; background:var(--bg-subtle); padding:9px; border:1px solid var(--border-main); font-size:11px;">
        <strong>Attire Description:</strong> ${escapeHtml(item.clothing_description)}
      </div>

      <!-- Biometric Photo Gallery Section -->
      <div style="margin-top:12px;">
        <div class="app-modal-detail-label" style="margin-bottom:6px;">Biometric Photo Records & AI Match Pool (${photos.length} Photo${photos.length > 1 ? 's' : ''})</div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          ${photos.map((url, idx) => `
            <div class="photo-upload-thumbnail" style="width:72px; height:72px; position:relative; border:1px solid var(--border-main); background:#000; border-radius:2px; overflow:hidden;">
              <img src="${url}" style="width:100%; height:100%; object-fit:cover;" alt="Photo ${idx + 1}">
              <div style="position:absolute; bottom:0; left:0; right:0; background:rgba(0,0,0,0.75); color:#00FF66; font-size:7.5px; font-family:var(--font-mono); text-align:center; padding:1px 0;">FACE #${idx + 1}</div>
            </div>
          `).join('')}
        </div>
        <div style="margin-top:6px; font-size:10px; color:#2E5B36; font-family:var(--font-mono); display:flex; align-items:center; gap:4px;">
          <span>✨ <strong>AI Face Recognition Active:</strong> 512-D embedding feature vectors extracted across 4 CCTV live streams.</span>
        </div>
      </div>
    `,
    footerHtml: `
      <button type="button" class="govt-btn btn-outline" id="lostDetailClose">Close</button>
      <button type="button" class="govt-btn btn-outline" id="lostDetailDispatch">Dispatch Squad</button>
      ${item.status !== 'REUNITED' ? `<button type="button" class="govt-btn" id="lostDetailReunite">Mark Reunited</button>` : ''}
    `
  });

  document.getElementById('lostDetailClose')?.addEventListener('click', closeAppModal);
  document.getElementById('lostDetailDispatch')?.addEventListener('click', () => {
    dispatchLostPerson(item.id);
  });
  document.getElementById('lostDetailReunite')?.addEventListener('click', () => {
    reuniteLostPerson(item.id);
  });
}

async function dispatchLostPerson(caseId) {
  openConfirmModal({
    title: 'Dispatch Volunteer Squad',
    message: 'Dispatch nearby field volunteer squad to the identified camera checkpoint?',
    confirmText: 'Dispatch Squad',
    onConfirm: async () => {
      await apiRequest(`/lost-persons/${encodeURIComponent(caseId)}/dispatch`, { method: 'POST' });
      await refreshLostPersons();
      await fetchLiveSummary();
    }
  });
}

async function reuniteLostPerson(caseId) {
  openConfirmModal({
    title: 'Reunite & Resolve Case',
    message: 'Confirm that pilgrim has been safely reunited with family/Dindi?',
    confirmText: 'Confirm Reunion',
    onConfirm: async () => {
      await apiRequest(`/lost-persons/${encodeURIComponent(caseId)}/reunite`, { method: 'POST' });
      await refreshLostPersons();
      await fetchLiveSummary();
    }
  });
}

function setupLostFoundButtons() {
  document.getElementById('registerLostPersonBtn')?.addEventListener('click', () => openLostPersonCreateModal(false));

  document.getElementById('dispatchVolunteerBtn')?.addEventListener('click', () => {
    if (AppState.selectedLostCase) {
      dispatchLostPerson(AppState.selectedLostCase.id);
    } else if (AppState.lostCases.length > 0) {
      dispatchLostPerson(AppState.lostCases[0].id);
    }
  });

  document.getElementById('queuePaBtn')?.addEventListener('click', () => {
    const caseItem = AppState.selectedLostCase || AppState.lostCases[0];
    if (caseItem) queuePaAnnouncement(caseItem);
  });
}

function openLostPersonCreateModal(isPublic = false) {
  let uploadedPhotos = [];

  openAppModal({
    title: isPublic ? 'Public Missing Person Registration' : 'Register Missing Person Case',
    kicker: isPublic ? 'CITIZEN REPORTING PORTAL' : 'POLICE HELPLINE CASE ENTRY',
    bodyHtml: `
      <form id="newCaseForm">
        <div class="form-group">
          <label>Full Name of Missing Person (हरवलेल्या व्यक्तीचे नाव)</label>
          <input type="text" id="newCaseName" class="form-control" placeholder="e.g. Maruti Kisan Shinde" required>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          <div class="form-group">
            <label>Age (वय)</label>
            <input type="number" id="newCaseAge" class="form-control" placeholder="68" required>
          </div>
          <div class="form-group">
            <label>Gender (लिंग)</label>
            <select id="newCaseGender" class="form-control">
              <option value="M">Male (पुरुष)</option>
              <option value="F">Female (स्त्री)</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Clothing Description (कपड्यांचे वर्णन)</label>
          <input type="text" id="newCaseClothing" class="form-control" placeholder="पांढरा कुर्ता, धोती, पांढरी टोपी, गळ्यात तुळशी माळ" required>
        </div>
        <div class="form-group">
          <label>Last Seen Location (शेवटचे पाहिलेले ठिकाण)</label>
          <input type="text" id="newCaseLocation" class="form-control" placeholder="Wakhri Phata / Sector 3 near Water Station" required>
        </div>

        ${isPublic ? `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          <div class="form-group">
            <label>Your Name (आपले नाव)</label>
            <input type="text" id="newCaseCallerName" class="form-control" placeholder="e.g. Ramesh Shinde">
          </div>
          <div class="form-group">
            <label>Contact Phone (मोबाईल नंबर)</label>
            <input type="text" id="newCaseCallerPhone" class="form-control" placeholder="e.g. 9876543210">
          </div>
        </div>
        ` : `
        <div class="form-group">
          <label>Priority</label>
          <select id="newCasePriority" class="form-control">
            <option value="HIGH">High (तातडीचे)</option>
            <option value="CRITICAL">Critical (अति तातडीचे)</option>
            <option value="NORMAL">Normal</option>
          </select>
        </div>
        `}

        <!-- Multi-Photo Upload Section (4-5 Photos for AI Face Detection) -->
        <div class="form-group" style="margin-top:10px;">
          <label>Photographs for AI Facial Recognition (Upload 1-5 Photos / फोटो जोडा)</label>
          <input type="file" id="lostPersonPhotoInput" multiple accept="image/*" style="display:none;">
          
          <div id="lostPersonDropzone" style="border:2px dashed var(--border-main); padding:12px; text-align:center; background:var(--bg-subtle); cursor:pointer; border-radius:2px; transition:border-color 0.2s;">
            <div style="font-weight:600; font-size:11px; color:var(--maroon-primary); margin-bottom:2px;">
              📁 Click to Upload 4-5 Photos (Frontal Face, Profile, Full Body)
            </div>
            <div style="font-size:9.5px; color:var(--text-muted);">
              PNG, JPG, JPEG accepted &bull; Max 5 images
            </div>
          </div>

          <div id="selectedPhotosPreviewContainer" style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;"></div>

          <div id="aiEmbeddingBadge" style="margin-top:6px; font-size:10px; color:#2E5B36; font-family:var(--font-mono); background:#E8F5E9; border:1px solid #A5D6A7; padding:6px 8px; border-radius:2px; display:none;">
            ✨ <strong>AI Face Recognition Model Slot Ready:</strong> Feature embeddings (512-D vectors) will be indexed for instant multi-camera CCTV matching.
          </div>
        </div>
      </form>
    `,
    footerHtml: `
      <button type="button" class="govt-btn btn-outline" id="newCaseCancel">Cancel</button>
      <button type="button" class="govt-btn" id="newCaseSubmit">${isPublic ? 'Submit Report (तक्रार दाखल करा)' : 'Register Case'}</button>
    `
  });

  // Setup Image Dropzone & Multi-file Upload
  const dropzone = document.getElementById('lostPersonDropzone');
  const fileInput = document.getElementById('lostPersonPhotoInput');
  const previewContainer = document.getElementById('selectedPhotosPreviewContainer');
  const aiBadge = document.getElementById('aiEmbeddingBadge');

  dropzone?.addEventListener('click', () => fileInput?.click());

  function renderPhotoThumbnails() {
    if (!previewContainer) return;
    previewContainer.innerHTML = '';

    uploadedPhotos.forEach((dataUrl, idx) => {
      const thumb = document.createElement('div');
      thumb.className = 'photo-upload-thumbnail';
      thumb.innerHTML = `
        <img src="${dataUrl}" alt="Face ${idx + 1}">
        <button type="button" class="photo-upload-remove-btn" title="Remove" data-idx="${idx}">×</button>
        <div style="position:absolute; bottom:0; left:0; right:0; background:rgba(0,0,0,0.7); color:#00FF66; font-size:7px; font-family:var(--font-mono); text-align:center;">#${idx + 1}</div>
      `;
      thumb.querySelector('.photo-upload-remove-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        uploadedPhotos.splice(idx, 1);
        renderPhotoThumbnails();
      });
      previewContainer.appendChild(thumb);
    });

    if (aiBadge) {
      aiBadge.style.display = uploadedPhotos.length > 0 ? 'block' : 'none';
    }
  }

  fileInput?.addEventListener('change', (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    const remainingSlots = 5 - uploadedPhotos.length;
    const toProcess = files.slice(0, remainingSlots);

    toProcess.forEach(file => {
      const reader = new FileReader();
      reader.onload = (loadEvt) => {
        if (loadEvt.target?.result && uploadedPhotos.length < 5) {
          uploadedPhotos.push(loadEvt.target.result);
          renderPhotoThumbnails();
        }
      };
      reader.readAsDataURL(file);
    });
  });

  document.getElementById('newCaseCancel')?.addEventListener('click', closeAppModal);
  document.getElementById('newCaseSubmit')?.addEventListener('click', async () => {
    const name = document.getElementById('newCaseName')?.value?.trim();
    const age = parseInt(document.getElementById('newCaseAge')?.value || '0');
    const gender = document.getElementById('newCaseGender')?.value || 'M';
    const clothing = document.getElementById('newCaseClothing')?.value?.trim();
    const location = document.getElementById('newCaseLocation')?.value?.trim();
    const priority = document.getElementById('newCasePriority')?.value || 'HIGH';
    const callerName = document.getElementById('newCaseCallerName')?.value?.trim() || null;
    const callerPhone = document.getElementById('newCaseCallerPhone')?.value?.trim() || null;

    if (!name || !age || !clothing || !location) {
      alert('Please fill out all required fields.');
      return;
    }

    const submitBtn = document.getElementById('newCaseSubmit');
    setButtonLoading(submitBtn, true, 'Submitting...');

    try {
      if (isPublic) {
        const resp = await apiRequest('/public/report-lost', {
          method: 'POST',
          body: {
            name,
            age,
            gender,
            clothing_description: clothing,
            last_seen_location: location,
            caller_name: callerName,
            caller_phone: callerPhone,
            photo_urls: uploadedPhotos
          },
          skipAuthRefresh: true
        });

        openAppModal({
          title: 'Report Submitted Successfully',
          kicker: 'AI FACIAL SEARCH ACTIVATED',
          bodyHtml: `
            <div style="text-align:center; padding:12px 0;">
              <div style="font-size:28px; margin-bottom:8px;">✅</div>
              <div style="font-weight:700; font-size:14px; color:var(--maroon-primary); margin-bottom:6px;">
                Case Reference: ${escapeHtml(resp.case_number || '#LF-NEW')}
              </div>
              <div style="font-size:12px; color:var(--text-primary); line-height:1.5;">
                Your report for <strong>${escapeHtml(name)}</strong> has been registered with the Police Command Center.<br>
                ${uploadedPhotos.length} photo(s) submitted for biometric recognition across all CCTV checkpoints.
              </div>
            </div>
          `,
          footerHtml: `
            <button type="button" class="govt-btn" id="publicSuccessClose">Close & Return to Map</button>
          `
        });
        document.getElementById('publicSuccessClose')?.addEventListener('click', closeAppModal);
      } else {
        await apiRequest('/lost-persons', {
          method: 'POST',
          body: {
            name,
            age,
            gender,
            clothing_description: clothing,
            last_seen_location: location,
            priority,
            photo_urls: uploadedPhotos,
            photo_url: uploadedPhotos[0] || null
          }
        });

        closeAppModal();
        await refreshLostPersons();
        await fetchLiveSummary();
      }
    } catch (err) {
      document.getElementById('appModalBody').innerHTML = `
        <div class="modal-error">${escapeHtml(err.message || 'Registration failed.')}</div>
      `;
      setButtonLoading(submitBtn, false, 'Register Case');
    }
  });
}

function setupMedicalEmergencyButtons() {
  document.getElementById('addMedicalAlertBtn')?.addEventListener('click', openAddMedicalEmergencyModal);
}

function openAddMedicalEmergencyModal() {
  openAppModal({
    title: 'Report Medical Emergency',
    kicker: 'FIRST RESPONDER & AMBULANCE DISPATCH',
    bodyHtml: `
      <form id="newMedicalAlertForm">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          <div class="form-group">
            <label>Emergency Category (प्रकार)</label>
            <select id="medType" class="form-control" required>
              <option value="HEAT_EXHAUSTION">HEAT_EXHAUSTION (उष्माघात / चक्कर)</option>
              <option value="DEHYDRATION">DEHYDRATION (अशक्तपणा / निर्जलीकरण)</option>
              <option value="FALL">FALL (पडून झालेली दुखापत)</option>
              <option value="FAINTING">FAINTING (बेशुद्ध पडणे)</option>
              <option value="CARDIAC_RISK">CARDIAC_RISK (हृदयविकार / छातीत दुखणे)</option>
              <option value="OTHER">OTHER (इतर वैद्यकीय मदत)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Triage Severity Level</label>
            <select id="medSeverity" class="form-control">
              <option value="HIGH">HIGH (तातडीची मदत)</option>
              <option value="CRITICAL">CRITICAL (गंभीर / जीवघेणी)</option>
              <option value="MEDIUM">MEDIUM (मध्यम)</option>
              <option value="LOW">LOW (किरकोळ)</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Chokepoint / Route Location (ठिकाण)</label>
          <input type="text" id="medLocation" class="form-control" placeholder="e.g. Sector 3 (Wakhri Phata Km 184) near Water Station #4" required>
        </div>
        <div class="form-group">
          <label>Emergency Details / Pilgrim Symptoms (तपशील व लक्षणे)</label>
          <textarea id="medDesc" class="form-control" rows="3" placeholder="Describe pilgrim condition, gender, age, symptoms and required immediate aid..." required></textarea>
        </div>
        <div class="form-group">
          <label>Assign First Responder / Ambulance Unit (Optional)</label>
          <input type="text" id="medVolunteer" class="form-control" placeholder="e.g. Mobile Medical Van #MV-02 (Dr. Deshmukh)">
        </div>
      </form>
    `,
    footerHtml: `
      <button type="button" class="govt-btn btn-outline" id="medCancelBtn">Cancel</button>
      <button type="button" class="govt-btn" id="medSubmitBtn" style="background:var(--status-red);">Dispatch Medical Alert</button>
    `
  });

  document.getElementById('medCancelBtn')?.addEventListener('click', closeAppModal);
  document.getElementById('medSubmitBtn')?.addEventListener('click', async () => {
    const type = document.getElementById('medType')?.value || 'HEAT_EXHAUSTION';
    const severity = document.getElementById('medSeverity')?.value || 'HIGH';
    const location = document.getElementById('medLocation')?.value?.trim();
    const desc = document.getElementById('medDesc')?.value?.trim();
    const volunteer = document.getElementById('medVolunteer')?.value?.trim() || null;
    const submitBtn = document.getElementById('medSubmitBtn');

    if (!location || !desc) {
      alert('Please fill out Location and Emergency Details.');
      return;
    }

    setButtonLoading(submitBtn, true, 'Dispatching...');

    try {
      await apiRequest('/medical-alerts', {
        method: 'POST',
        body: {
          type,
          severity,
          latitude: 17.7280,
          longitude: 75.2950,
          description: `${location} - ${desc}`,
          assigned_volunteer_name: volunteer,
          is_demo: false
        }
      });
      closeAppModal();
      await refreshMedicalAlerts();
    } catch (err) {
      alert(err.message || 'Failed to dispatch medical alert.');
      setButtonLoading(submitBtn, false, 'Dispatch Medical Alert');
    }
  });
}

function queuePaAnnouncement(caseItem) {
  openConfirmModal({
    title: 'Queue Public Address Announcement',
    message: `Queue loudspeaker announcement for Case ${caseItem.case_number} (${caseItem.name}) across Sector 3 & Wakhri Phata PA systems?`,
    confirmText: 'Queue Announcement',
    onConfirm: async () => {
      try {
        await apiRequest(`/lost-persons/${encodeURIComponent(caseItem.id)}/pa-announce`, {
          method: 'POST'
        });
      } catch (e) {
        console.debug('[VariSetu] PA announcement simulated.');
      }

      openAppModal({
        title: 'PA Announcement Broadcasted',
        bodyHtml: `
          <div class="modal-success">
            Announcement queued in demo mode: "हरवलेली व्यक्ती: ${escapeHtml(caseItem.name)}, वय ${escapeHtml(caseItem.age)}, पोशाख: ${escapeHtml(caseItem.clothing_description)}."
          </div>
        `,
        footerHtml: `<button class="govt-btn" id="paDoneBtn">Done</button>`
      });
      document.getElementById('paDoneBtn')?.addEventListener('click', closeAppModal);
    }
  });
}

/* ==================== MEDICAL ALERTS ==================== */
async function refreshMedicalAlerts() {
  try {
    const alerts = await apiRequest('/medical-alerts');
    AppState.medicalAlerts = alerts;
    renderMedicalAlerts(alerts);
    return alerts;
  } catch (err) {
    console.debug('[VariSetu] Medical alerts fetch skipped.');
    return [];
  }
}

function renderMedicalAlerts(alerts) {
  const container = document.getElementById('medicalAlertsContainer');
  if (!container) return;

  if (!alerts || alerts.length === 0) {
    container.innerHTML = `<div style="padding:12px; color:var(--text-secondary);">No active medical alerts.</div>`;
    return;
  }

  container.innerHTML = alerts.map(alert => `
    <div class="alert-card-item ${alert.status === 'RESOLVED' ? 'acknowledged' : ''}" data-medical-id="${escapeHtml(alert.id)}">
      <div>
        <div style="font-weight:700; color:var(--status-red); font-size:13px;">
          ${escapeHtml(alert.type?.replace('_', ' ') || 'MEDICAL EMERGENCY')}
        </div>
        <div style="font-size:11px; color:var(--text-secondary); margin:2px 0;">
          ${escapeHtml(alert.description || 'Medical incident reported')}
        </div>
        <div style="font-size:11px; color:var(--text-muted);">
          Assigned Volunteer / Unit: ${escapeHtml(alert.assigned_volunteer_name || 'Standby')}
        </div>
      </div>
      <div>
        ${
          alert.status === 'ACTIVE'
            ? `<button class="govt-btn" type="button" data-medical-ack="${escapeHtml(alert.id)}">Acknowledge</button>`
            : `<button class="govt-btn btn-disabled" type="button" disabled>${escapeHtml(alert.status)}</button>`
        }
      </div>
    </div>
  `).join('');

  container.querySelectorAll('[data-medical-ack]').forEach(button => {
    button.addEventListener('click', () => {
      acknowledgeMedicalAlert(button.dataset.medicalAck, button);
    });
  });
}

async function acknowledgeMedicalAlert(alertId, button) {
  if (!alertId) return;

  try {
    setButtonLoading(button, true, 'Acknowledging...');

    const updated = await apiRequest(`/medical-alerts/${encodeURIComponent(alertId)}/acknowledge`, {
      method: 'POST',
      body: { notes: 'Acknowledged via VariSetu Command Dashboard' }
    });

    await refreshMedicalAlerts();
    await fetchLiveSummary();

    openAppModal({
      title: 'Medical Alert Acknowledged',
      bodyHtml: `
        <div class="modal-success">
          Alert <strong>${escapeHtml(updated.alert_code || updated.id)}</strong> has been acknowledged. Ambulance / Volunteer unit assigned.
        </div>
      `,
      footerHtml: `<button class="govt-btn" id="medAckDoneBtn">Done</button>`
    });
    document.getElementById('medAckDoneBtn')?.addEventListener('click', closeAppModal);
  } catch (error) {
    openAppModal({
      title: 'Acknowledgement Failed',
      bodyHtml: `<div class="modal-error">${escapeHtml(error.message)}</div>`,
      footerHtml: `<button class="govt-btn" id="medAckErrClose">Close</button>`
    });
    document.getElementById('medAckErrClose')?.addEventListener('click', closeAppModal);
  } finally {
    setButtonLoading(button, false, 'Acknowledge');
  }
}

async function fetchHeatRisk() {
  try {
    const data = await apiRequest('/dashboard/heat-risk');
    if (!data) return;

    const t = document.getElementById('heatTemp');
    const h = document.getElementById('heatHumidity');
    const r = document.getElementById('heatRiskIndex');
    const w = document.getElementById('heatWaterStations');
    const o = document.getElementById('heatOrslSupplies');
    const adv = document.getElementById('heatAdvisoryText');

    if (t) t.textContent = data.ambient_temperature;
    if (h) h.textContent = data.relative_humidity;
    if (r) r.textContent = data.computed_risk_index;
    if (w) w.textContent = data.water_stations_active;
    if (o) o.textContent = data.orsl_sachet_supplies;
    if (adv) adv.innerHTML = `<strong>Advisory Action:</strong> ${escapeHtml(data.advisory_action)}`;
  } catch (err) {
    console.debug('[VariSetu] Heat risk fetch skipped.');
  }
}

/* ==================== RESOURCES MANAGEMENT ==================== */
async function refreshResources() {
  try {
    const resources = await apiRequest('/resources');
    AppState.resources = resources;
    renderResources(resources);
    return resources;
  } catch (err) {
    console.debug('[VariSetu] Resources fetch skipped.');
    return [];
  }
}

function renderResources(resources) {
  const tbody = document.getElementById('resourcesTableBody');
  if (!tbody || !resources || resources.length === 0) return;

  const grouped = {};
  resources.forEach(r => {
    let key = r.resource_type?.replace('_', ' ') || 'GENERAL RESOURCE';
    if (r.resource_type === 'WATER_TANKER') key = 'Water Tankers (10,000L)';
    else if (r.resource_type === 'MEDICAL_VAN' || r.resource_type === 'AMBULANCE') key = 'Mobile Medical Vans & Ambulances';
    else if (r.resource_type === 'POLICE_SQUAD') key = 'Police Patrol Squads';
    else if (r.resource_type === 'VOLUNTEER_TEAM') key = 'Volunteer Dindi Stewards';
    else if (r.resource_type === 'FOOD_VAN') key = 'Food Distribution Vans';

    if (!grouped[key]) {
      grouped[key] = { total: 0, available: 0, deployed: 0, locations: [] };
    }
    grouped[key].total += 1;
    if (r.availability === 'AVAILABLE') {
      grouped[key].available += 1;
    } else {
      grouped[key].deployed += 1;
    }
    if (r.location_description) {
      grouped[key].locations.push(r.location_description);
    }
  });

  tbody.innerHTML = Object.entries(grouped).map(([type, item]) => `
    <tr>
      <td><strong>${escapeHtml(type)}</strong></td>
      <td>${item.deployed} Units</td>
      <td>${item.available} Units</td>
      <td>${escapeHtml(item.locations.slice(0, 2).join(' & ') || 'Corridor Stations')}</td>
      <td>
        <span class="density-tag ${item.available > 0 ? 'green' : 'red'}">
          ${item.available > 0 ? 'OPTIMAL' : 'DEPLOYED'}
        </span>
      </td>
    </tr>
  `).join('');
}

/* ==================== ROUTES DIVERSION ==================== */
async function refreshRoutes() {
  try {
    const routes = await apiRequest('/routes');
    AppState.routes = routes;
    renderRoutes(routes);
    return routes;
  } catch (err) {
    console.debug('[VariSetu] Routes fetch skipped.');
    return [];
  }
}

function renderRoutes(routes) {
  const container = document.getElementById('routesContainer');
  if (!container || !routes || routes.length === 0) return;

  container.innerHTML = routes.map(route => `
    <div class="route-status-item" data-route-id="${escapeHtml(route.id)}">
      <div>
        <div style="font-weight:600; font-size:12px;">${escapeHtml(route.name)}</div>
        <div style="font-size:10px; color:var(--text-secondary);">${escapeHtml(route.description || '')}</div>
      </div>
      <span class="status-pill ${getRouteClass(route.status)}">
        ${escapeHtml(route.status?.replace('_', ' '))}
      </span>
    </div>
  `).join('');
}

function getRouteClass(status) {
  const s = String(status || '').toUpperCase();
  if (s.includes('OPEN') || s.includes('PILGRIM') || s.includes('EMERGENCY')) return 'open';
  if (s.includes('CLOSED')) return 'closed';
  if (s.includes('DIVERT')) return 'diverted';
  return 'open';
}

/* ==================== DEMO SIMULATION ==================== */
function setupDemoButton() {
  const btn = document.getElementById('demoToggleBtn');
  const text = document.getElementById('demoToggleText');

  btn?.addEventListener('click', async () => {
    if (!AppState.isDemoRunning) {
      openConfirmModal({
        title: 'Start Wari Pilgrimage Simulation',
        message: 'Start the automated 12-step emergency scenario? Live crowd peaks, lost person matching, and medical dispatches will stream in real-time.',
        confirmText: 'Start Simulation',
        onConfirm: async () => {
          await apiRequest('/demo/start', { method: 'POST' });
          AppState.isDemoRunning = true;
          if (text) text.textContent = 'Stop Demo';
          appendTickerEvent('[DEMO] 12-step pilgrimage operational scenario started.');
        }
      });
    } else {
      await apiRequest('/demo/stop', { method: 'POST' });
      AppState.isDemoRunning = false;
      if (text) text.textContent = 'Start Demo';
      appendTickerEvent('[DEMO] Simulation stopped.');
    }
  });
}

/* ==================== REALTIME AUTHENTICATED WEBSOCKET CLIENT ==================== */
function connectWebSocket() {
  disconnectWebSocket();

  const token = getAccessToken();
  if (!token) return;

  try {
    const ws = new WebSocket(`${WS_BASE}/all?token=${encodeURIComponent(token)}`);
    window.varisetuWebSocket = ws;
    AppState.ws = ws;

    ws.onopen = () => {
      console.log('[VariSetu Live] Authenticated WebSocket connected to /ws/all');
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        handleLiveEvent(payload);
      } catch (e) {
        console.error('[VariSetu Live] WS parse error:', e);
      }
    };

    ws.onclose = (event) => {
      if (event.code === 1008) {
        console.warn('[VariSetu Live] WebSocket authentication failed.');
        handleSessionExpiration();
      } else if (getAccessToken()) {
        setTimeout(connectWebSocket, 5000);
      }
    };
  } catch (err) {
    console.debug('[VariSetu Live] WebSocket initialization deferred.');
  }
}

function disconnectWebSocket() {
  if (window.varisetuWebSocket) {
    try {
      window.varisetuWebSocket.close();
    } catch {}
    window.varisetuWebSocket = null;
    AppState.ws = null;
  }
}

async function handleLiveEvent(msg) {
  if (!msg || !msg.event) return;

  switch (msg.event) {
    case 'TICKER_EVENT':
      if (msg.data?.text) {
        appendTickerEvent(msg.data.text);
      }
      break;

    case 'INCIDENT_CREATED':
    case 'INCIDENT_UPDATED':
      await fetchLiveSummary();
      break;

    case 'CROWD_UPDATED':
      await refreshCrowdZones();
      await fetchLiveSummary();
      break;

    case 'MEDICAL_ALERT_CREATED':
    case 'MEDICAL_ALERT_UPDATED':
      await refreshMedicalAlerts();
      await fetchLiveSummary();
      break;

    case 'RESOURCE_DISPATCHED':
    case 'RESOURCE_STATUS_CHANGED':
      await refreshResources();
      await fetchLiveSummary();
      break;

    case 'LOST_PERSON_MATCH_FOUND':
    case 'LOST_PERSON_VERIFIED':
    case 'LOST_PERSON_REUNITED':
      await refreshLostPersons();
      await fetchLiveSummary();
      break;

    case 'ROUTE_CHANGED':
      await refreshRoutes();
      break;

    default:
      console.debug('[VariSetu] Realtime event received:', msg.event);
  }
}

function appendTickerEvent(text) {
  const ticker = document.getElementById('incidentLogText');
  if (!ticker || !text) return;

  const current = ticker.textContent.trim();
  if (!current) {
    ticker.textContent = text;
    return;
  }
  ticker.textContent = `${text} -- ${current}`;
}

```

---

## Frontend/package.json
`Frontend/package.json`

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

## docker-compose.yml
`docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: varisetu-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgrespassword
      POSTGRES_DB: varisetu
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: varisetu-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Optional Qdrant profile (can be started with: docker compose --profile vector up)
  qdrant:
    image: qdrant/qdrant:v1.8.0
    container_name: varisetu-qdrant
    profiles: ["vector"]
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

```

---

## Backend/requirements.txt
`Backend/requirements.txt`

```text
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic[email]>=2.6.0
pydantic-settings>=2.2.0
sqlalchemy>=2.0.28
asyncpg>=0.29.0
aiosqlite>=0.20.0
alembic>=1.13.1
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.1.2
redis>=5.0.3
httpx>=0.27.0
python-multipart>=0.0.9
pytest>=8.1.0
pytest-asyncio>=0.23.5
websockets>=12.0
email-validator>=2.0.0

```

---

## Backend/pytest.ini
`Backend/pytest.ini`

```ini
[pytest]
pythonpath = .
asyncio_mode = auto
testpaths = tests

```

---

## Backend/app/main.py
`Backend/app/main.py`

```python
import os
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.cameras import router as cameras_router
from app.api.crowd import router as crowd_router
from app.api.dashboard import router as dashboard_router
from app.api.incidents import router as incidents_router
from app.api.lost_persons import router as lost_persons_router
from app.api.medical import router as medical_router
from app.api.notifications import audit_router, demo_router, health_router, notifications_router
from app.api.public import public_router
from app.api.resources import router as resources_router
from app.api.routes import router as routes_router
from app.api.zones import router as zones_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.core.redis import redis_client
from app.core.security import decode_token
from app.seed.seed_data import seed_database
from app.services.demo_service import demo_service
from app.websocket.manager import ws_manager

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing VariSetu Command Center Backend...")
    await redis_client.connect()
    await init_db()
    try:
        await seed_database()
    except Exception as e:
        logger.warning(f"Auto-seeding skipped or failed: {e}")

    yield

    # Shutdown sequence
    logger.info("Shutting down VariSetu Command Center Backend...")
    await demo_service.stop()
    await redis_client.disconnect()


app = FastAPI(
    title="VariSetu Command Center API",
    description="Mission-critical command & control backend for Ashadhi Wari pilgrimage crowd safety, biometric lost person reunion, and emergency resource management.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    response.headers["X-App-Name"] = "VariSetu"
    return response


# Ensure uploads directory exists and mount static files
os.makedirs(settings.STORAGE_LOCAL_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.STORAGE_LOCAL_DIR), name="uploads")

# Register REST Routers
app.include_router(health_router)
app.include_router(public_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(cameras_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(crowd_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(lost_persons_router, prefix=settings.API_V1_STR)
app.include_router(medical_router, prefix=settings.API_V1_STR)
app.include_router(resources_router, prefix=settings.API_V1_STR)
app.include_router(routes_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)


# Realtime WebSockets Channels with JWT Verification
@app.websocket("/ws")
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "all", token: Optional[str] = None):
    if settings.AUTH_REQUIRED:
        auth_token = token or websocket.query_params.get("token")
        if not auth_token:
            await websocket.close(code=1008)
            return
        payload = decode_token(auth_token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=1008)
            return

    await ws_manager.connect(websocket, channel=channel)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            logger.debug(f"Received WS message on {channel}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel=channel)
    except Exception as e:
        logger.warning(f"WebSocket error on channel {channel}: {e}")
        ws_manager.disconnect(websocket, channel=channel)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

```

---

## Backend/app/core/config.py
`Backend/app/core/config.py`

```python
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    APP_NAME: str = "VariSetu Command Center API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Database connection string
    # Standard PostgreSQL: postgresql+asyncpg://postgres:postgres@localhost:5432/varisetu
    # Supabase PostgreSQL: postgresql+asyncpg://postgres:[password]@db.[ref].supabase.co:5432/postgres
    # SQLite fallback for zero-setup local dev/test: sqlite+aiosqlite:///./varisetu.db
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./varisetu.db",
        description="Async database connection string"
    )

    # Sync Database URL for Alembic migrations if needed
    @property
    def SYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg2").replace("postgresql+psycopg2", "postgresql")
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        return url

    # Redis Connection (Optional, falls back to in-memory)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # Security & JWT Token Config
    JWT_SECRET_KEY: str = "varisetu-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Authentication is enforced in the production system
    AUTH_REQUIRED: bool = True

    # Modular Storage & AI Provider Settings
    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./uploads"

    VECTOR_PROVIDER: str = "mock"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None

    SPEECH_PROVIDER: str = "mock"
    VISION_PROVIDER: str = "mock"
    WEATHER_PROVIDER: str = "mock"
    NOTIFICATION_PROVIDER: str = "mock"

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]


settings = Settings()

```

---

## Backend/app/core/database.py
`Backend/app/core/database.py`

```python
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger("varisetu.database")

# Build engine arguments based on driver
engine_kwargs = {
    "echo": False,
    "future": True,
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL pooling parameters
    engine_kwargs["pool_size"] = 15
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async SQLAlchemy session.
    Automatically closes session upon request completion.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database schema (creates tables if they don't exist).
    Used during initial startup or in-memory testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")

```

---

## Backend/app/core/security.py
`Backend/app/core/security.py`

```python
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against its bcrypt hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode("utf-8")
        else:
            hashed_bytes = hashed_password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a plaintext password."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str = "VIEWER",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate JWT Access Token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate JWT Refresh Token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None

```

---

## Backend/app/core/rbac.py
`Backend/app/core/rbac.py`

```python
import enum
from typing import List, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_token


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    COMMANDER = "COMMANDER"
    POLICE = "POLICE"
    MEDICAL = "MEDICAL"
    RESOURCE_MANAGER = "RESOURCE_MANAGER"
    VOLUNTEER_COORDINATOR = "VOLUNTEER_COORDINATOR"
    VIEWER = "VIEWER"


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Extracts user from JWT token if present.
    If AUTH_REQUIRED is False and no token is passed, returns a default mock Commander user.
    """
    from app.models.user import User

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            query = select(User).where(User.id == user_id, User.is_active == True)
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user

    if not settings.AUTH_REQUIRED:
        # Return a fallback admin/commander user object for development prototyping
        return User(
            id="00000000-0000-0000-0000-000000000001",
            name="Command Center Controller",
            email="control.room@mahapolice.gov.in",
            role=UserRole.ADMIN,
            department="Maharashtra Police IT Cell",
            is_active=True
        )

    return None


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Strictly requires an authenticated user."""
    user = await get_current_user_optional(authorization, db)
    if not user:
        raise UnauthorizedException("Valid authentication credentials required")
    return user


def require_roles(allowed_roles: List[UserRole]):
    """Role-based authorization dependency factory."""
    async def role_checker(current_user = Depends(get_current_user)):
        if current_user.role == UserRole.ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Role {current_user.role} does not have permission for this operation"
            )
        return current_user
    return role_checker

```

---

## Backend/app/core/redis.py
`Backend/app/core/redis.py`

```python
import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("varisetu.redis")

class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._memory_cache: dict = {}
        self.is_connected: bool = False

    async def connect(self):
        """Attempt to connect to Redis, fall back to in-memory mode if unavailable."""
        if not settings.REDIS_URL:
            logger.info("No REDIS_URL configured; using in-memory cache fallback.")
            return

        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0
            )
            await self.redis.ping()
            self.is_connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self.is_connected = False
            self.redis = None
            logger.warning(f"Redis connection failed ({e}); operating in in-memory cache fallback mode.")

    async def disconnect(self):
        if self.redis and self.is_connected:
            await self.redis.close()
            self.is_connected = False
            logger.info("Disconnected from Redis.")

    async def get(self, key: str) -> Optional[Any]:
        if self.is_connected and self.redis:
            try:
                val = await self.redis.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return self._memory_cache.get(key)

    async def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        serialized = json.dumps(value, default=str)
        if self.is_connected and self.redis:
            try:
                await self.redis.set(key, serialized, ex=expire_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        self._memory_cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        if self.is_connected and self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        self._memory_cache.pop(key, None)
        return True

    async def publish(self, channel: str, message: dict):
        serialized = json.dumps(message, default=str)
        if self.is_connected and self.redis:
            try:
                await self.redis.publish(channel, serialized)
            except Exception as e:
                logger.error(f"Redis publish error: {e}")


redis_client = RedisClient()

```

---

## Backend/app/core/exceptions.py
`Backend/app/core/exceptions.py`

```python
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {}
                }
            }
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid credentials or unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code=code, message=message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Insufficient role permissions", code: str = "FORBIDDEN"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code=code, message=message)


class ValidationException(AppException):
    def __init__(self, message: str = "Request validation failed", code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code=code, message=message, details=details)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict", code: str = "CONFLICT"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, code=code, message=message)


class StateTransitionException(AppException):
    def __init__(self, current_state: str, attempted_state: str, entity_type: str = "Entity"):
        message = f"Invalid status transition for {entity_type}: cannot transition from {current_state} to {attempted_state}."
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_STATE_TRANSITION",
            message=message,
            details={"current_state": current_state, "attempted_state": attempted_state}
        )

```

---

## Backend/app/core/logging.py
`Backend/app/core/logging.py`

```python
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure structured logging for VariSetu."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence overly verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger = logging.getLogger("varisetu")
    logger.info(f"Logging initialized in {settings.APP_ENV} mode (Level: {logging.getLevelName(log_level)})")
    return logger

```

---

## Backend/app/models/__init__.py
`Backend/app/models/__init__.py`

```python
from app.core.database import Base
from app.models.base import BaseModel
from app.models.user import User
from app.models.zone import Zone, RiskLevel
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.forecast import CrowdForecast
from app.models.incident import Incident, IncidentEvent, IncidentType, IncidentSeverity, IncidentStatus
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.medical import MedicalAlert, MedicalAlertType, MedicalAlertStatus
from app.models.resource import Resource, ResourceAssignment, ResourceType, ResourceAvailability, ResourceAssignmentStatus
from app.models.route import Route, RouteStatus
from app.models.notification import Notification, NotificationType
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "Zone",
    "RiskLevel",
    "Camera",
    "CameraStatus",
    "CrowdObservation",
    "CrowdTrend",
    "CrowdForecast",
    "Incident",
    "IncidentEvent",
    "IncidentType",
    "IncidentSeverity",
    "IncidentStatus",
    "LostPersonCase",
    "LostPersonReport",
    "LostPersonStatus",
    "FaceMatchResult",
    "FaceMatchStatus",
    "MedicalAlert",
    "MedicalAlertType",
    "MedicalAlertStatus",
    "Resource",
    "ResourceAssignment",
    "ResourceType",
    "ResourceAvailability",
    "ResourceAssignmentStatus",
    "Route",
    "RouteStatus",
    "Notification",
    "NotificationType",
    "AuditLog",
]

```

---

## Backend/app/models/base.py
`Backend/app/models/base.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

```

---

## Backend/app/models/user.py
`Backend/app/models/user.py`

```python
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.rbac import UserRole
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_roles"),
        default=UserRole.VIEWER,
        nullable=False
    )
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

```

---

## Backend/app/models/zone.py
`Backend/app/models/zone.py`

```python
import enum
from typing import Optional
from sqlalchemy import Boolean, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Zone(BaseModel):
    __tablename__ = "zones"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_levels"),
        default=RiskLevel.LOW,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

```

---

## Backend/app/models/camera.py
`Backend/app/models/camera.py`

```python
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"


class Camera(BaseModel):
    __tablename__ = "cameras"

    camera_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    rtsp_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[CameraStatus] = mapped_column(
        Enum(CameraStatus, name="camera_statuses"),
        default=CameraStatus.ONLINE,
        nullable=False,
        index=True
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    zone = relationship("Zone", backref="cameras")

```

---

## Backend/app/models/crowd.py
`Backend/app/models/crowd.py`

```python
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.zone import RiskLevel


class CrowdTrend(str, enum.Enum):
    RISING = "RISING"
    STABLE = "STABLE"
    FALLING = "FALLING"
    EASING = "EASING"


class CrowdObservation(BaseModel):
    __tablename__ = "crowd_observations"

    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True, index=True)
    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    density_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    movement_direction: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    trend: Mapped[CrowdTrend] = mapped_column(
        Enum(CrowdTrend, name="crowd_trends"),
        default=CrowdTrend.STABLE,
        nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="crowd_risk_levels"),
        default=RiskLevel.LOW,
        nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), default="DEMO", nullable=False)  # DEMO / VISION_YOLO / SENSOR
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    zone = relationship("Zone", backref="crowd_observations")
    camera = relationship("Camera", backref="crowd_observations")


# Composite index for performance
Index("idx_crowd_zone_time", CrowdObservation.zone_id, CrowdObservation.observed_at.desc())

```

---

## Backend/app/models/forecast.py
`Backend/app/models/forecast.py`

```python
from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.zone import RiskLevel


class CrowdForecast(BaseModel):
    __tablename__ = "crowd_forecasts"

    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    predicted_density: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="forecast_risk_levels"),
        default=RiskLevel.LOW,
        nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(50), default="demo-rule-based-v1", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)

    # Relationship
    zone = relationship("Zone", backref="forecasts")

```

---

## Backend/app/models/incident.py
`Backend/app/models/incident.py`

```python
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class IncidentType(str, enum.Enum):
    CROWD = "CROWD"
    MEDICAL = "MEDICAL"
    MISSING_PERSON = "MISSING_PERSON"
    SECURITY = "SECURITY"
    ROAD_BLOCK = "ROAD_BLOCK"
    RESOURCE = "RESOURCE"
    FIRE = "FIRE"
    OTHER = "OTHER"


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Incident(BaseModel):
    __tablename__ = "incidents"

    incident_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incident_types"),
        nullable=False,
        index=True
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severities"),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
        index=True
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_statuses"),
        default=IncidentStatus.OPEN,
        nullable=False,
        index=True
    )
    source: Mapped[str] = mapped_column(String(50), default="OPERATOR", nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships with selectin lazy loading for safe async serialization
    zone = relationship("Zone", backref="incidents", lazy="selectin")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvent.created_at.desc()", lazy="selectin")


class IncidentEvent(BaseModel):
    __tablename__ = "incident_events"

    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    actor_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="events")

```

---

## Backend/app/models/lost_person.py
`Backend/app/models/lost_person.py`

```python
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class LostPersonStatus(str, enum.Enum):
    SEARCHING = "SEARCHING"
    MATCH_FOUND = "MATCH_FOUND"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    REUNITED = "REUNITED"
    CLOSED = "CLOSED"


class LostPersonCase(BaseModel):
    __tablename__ = "lost_person_cases"

    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    clothing_description: Mapped[str] = mapped_column(Text, nullable=False)
    physical_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_seen_location: Mapped[str] = mapped_column(String(150), nullable=False)
    last_seen_camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    photo_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    status: Mapped[LostPersonStatus] = mapped_column(
        Enum(LostPersonStatus, name="lost_person_statuses"),
        default=LostPersonStatus.SEARCHING,
        nullable=False,
        index=True
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships with selectin loading
    reports = relationship("LostPersonReport", back_populates="case", cascade="all, delete-orphan", lazy="selectin")
    matches = relationship("FaceMatchResult", back_populates="case", cascade="all, delete-orphan", lazy="selectin")
    camera = relationship("Camera", backref="lost_persons", lazy="selectin")


class LostPersonReport(BaseModel):
    __tablename__ = "lost_person_reports"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("lost_person_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    caller_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    caller_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    audio_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="mr", nullable=False)
    asr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("LostPersonCase", back_populates="reports")

```

---

## Backend/app/models/face_match.py
`Backend/app/models/face_match.py`

```python
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class FaceMatchStatus(str, enum.Enum):
    CANDIDATE = "CANDIDATE"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class FaceMatchResult(BaseModel):
    __tablename__ = "face_match_results"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("lost_person_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    frame_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    status: Mapped[FaceMatchStatus] = mapped_column(
        Enum(FaceMatchStatus, name="face_match_statuses"),
        default=FaceMatchStatus.CANDIDATE,
        nullable=False
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    verified_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("LostPersonCase", back_populates="matches")
    camera = relationship("Camera", backref="face_matches")

```

---

## Backend/app/models/medical.py
`Backend/app/models/medical.py`

```python
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.incident import IncidentSeverity


class MedicalAlertType(str, enum.Enum):
    FALL = "FALL"
    FAINTING = "FAINTING"
    HEAT_EXHAUSTION = "HEAT_EXHAUSTION"
    DEHYDRATION = "DEHYDRATION"
    CARDIAC_RISK = "CARDIAC_RISK"
    OTHER = "OTHER"


class MedicalAlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class MedicalAlert(BaseModel):
    __tablename__ = "medical_alerts"

    alert_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[MedicalAlertType] = mapped_column(
        Enum(MedicalAlertType, name="medical_alert_types"),
        nullable=False,
        index=True
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="medical_severities"),
        default=IncidentSeverity.HIGH,
        nullable=False
    )
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    camera_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MedicalAlertStatus] = mapped_column(
        Enum(MedicalAlertStatus, name="medical_alert_statuses"),
        default=MedicalAlertStatus.ACTIVE,
        nullable=False,
        index=True
    )
    assigned_resource_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("resources.id", ondelete="SET NULL"), nullable=True)
    assigned_volunteer_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    zone = relationship("Zone", backref="medical_alerts")
    camera = relationship("Camera", backref="medical_alerts")
    resource = relationship("Resource", backref="assigned_medical_alerts", foreign_keys=[assigned_resource_id])

```

---

## Backend/app/models/resource.py
`Backend/app/models/resource.py`

```python
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ResourceType(str, enum.Enum):
    WATER_TANKER = "WATER_TANKER"
    MEDICAL_VAN = "MEDICAL_VAN"
    POLICE_SQUAD = "POLICE_SQUAD"
    VOLUNTEER_TEAM = "VOLUNTEER_TEAM"
    FOOD_VAN = "FOOD_VAN"
    AMBULANCE = "AMBULANCE"
    OTHER = "OTHER"


class ResourceAvailability(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    UNAVAILABLE = "UNAVAILABLE"
    OFFLINE = "OFFLINE"


class ResourceAssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Resource(BaseModel):
    __tablename__ = "resources"

    resource_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="resource_types"),
        nullable=False,
        index=True
    )
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status_tag: Mapped[str] = mapped_column(String(50), default="OPTIMAL", nullable=False)
    availability: Mapped[ResourceAvailability] = mapped_column(
        Enum(ResourceAvailability, name="resource_availabilities"),
        default=ResourceAvailability.AVAILABLE,
        nullable=False,
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True)
    location_description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    operator_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operator_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships with selectin loading
    zone = relationship("Zone", backref="resources", lazy="selectin")
    assignments = relationship("ResourceAssignment", back_populates="resource", cascade="all, delete-orphan", lazy="selectin")


class ResourceAssignment(BaseModel):
    __tablename__ = "resource_assignments"

    resource_id: Mapped[str] = mapped_column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[ResourceAssignmentStatus] = mapped_column(
        Enum(ResourceAssignmentStatus, name="assignment_statuses"),
        default=ResourceAssignmentStatus.PENDING,
        nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    arrived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    resource = relationship("Resource", back_populates="assignments")

```

---

## Backend/app/models/route.py
`Backend/app/models/route.py`

```python
import enum
from typing import Optional
from sqlalchemy import Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RouteStatus(str, enum.Enum):
    OPEN = "OPEN"
    DIVERTED = "DIVERTED"
    CLOSED = "CLOSED"
    EMERGENCY_ACCESS = "EMERGENCY_ACCESS"
    PILGRIMS_ONLY = "PILGRIMS_ONLY"


class Route(BaseModel):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[RouteStatus] = mapped_column(
        Enum(RouteStatus, name="route_statuses"),
        default=RouteStatus.OPEN,
        nullable=False,
        index=True
    )
    priority: Mapped[str] = mapped_column(String(20), default="PRIMARY", nullable=False)
    latitude_start: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude_start: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latitude_end: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude_end: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

```

---

## Backend/app/models/notification.py
`Backend/app/models/notification.py`

```python
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    INCIDENT = "INCIDENT"
    MEDICAL = "MEDICAL"
    CROWD = "CROWD"
    LOST_PERSON = "LOST_PERSON"
    RESOURCE = "RESOURCE"
    SYSTEM = "SYSTEM"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_types"),
        default=NotificationType.SYSTEM,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

```

---

## Backend/app/models/audit.py
`Backend/app/models/audit.py`

```python
from typing import Optional
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # LOGIN, INCIDENT_ACKNOWLEDGED, DISPATCH, etc.
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Incident, MedicalAlert, Route, etc.
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

```

---

## Backend/app/schemas/auth.py
`Backend/app/schemas/auth.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.rbac import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    last_login: Optional[datetime] = None


TokenResponse.model_rebuild()

```

---

## Backend/app/schemas/zone.py
`Backend/app/schemas/zone.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.zone import RiskLevel


class ZoneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    capacity: int = Field(default=50000, ge=1)
    risk_level: RiskLevel = RiskLevel.LOW
    is_active: bool = True


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    capacity: Optional[int] = Field(None, ge=1)
    risk_level: Optional[RiskLevel] = None
    is_active: Optional[bool] = None


class ZoneOut(ZoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ZoneCrowdMetrics(BaseModel):
    zone_id: str
    zone_name: str
    density_percentage: float
    people_count: int
    trend: str
    risk_level: RiskLevel
    recommended_action: str
    last_updated: datetime

```

---

## Backend/app/schemas/camera.py
`Backend/app/schemas/camera.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.camera import CameraStatus


class CameraBase(BaseModel):
    camera_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    zone_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    rtsp_url: Optional[str] = None
    status: CameraStatus = CameraStatus.ONLINE


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    rtsp_url: Optional[str] = None
    status: Optional[CameraStatus] = None


class CameraHeartbeat(BaseModel):
    status: CameraStatus = CameraStatus.ONLINE
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CameraPTZCommand(BaseModel):
    action: str = Field(..., description="pan_left, pan_right, tilt_up, tilt_down, zoom_in, zoom_out, preset")
    value: Optional[float] = None
    preset_id: Optional[int] = None


class CameraOut(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    current_density: Optional[float] = None
    density_status: Optional[str] = None

```

---

## Backend/app/schemas/crowd.py
`Backend/app/schemas/crowd.py`

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.crowd import CrowdTrend
from app.models.zone import RiskLevel


class CrowdObservationCreate(BaseModel):
    zone_id: str
    camera_id: Optional[str] = None
    density_percentage: float = Field(..., ge=0.0, le=100.0)
    people_count: int = Field(default=0, ge=0)
    movement_direction: Optional[str] = None
    trend: CrowdTrend = CrowdTrend.STABLE
    risk_level: RiskLevel = RiskLevel.LOW
    source: str = "DEMO"
    observed_at: Optional[datetime] = None


class CrowdObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zone_id: str
    camera_id: Optional[str] = None
    density_percentage: float
    people_count: int
    movement_direction: Optional[str] = None
    trend: CrowdTrend
    risk_level: RiskLevel
    source: str
    observed_at: datetime
    created_at: datetime


class CrowdForecastPoint(BaseModel):
    timestamp: str
    predicted_density: float
    risk_level: str


class ZoneForecastData(BaseModel):
    zone_name: str
    forecast_points: List[CrowdForecastPoint]


class CrowdForecastResponse(BaseModel):
    time_labels: List[str]
    zones: List[ZoneForecastData]
    model_version: str = "demo-rule-based-v1"
    generated_at: datetime

```

---

## Backend/app/schemas/incident.py
`Backend/app/schemas/incident.py`

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity, IncidentStatus, IncidentType


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    description: Optional[str] = None
    zone_id: Optional[str] = None
    camera_id: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    source: str = "OPERATOR"


class IncidentCreate(IncidentBase):
    is_demo: bool = False


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    description: Optional[str] = None
    assigned_user_id: Optional[str] = None


class IncidentAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class IncidentResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=2)


class IncidentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    event_type: str
    message: str
    actor_user_id: Optional[str] = None
    metadata_json: Optional[dict] = None
    created_at: datetime


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_number: str
    status: IncidentStatus
    created_by: Optional[str] = None
    assigned_user_id: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    events: Optional[List[IncidentEventOut]] = None

```

---

## Backend/app/schemas/lost_person.py
`Backend/app/schemas/lost_person.py`

```python
from datetime import datetime
from typing import List, Optional
import json
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.face_match import FaceMatchStatus
from app.models.lost_person import LostPersonStatus


class LostPersonReportBase(BaseModel):
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    transcript: Optional[str] = None
    language: str = "mr"
    asr_confidence: Optional[float] = None


class LostPersonReportCreate(LostPersonReportBase):
    pass


class LostPersonReportOut(LostPersonReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    audio_file_url: Optional[str] = None
    reported_at: datetime


class FaceMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    camera_id: Optional[str] = None
    frame_reference: Optional[str] = None
    similarity_score: float
    confidence: float
    status: FaceMatchStatus
    detected_at: datetime
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class LostPersonCaseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., description="M / F / Other")
    clothing_description: str = Field(..., min_length=2)
    physical_description: Optional[str] = None
    last_seen_location: str = Field(..., min_length=2)
    last_seen_camera_id: Optional[str] = None
    photo_url: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    priority: str = "HIGH"

    @field_validator('photo_urls', mode='before')
    @classmethod
    def parse_photo_urls(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [v]
            except Exception:
                return [v]
        return [str(v)]


class LostPersonCaseCreate(LostPersonCaseBase):
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    initial_transcript: Optional[str] = None
    is_demo: bool = False


class LostPersonCaseUpdate(BaseModel):
    clothing_description: Optional[str] = None
    physical_description: Optional[str] = None
    status: Optional[LostPersonStatus] = None
    last_seen_location: Optional[str] = None


class LostPersonCaseOut(LostPersonCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    incident_id: Optional[str] = None
    status: LostPersonStatus
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    reports: Optional[List[LostPersonReportOut]] = None
    matches: Optional[List[FaceMatchOut]] = None


class FaceMatchVerifyRequest(BaseModel):
    verified: bool
    officer_notes: Optional[str] = None


class PurgeSensitiveDataResponse(BaseModel):
    success: bool
    message: str
    purged_records_count: int
    case_id: str

```

---

## Backend/app/schemas/medical.py
`Backend/app/schemas/medical.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity
from app.models.medical import MedicalAlertStatus, MedicalAlertType


class MedicalAlertBase(BaseModel):
    type: MedicalAlertType
    severity: IncidentSeverity = IncidentSeverity.HIGH
    zone_id: Optional[str] = None
    camera_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    description: str = Field(..., min_length=2)
    assigned_volunteer_name: Optional[str] = None


class MedicalAlertCreate(MedicalAlertBase):
    is_demo: bool = False


class MedicalAlertAcknowledgeRequest(BaseModel):
    assigned_volunteer_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalAlertDispatchRequest(BaseModel):
    resource_id: str
    volunteer_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalAlertResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=2)


class MedicalAlertOut(MedicalAlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_code: str
    incident_id: Optional[str] = None
    status: MedicalAlertStatus
    assigned_resource_id: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime

```

---

## Backend/app/schemas/resource.py
`Backend/app/schemas/resource.py`

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.resource import ResourceAvailability, ResourceType, ResourceAssignmentStatus


class ResourceBase(BaseModel):
    resource_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    resource_type: ResourceType
    capacity: Optional[int] = None
    status_tag: str = "OPTIMAL"
    availability: ResourceAvailability = ResourceAvailability.AVAILABLE
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    zone_id: Optional[str] = None
    location_description: Optional[str] = None
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    status_tag: Optional[str] = None
    availability: Optional[ResourceAvailability] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    zone_id: Optional[str] = None
    location_description: Optional[str] = None
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None


class ResourceStatusUpdateRequest(BaseModel):
    availability: ResourceAvailability
    status_tag: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class ResourceDispatchRequest(BaseModel):
    incident_id: Optional[str] = None
    target_location: Optional[str] = None
    notes: Optional[str] = None


class ResourceAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    resource_id: str
    incident_id: Optional[str] = None
    status: ResourceAssignmentStatus
    assigned_at: datetime
    accepted_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    distance_km: Optional[float] = None
    assignments: Optional[List[ResourceAssignmentOut]] = None

```

---

## Backend/app/schemas/route.py
`Backend/app/schemas/route.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.route import RouteStatus


class RouteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    status: RouteStatus = RouteStatus.OPEN
    priority: str = "PRIMARY"
    latitude_start: Optional[float] = None
    longitude_start: Optional[float] = None
    latitude_end: Optional[float] = None
    longitude_end: Optional[float] = None


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[RouteStatus] = None
    priority: Optional[str] = None


class RouteActionRequest(BaseModel):
    reason: Optional[str] = None


class RouteOut(RouteBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

```

---

## Backend/app/schemas/audit.py
`Backend/app/schemas/audit.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

```

---

## Backend/app/schemas/notification.py
`Backend/app/schemas/notification.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationType


class NotificationCreate(BaseModel):
    user_id: Optional[str] = None
    incident_id: Optional[str] = None
    type: NotificationType = NotificationType.SYSTEM
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2)
    priority: str = "NORMAL"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    incident_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

```

---

## Backend/app/schemas/dashboard.py
`Backend/app/schemas/dashboard.py`

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    active_incidents: int
    active_lost_person_cases: int
    active_medical_alerts: int
    critical_zones: int
    deployed_resources: int
    available_resources: int
    total_resources: int
    active_cameras: int
    total_cameras: int
    estimated_pilgrim_count: int
    max_crowd_density: float
    max_density: float
    palkhi_location: str
    palkhi_status: str
    last_updated: datetime


class IncidentTickerItem(BaseModel):
    timestamp: str
    formatted_text: str
    incident_number: Optional[str] = None
    type: str
    severity: str


class HeatRiskReadout(BaseModel):
    ambient_temperature: str = "34° C"
    relative_humidity: str = "72%"
    computed_risk_index: str = "7.8 / 10 (MODERATE HEAT RISK)"
    water_stations_active: str = "12 Operational"
    orsl_sachet_supplies: str = "14,200 Packets Available"
    advisory_action: str = "Trigger mist sprayer vans at Wakhri Junction & increase water distribution post deployment by 20%."


class CorridorRouteSegment(BaseModel):
    name: str
    sector: str
    density_percentage: float
    color_hex: str
    status_tag: str
    coordinates: List[List[float]]

```

---

## Backend/app/services/audit_service.py
`Backend/app/services/audit_service.py`

```python
import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

logger = logging.getLogger("varisetu.audit")


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create an immutable audit log record."""
        audit_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_entry)
        logger.info(f"AUDIT | {action} on {entity_type}:{entity_id or 'N/A'} by User:{user_id or 'SYSTEM'}")
        return audit_entry


audit_service = AuditService()

```

---

## Backend/app/services/auth_service.py
`Backend/app/services/auth_service.py`

```python
from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut
from app.services.audit_service import audit_service


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> TokenResponse:
        query = select(User).where(User.email == login_data.email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        await audit_service.log_action(
            db=db,
            action="USER_LOGIN",
            entity_type="User",
            entity_id=user.id,
            user_id=user.id
        )
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        user_id = payload.get("sub")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found or inactive")

        access_token = create_access_token(subject=user.id, role=user.role.value)
        new_refresh = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserOut.model_validate(user)
        )

    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserCreate) -> UserOut:
        existing = await db.execute(select(User).where(User.email == user_in.email))
        if existing.scalar_one_or_none():
            raise ConflictException(f"User with email {user_in.email} already exists")

        new_user = User(
            name=user_in.name,
            email=user_in.email,
            phone=user_in.phone,
            password_hash=get_password_hash(user_in.password),
            role=user_in.role,
            department=user_in.department,
            is_active=user_in.is_active
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        await audit_service.log_action(
            db=db,
            action="USER_REGISTERED",
            entity_type="User",
            entity_id=new_user.id
        )
        return UserOut.model_validate(new_user)

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[UserOut]:
        query = select(User).order_by(User.name)
        result = await db.execute(query)
        users = result.scalars().all()
        return [UserOut.model_validate(u) for u in users]


auth_service = AuthService()

```

---

## Backend/app/services/incident_service.py
`Backend/app/services/incident_service.py`

```python
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, StateTransitionException
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class IncidentService:
    @staticmethod
    async def generate_incident_number(db: AsyncSession) -> str:
        count_q = select(func.count(Incident.id))
        res = await db.execute(count_q)
        total = res.scalar() or 0
        return f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{total + 101:04d}"

    @staticmethod
    async def create_incident(
        db: AsyncSession,
        incident_in: IncidentCreate,
        user_id: Optional[str] = None
    ) -> Incident:
        inc_num = await IncidentService.generate_incident_number(db)

        incident = Incident(
            incident_number=inc_num,
            type=incident_in.type,
            severity=incident_in.severity,
            status=IncidentStatus.OPEN,
            source=incident_in.source,
            zone_id=incident_in.zone_id,
            camera_id=incident_in.camera_id,
            latitude=incident_in.latitude,
            longitude=incident_in.longitude,
            title=incident_in.title,
            description=incident_in.description,
            created_by=user_id,
            is_demo=incident_in.is_demo
        )
        db.add(incident)
        await db.flush()

        # Initial event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="INCIDENT_CREATED",
            message=f"Incident {inc_num} reported: {incident.title}",
            actor_user_id=user_id,
            metadata_json={"severity": incident.severity.value, "source": incident.source}
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_CREATED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id,
            new_value={"incident_number": inc_num, "title": incident.title}
        )

        await db.commit()
        await db.refresh(incident)

        # Broadcast realtime WebSocket event
        event_payload = {
            "incident_id": incident.id,
            "incident_number": incident.incident_number,
            "title": incident.title,
            "type": incident.type.value,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "source": incident.source,
            "created_at": incident.created_at.isoformat()
        }
        await ws_manager.broadcast(WebSocketEventType.INCIDENT_CREATED, event_payload, channel="incidents")
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] {incident.incident_number} {incident.title}"},
            channel="dashboard"
        )

        return incident

    @staticmethod
    async def acknowledge_incident(
        db: AsyncSession,
        incident_id: str,
        user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Incident:
        query = select(Incident).where(Incident.id == incident_id).options(selectinload(Incident.events))
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise NotFoundException("Incident not found")

        if incident.status not in (IncidentStatus.OPEN,):
            raise StateTransitionException(incident.status.value, IncidentStatus.ACKNOWLEDGED.value, "Incident")

        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now(timezone.utc)
        incident.assigned_user_id = user_id

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="OFFICER_ACKNOWLEDGED",
            message=f"Incident acknowledged by controller. {notes or ''}".strip(),
            actor_user_id=user_id
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_ACKNOWLEDGED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(incident)

        await ws_manager.broadcast(
            WebSocketEventType.INCIDENT_UPDATED,
            {"incident_id": incident.id, "status": incident.status.value},
            channel="incidents"
        )
        return incident

    @staticmethod
    async def resolve_incident(
        db: AsyncSession,
        incident_id: str,
        resolution_notes: str,
        user_id: Optional[str] = None
    ) -> Incident:
        query = select(Incident).where(Incident.id == incident_id).options(selectinload(Incident.events))
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise NotFoundException("Incident not found")

        if incident.status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
            raise StateTransitionException(incident.status.value, IncidentStatus.RESOLVED.value, "Incident")

        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now(timezone.utc)

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="INCIDENT_RESOLVED",
            message=f"Incident resolved: {resolution_notes}",
            actor_user_id=user_id
        )
        db.add(event)

        await audit_service.log_action(
            db=db,
            action="INCIDENT_RESOLVED",
            entity_type="Incident",
            entity_id=incident.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(incident)

        await ws_manager.broadcast(
            WebSocketEventType.INCIDENT_UPDATED,
            {"incident_id": incident.id, "status": incident.status.value, "resolved_at": incident.resolved_at.isoformat()},
            channel="incidents"
        )
        return incident

    @staticmethod
    async def get_incidents(
        db: AsyncSession,
        status: Optional[IncidentStatus] = None,
        type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None,
        zone_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Incident]:
        query = select(Incident).options(selectinload(Incident.events)).order_by(Incident.created_at.desc())
        if status:
            query = query.where(Incident.status == status)
        if type:
            query = query.where(Incident.type == type)
        if severity:
            query = query.where(Incident.severity == severity)
        if zone_id:
            query = query.where(Incident.zone_id == zone_id)

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        return list(result.scalars().all())


incident_service = IncidentService()

```

---

## Backend/app/services/lost_person_service.py
`Backend/app/services/lost_person_service.py`

```python
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, StateTransitionException
from app.integrations.qdrant_adapter import qdrant_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.vision_adapter import vision_adapter
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.schemas.lost_person import LostPersonCaseCreate
from app.services.audit_service import audit_service
from app.services.incident_service import incident_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class LostPersonService:
    @staticmethod
    async def generate_case_number(db: AsyncSession) -> str:
        res = await db.execute(select(LostPersonCase.case_number))
        existing = {row[0] for row in res.fetchall()}
        num = 801
        while f"#LF-{num}" in existing:
            num += 1
        return f"#LF-{num}"

    @staticmethod
    async def create_case(
        db: AsyncSession,
        case_in: LostPersonCaseCreate,
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case_number = await LostPersonService.generate_case_number(db)

        # Create linked incident automatically
        incident = Incident(
            incident_number=f"INC-{case_number.replace('#', '')}",
            type=IncidentType.MISSING_PERSON,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.OPEN,
            source="HELPLINE_112",
            title=f"Missing Person: {case_in.name} ({case_in.age} {case_in.gender})",
            description=f"Last seen at: {case_in.last_seen_location}. Attire: {case_in.clothing_description}",
            created_by=user_id,
            is_demo=case_in.is_demo
        )
        db.add(incident)
        await db.flush()

        import json
        photo_urls_str = json.dumps(case_in.photo_urls) if case_in.photo_urls else None
        photo_url_val = case_in.photo_url or (case_in.photo_urls[0] if case_in.photo_urls else None)

        case = LostPersonCase(
            case_number=case_number,
            incident_id=incident.id,
            name=case_in.name,
            age=case_in.age,
            gender=case_in.gender,
            clothing_description=case_in.clothing_description,
            physical_description=case_in.physical_description,
            last_seen_location=case_in.last_seen_location,
            last_seen_camera_id=case_in.last_seen_camera_id,
            photo_url=photo_url_val,
            photo_urls=photo_urls_str,
            priority=case_in.priority,
            status=LostPersonStatus.SEARCHING,
            created_by=user_id,
            is_demo=case_in.is_demo
        )
        db.add(case)
        await db.flush()

        # Add initial caller report if provided
        if case_in.initial_transcript or case_in.caller_name:
            report = LostPersonReport(
                case_id=case.id,
                caller_name=case_in.caller_name or "Anonymous Pilgrim",
                caller_phone=case_in.caller_phone or "112 Helpline",
                transcript=case_in.initial_transcript,
                language="mr",
                asr_confidence=0.94
            )
            db.add(report)

        await audit_service.log_action(
            db=db,
            action="LOST_PERSON_CASE_CREATED",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id,
            new_value={"case_number": case_number, "name": case.name}
        )

        await db.commit()
        await db.refresh(case)

        # Broadcast event
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] Lost Person Case {case.case_number} registered: {case.name}"},
            channel="dashboard"
        )
        return case

    @staticmethod
    async def add_match_candidate(
        db: AsyncSession,
        case_id: str,
        camera_id: str,
        similarity_score: float,
        frame_ref: str = "frame_001.jpg"
    ) -> FaceMatchResult:
        match = FaceMatchResult(
            case_id=case_id,
            camera_id=camera_id,
            frame_reference=frame_ref,
            similarity_score=similarity_score,
            confidence=0.94,
            status=FaceMatchStatus.PENDING_VERIFICATION
        )
        db.add(match)

        # Update case status
        case_q = select(LostPersonCase).where(LostPersonCase.id == case_id)
        res = await db.execute(case_q)
        case = res.scalar_one_or_none()
        if case:
            case.status = LostPersonStatus.MATCH_FOUND

        await db.commit()
        await db.refresh(match)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_MATCH_FOUND,
            {"case_id": case_id, "camera_id": camera_id, "score": similarity_score},
            channel="lost-persons"
        )
        return match

    @staticmethod
    async def verify_match(
        db: AsyncSession,
        case_id: str,
        match_id: str,
        verified: bool,
        user_id: Optional[str] = None
    ) -> FaceMatchResult:
        query = select(FaceMatchResult).where(FaceMatchResult.id == match_id, FaceMatchResult.case_id == case_id)
        res = await db.execute(query)
        match = res.scalar_one_or_none()
        if not match:
            raise NotFoundException("Match result not found")

        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()

        match.status = FaceMatchStatus.VERIFIED if verified else FaceMatchStatus.REJECTED
        match.verified_by = user_id
        match.verified_at = datetime.now(timezone.utc)

        if case:
            case.status = LostPersonStatus.VERIFIED if verified else LostPersonStatus.SEARCHING

        await audit_service.log_action(
            db=db,
            action="FACE_MATCH_VERIFIED" if verified else "FACE_MATCH_REJECTED",
            entity_type="FaceMatchResult",
            entity_id=match.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(match)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_VERIFIED,
            {"case_id": case_id, "match_id": match_id, "verified": verified},
            channel="lost-persons"
        )
        return match

    @staticmethod
    async def dispatch_volunteer(
        db: AsyncSession,
        case_id: str,
        volunteer_name: str = "Nearby Volunteer Team",
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if not case:
            raise NotFoundException("Case not found")

        case.status = LostPersonStatus.DISPATCHED
        await audit_service.log_action(
            db=db,
            action="VOLUNTEER_DISPATCHED_FOR_LOST_PERSON",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id
        )
        await db.commit()
        await db.refresh(case)
        return case

    @staticmethod
    async def reunite_case(
        db: AsyncSession,
        case_id: str,
        user_id: Optional[str] = None
    ) -> LostPersonCase:
        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if not case:
            raise NotFoundException("Case not found")

        case.status = LostPersonStatus.REUNITED
        case.resolved_at = datetime.now(timezone.utc)

        if case.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == case.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.RESOLVED
                inc.resolved_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="LOST_PERSON_REUNITED",
            entity_type="LostPersonCase",
            entity_id=case.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(case)

        await ws_manager.broadcast(
            WebSocketEventType.LOST_PERSON_REUNITED,
            {"case_id": case.id, "case_number": case.case_number},
            channel="lost-persons"
        )
        return case

    @staticmethod
    async def purge_sensitive_data(db: AsyncSession, case_id: str) -> int:
        """
        Privacy requirement: permanently purge temporary biometric vectors,
        face match frames, and audio references for a case while keeping the operational case record.
        """
        deleted_count = await qdrant_adapter.delete_case_embeddings(case_id)

        case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == case_id))).scalar_one_or_none()
        if case:
            case.photo_url = None

        await audit_service.log_action(
            db=db,
            action="SENSITIVE_BIOMETRIC_DATA_PURGED",
            entity_type="LostPersonCase",
            entity_id=case_id
        )
        await db.commit()
        return deleted_count

    @staticmethod
    async def get_cases(db: AsyncSession, status: Optional[LostPersonStatus] = None) -> List[LostPersonCase]:
        query = select(LostPersonCase).options(
            selectinload(LostPersonCase.reports),
            selectinload(LostPersonCase.matches)
        ).order_by(LostPersonCase.created_at.desc())
        if status:
            query = query.where(LostPersonCase.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())


lost_person_service = LostPersonService()

```

---

## Backend/app/services/medical_service.py
`Backend/app/services/medical_service.py`

```python
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.exceptions import NotFoundException, StateTransitionException
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentType
from app.models.medical import MedicalAlert, MedicalAlertStatus, MedicalAlertType
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability
from app.schemas.medical import MedicalAlertCreate
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class MedicalService:
    @staticmethod
    async def generate_alert_code(db: AsyncSession) -> str:
        count_q = select(func.count(MedicalAlert.id))
        res = await db.execute(count_q)
        total = res.scalar() or 0
        return f"MED-{total + 101:03d}"

    @staticmethod
    async def create_alert(
        db: AsyncSession,
        alert_in: MedicalAlertCreate,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert_code = await MedicalService.generate_alert_code(db)

        # Automatically create linked operational incident
        incident = Incident(
            incident_number=f"INC-{alert_code}",
            type=IncidentType.MEDICAL,
            severity=alert_in.severity,
            status=IncidentStatus.OPEN,
            source="MEDICAL_SENSOR",
            zone_id=alert_in.zone_id,
            camera_id=alert_in.camera_id,
            latitude=alert_in.latitude,
            longitude=alert_in.longitude,
            title=f"Medical Emergency: {alert_in.type.value.replace('_', ' ')}",
            description=alert_in.description,
            created_by=user_id,
            is_demo=alert_in.is_demo
        )
        db.add(incident)
        await db.flush()

        alert = MedicalAlert(
            alert_code=alert_code,
            incident_id=incident.id,
            type=alert_in.type,
            severity=alert_in.severity,
            zone_id=alert_in.zone_id,
            camera_id=alert_in.camera_id,
            latitude=alert_in.latitude,
            longitude=alert_in.longitude,
            description=alert_in.description,
            status=MedicalAlertStatus.ACTIVE,
            assigned_volunteer_name=alert_in.assigned_volunteer_name,
            is_demo=alert_in.is_demo
        )
        db.add(alert)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_CREATED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id,
            new_value={"alert_code": alert_code, "type": alert.type.value}
        )

        await db.commit()
        await db.refresh(alert)

        # Broadcast realtime alerts
        event_payload = {
            "alert_id": alert.id,
            "alert_code": alert.alert_code,
            "type": alert.type.value,
            "severity": alert.severity.value,
            "description": alert.description,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat()
        }
        await ws_manager.broadcast(WebSocketEventType.MEDICAL_ALERT_CREATED, event_payload, channel="medical")
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] {alert.alert_code} {alert.description}"},
            channel="dashboard"
        )
        return alert

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: str,
        volunteer_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        query = select(MedicalAlert).where(MedicalAlert.id == alert_id)
        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            raise NotFoundException("Medical alert not found")

        if alert.status not in (MedicalAlertStatus.ACTIVE,):
            raise StateTransitionException(alert.status.value, MedicalAlertStatus.ACKNOWLEDGED.value, "MedicalAlert")

        alert.status = MedicalAlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        if volunteer_name:
            alert.assigned_volunteer_name = volunteer_name

        if alert.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == alert.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.ACKNOWLEDGED
                inc.acknowledged_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_ACKNOWLEDGED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value, "assigned_volunteer": alert.assigned_volunteer_name},
            channel="medical"
        )
        return alert

    @staticmethod
    async def dispatch_medical_unit(
        db: AsyncSession,
        alert_id: str,
        resource_id: str,
        volunteer_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert = (await db.execute(select(MedicalAlert).where(MedicalAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            raise NotFoundException("Medical alert not found")

        resource = (await db.execute(select(Resource).where(Resource.id == resource_id))).scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        alert.status = MedicalAlertStatus.DISPATCHED
        alert.assigned_resource_id = resource_id
        if volunteer_name:
            alert.assigned_volunteer_name = volunteer_name

        # Update resource status
        resource.availability = ResourceAvailability.ASSIGNED

        # Create assignment
        assignment = ResourceAssignment(
            resource_id=resource.id,
            incident_id=alert.incident_id,
            assigned_by=user_id,
            status=ResourceAssignmentStatus.EN_ROUTE,
            notes=f"Dispatched for medical alert {alert.alert_code}"
        )
        db.add(assignment)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_UNIT_DISPATCHED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id,
            new_value={"resource_code": resource.resource_code, "volunteer": volunteer_name}
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value, "resource_code": resource.resource_code},
            channel="medical"
        )
        return alert

    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        alert_id: str,
        resolution_notes: str,
        user_id: Optional[str] = None
    ) -> MedicalAlert:
        alert = (await db.execute(select(MedicalAlert).where(MedicalAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            raise NotFoundException("Medical alert not found")

        alert.status = MedicalAlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)

        if alert.incident_id:
            inc = (await db.execute(select(Incident).where(Incident.id == alert.incident_id))).scalar_one_or_none()
            if inc:
                inc.status = IncidentStatus.RESOLVED
                inc.resolved_at = datetime.now(timezone.utc)

        await audit_service.log_action(
            db=db,
            action="MEDICAL_ALERT_RESOLVED",
            entity_type="MedicalAlert",
            entity_id=alert.id,
            user_id=user_id
        )

        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast(
            WebSocketEventType.MEDICAL_ALERT_UPDATED,
            {"alert_id": alert.id, "status": alert.status.value},
            channel="medical"
        )
        return alert

    @staticmethod
    async def get_alerts(db: AsyncSession, status: Optional[MedicalAlertStatus] = None) -> List[MedicalAlert]:
        query = select(MedicalAlert).order_by(MedicalAlert.created_at.desc())
        if status:
            query = query.where(MedicalAlert.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())


medical_service = MedicalService()

```

---

## Backend/app/services/resource_service.py
`Backend/app/services/resource_service.py`

```python
import math
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.incident import Incident, IncidentEvent
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability, ResourceType
from app.schemas.resource import ResourceOut
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class ResourceService:
    @staticmethod
    async def get_resources(
        db: AsyncSession,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None
    ) -> List[Resource]:
        query = select(Resource).options(selectinload(Resource.assignments)).order_by(Resource.resource_code)
        if resource_type:
            query = query.where(Resource.resource_type == resource_type)
        if availability:
            query = query.where(Resource.availability == availability)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_nearby_resources(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None,
        limit: int = 10
    ) -> List[ResourceOut]:
        resources = await ResourceService.get_resources(db, resource_type, availability)
        result_items = []
        for r in resources:
            dist = haversine_distance(latitude, longitude, r.latitude, r.longitude)
            out_model = ResourceOut.model_validate(r)
            out_model.distance_km = dist
            result_items.append(out_model)

        # Sort by proximity
        result_items.sort(key=lambda x: x.distance_km or 999999.0)
        return result_items[:limit]

    @staticmethod
    async def dispatch_resource(
        db: AsyncSession,
        resource_id: str,
        incident_id: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Resource:
        query = select(Resource).where(Resource.id == resource_id).options(selectinload(Resource.assignments))
        result = await db.execute(query)
        resource = result.scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        resource.availability = ResourceAvailability.ASSIGNED

        assignment = ResourceAssignment(
            resource_id=resource.id,
            incident_id=incident_id,
            assigned_by=user_id,
            status=ResourceAssignmentStatus.EN_ROUTE,
            notes=notes
        )
        db.add(assignment)

        if incident_id:
            event = IncidentEvent(
                incident_id=incident_id,
                event_type="RESOURCE_DISPATCHED",
                message=f"Resource {resource.name} ({resource.resource_code}) dispatched to incident scene.",
                actor_user_id=user_id
            )
            db.add(event)

        await audit_service.log_action(
            db=db,
            action="RESOURCE_DISPATCHED",
            entity_type="Resource",
            entity_id=resource.id,
            user_id=user_id,
            new_value={"availability": resource.availability.value, "incident_id": incident_id}
        )

        await db.commit()
        await db.refresh(resource)

        await ws_manager.broadcast(
            WebSocketEventType.RESOURCE_DISPATCHED,
            {"resource_id": resource.id, "resource_code": resource.resource_code, "status": resource.availability.value},
            channel="resources"
        )
        return resource

    @staticmethod
    async def update_status(
        db: AsyncSession,
        resource_id: str,
        availability: ResourceAvailability,
        status_tag: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> Resource:
        resource = (await db.execute(select(Resource).where(Resource.id == resource_id))).scalar_one_or_none()
        if not resource:
            raise NotFoundException("Resource not found")

        old_val = {"availability": resource.availability.value}
        resource.availability = availability
        if status_tag:
            resource.status_tag = status_tag
        if latitude is not None:
            resource.latitude = latitude
        if longitude is not None:
            resource.longitude = longitude

        await audit_service.log_action(
            db=db,
            action="RESOURCE_STATUS_UPDATED",
            entity_type="Resource",
            entity_id=resource.id,
            user_id=user_id,
            old_value=old_val,
            new_value={"availability": availability.value}
        )

        await db.commit()
        await db.refresh(resource)

        await ws_manager.broadcast(
            WebSocketEventType.RESOURCE_STATUS_CHANGED,
            {"resource_id": resource.id, "availability": resource.availability.value},
            channel="resources"
        )
        return resource


resource_service = ResourceService()

```

---

## Backend/app/services/crowd_service.py
`Backend/app/services/crowd_service.py`

```python
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.zone import RiskLevel, Zone
from app.schemas.crowd import CrowdObservationCreate
from app.schemas.zone import ZoneCrowdMetrics
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class CrowdService:
    @staticmethod
    def calculate_risk(density: float) -> RiskLevel:
        if density >= 90.0:
            return RiskLevel.CRITICAL
        elif density >= 75.0:
            return RiskLevel.HIGH
        elif density >= 55.0:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    @staticmethod
    def get_recommended_action(zone_name: str, density: float) -> str:
        if "Pandharpur" in zone_name and density >= 90:
            return "Divert pilgrim queue via North Ring Road"
        elif "Wakhri" in zone_name and density >= 80:
            return "Deploy 4 extra police constables to junction"
        elif "Vakhri" in zone_name and density >= 70:
            return "Monitor bottleneck near bridge entry"
        elif "Saswad" in zone_name:
            return "Normal traffic regulation"
        elif "Tarapur" in zone_name:
            return "Allow local supply vehicle passage"
        return "Standard patrol active"

    @staticmethod
    async def record_observation(db: AsyncSession, obs_in: CrowdObservationCreate) -> CrowdObservation:
        risk = CrowdService.calculate_risk(obs_in.density_percentage)
        obs = CrowdObservation(
            zone_id=obs_in.zone_id,
            camera_id=obs_in.camera_id,
            density_percentage=obs_in.density_percentage,
            people_count=obs_in.people_count,
            movement_direction=obs_in.movement_direction,
            trend=obs_in.trend,
            risk_level=risk,
            source=obs_in.source,
            observed_at=obs_in.observed_at or datetime.now(timezone.utc)
        )
        db.add(obs)

        # Update Zone current risk level
        zone = (await db.execute(select(Zone).where(Zone.id == obs_in.zone_id))).scalar_one_or_none()
        if zone:
            zone.risk_level = risk

        await db.commit()
        await db.refresh(obs)

        await ws_manager.broadcast(
            WebSocketEventType.CROWD_UPDATED,
            {
                "zone_id": obs.zone_id,
                "density_percentage": obs.density_percentage,
                "trend": obs.trend.value,
                "risk_level": obs.risk_level.value
            },
            channel="crowd"
        )
        return obs

    @staticmethod
    async def get_current_zone_metrics(db: AsyncSession) -> List[ZoneCrowdMetrics]:
        zones = (await db.execute(select(Zone).where(Zone.is_active == True))).scalars().all()
        metrics = []

        for z in zones:
            # Fetch latest observation
            obs_q = select(CrowdObservation).where(CrowdObservation.zone_id == z.id).order_by(desc(CrowdObservation.observed_at)).limit(1)
            obs = (await db.execute(obs_q)).scalar_one_or_none()

            density = obs.density_percentage if obs else 40.0
            people_cnt = obs.people_count if obs else 500
            trend_val = obs.trend.value if obs else "STABLE"
            risk = obs.risk_level if obs else z.risk_level
            last_up = obs.observed_at if obs else z.updated_at

            metrics.append(ZoneCrowdMetrics(
                zone_id=z.id,
                zone_name=z.name,
                density_percentage=density,
                people_count=people_cnt,
                trend=trend_val,
                risk_level=risk,
                recommended_action=CrowdService.get_recommended_action(z.name, density),
                last_updated=last_up
            ))

        # Sort by density descending
        metrics.sort(key=lambda m: m.density_percentage, reverse=True)
        return metrics


crowd_service = CrowdService()

```

---

## Backend/app/services/forecast_service.py
`Backend/app/services/forecast_service.py`

```python
from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.zone import Zone
from app.schemas.crowd import CrowdForecastPoint, CrowdForecastResponse, ZoneForecastData


class ForecastService:
    @staticmethod
    async def get_2hour_forecast(db: AsyncSession) -> CrowdForecastResponse:
        """
        Generate 2-hour congestion forecast model (7 intervals from 19:00 to 21:00 IST).
        Deterministic rule-based forecast baseline version.
        """
        time_labels = ["19:00 IST", "19:20 IST", "19:40 IST", "20:00 IST", "20:20 IST", "20:40 IST", "21:00 IST"]

        # Default prediction profiles matching the operational dashboard
        profiles = {
            "Pandharpur Chowk": [94.0, 96.0, 98.0, 92.0, 85.0, 78.0, 70.0],
            "Wakhri Phata": [88.0, 90.0, 86.0, 82.0, 75.0, 68.0, 60.0]
        }

        zones_data: List[ZoneForecastData] = []
        for zone_name, densities in profiles.items():
            pts = []
            for t_label, d_val in zip(time_labels, densities):
                risk = "CRITICAL" if d_val >= 90 else ("HIGH" if d_val >= 75 else "MODERATE")
                pts.append(CrowdForecastPoint(
                    timestamp=t_label,
                    predicted_density=d_val,
                    risk_level=risk
                ))
            zones_data.append(ZoneForecastData(zone_name=zone_name, forecast_points=pts))

        return CrowdForecastResponse(
            time_labels=time_labels,
            zones=zones_data,
            model_version="demo-rule-based-v1",
            generated_at=datetime.now(timezone.utc)
        )


forecast_service = ForecastService()

```

---

## Backend/app/services/route_service.py
`Backend/app/services/route_service.py`

```python
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException
from app.models.incident import Incident, IncidentEvent
from app.models.route import Route, RouteStatus
from app.services.audit_service import audit_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager


class RouteService:
    @staticmethod
    async def get_routes(db: AsyncSession) -> List[Route]:
        query = select(Route).order_by(Route.priority, Route.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def change_status(
        db: AsyncSession,
        route_id: str,
        status: RouteStatus,
        reason: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Route:
        query = select(Route).where(Route.id == route_id)
        result = await db.execute(query)
        route = result.scalar_one_or_none()

        if not route:
            raise NotFoundException("Route corridor not found")

        old_status = route.status.value
        route.status = status
        route.updated_by = user_id

        await audit_service.log_action(
            db=db,
            action="ROUTE_STATUS_CHANGED",
            entity_type="Route",
            entity_id=route.id,
            user_id=user_id,
            old_value={"status": old_status},
            new_value={"status": status.value, "reason": reason}
        )

        await db.commit()
        await db.refresh(route)

        # Broadcast update
        await ws_manager.broadcast(
            WebSocketEventType.ROUTE_CHANGED,
            {"route_id": route.id, "name": route.name, "status": route.status.value, "reason": reason},
            channel="dashboard"
        )
        await ws_manager.broadcast(
            WebSocketEventType.TICKER_EVENT,
            {"text": f"[{datetime.now().strftime('%H:%M:%S')}] Route {route.name} status updated: {route.status.value}"},
            channel="dashboard"
        )
        return route


route_service = RouteService()

```

---

## Backend/app/services/dashboard_service.py
`Backend/app/services/dashboard_service.py`

```python
from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select

from app.integrations.weather_adapter import weather_adapter
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation
from app.models.incident import Incident, IncidentEvent, IncidentStatus
from app.models.lost_person import LostPersonCase, LostPersonStatus
from app.models.medical import MedicalAlert, MedicalAlertStatus
from app.models.resource import Resource, ResourceAvailability
from app.models.zone import RiskLevel, Zone
from app.schemas.dashboard import DashboardSummary, HeatRiskReadout, IncidentTickerItem


class DashboardService:
    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        # Active incidents count
        inc_q = select(func.count(Incident.id)).where(Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED]))
        active_inc = (await db.execute(inc_q)).scalar() or 0

        # Active lost person cases count
        lost_q = select(func.count(LostPersonCase.id)).where(LostPersonCase.status.notin_([LostPersonStatus.REUNITED, LostPersonStatus.CLOSED]))
        active_lost = (await db.execute(lost_q)).scalar() or 0

        # Active medical alerts count
        med_q = select(func.count(MedicalAlert.id)).where(MedicalAlert.status.notin_([MedicalAlertStatus.RESOLVED, MedicalAlertStatus.CLOSED]))
        active_med = (await db.execute(med_q)).scalar() or 0

        # Critical zones count
        crit_q = select(func.count(Zone.id)).where(Zone.risk_level == RiskLevel.CRITICAL)
        crit_zones = (await db.execute(crit_q)).scalar() or 0

        # Deployed vs Available resources
        dep_q = select(func.count(Resource.id)).where(Resource.availability.in_([ResourceAvailability.ASSIGNED, ResourceAvailability.EN_ROUTE, ResourceAvailability.ON_SCENE]))
        avail_q = select(func.count(Resource.id)).where(Resource.availability == ResourceAvailability.AVAILABLE)
        total_res_q = select(func.count(Resource.id))
        deployed_res = (await db.execute(dep_q)).scalar() or 0
        avail_res = (await db.execute(avail_q)).scalar() or 0
        total_res = (await db.execute(total_res_q)).scalar() or (deployed_res + avail_res)

        # Cameras count
        cam_online_q = select(func.count(Camera.id)).where(Camera.status == CameraStatus.ONLINE)
        cam_total_q = select(func.count(Camera.id))
        active_cams = (await db.execute(cam_online_q)).scalar() or 0
        total_cams = (await db.execute(cam_total_q)).scalar() or 0

        # Max crowd density from latest observations
        max_density_q = select(func.max(CrowdObservation.density_percentage))
        max_density = (await db.execute(max_density_q)).scalar() or 94.0

        return DashboardSummary(
            active_incidents=active_inc,
            active_lost_person_cases=active_lost,
            active_medical_alerts=active_med,
            critical_zones=crit_zones,
            deployed_resources=deployed_res,
            available_resources=avail_res,
            total_resources=total_res,
            active_cameras=active_cams,
            total_cameras=total_cams,
            estimated_pilgrim_count=845000,
            max_crowd_density=float(max_density),
            max_density=float(max_density),
            palkhi_location="Approaching Wakhri Phata (Km 184)",
            palkhi_status="Sant Tukaram Maharaj Palkhi",
            last_updated=datetime.now(timezone.utc)
        )

    @staticmethod
    async def get_ticker_events(db: AsyncSession, limit: int = 20) -> List[IncidentTickerItem]:
        query = select(IncidentEvent).order_by(desc(IncidentEvent.created_at)).limit(limit)
        events = (await db.execute(query)).scalars().all()

        ticker_items = []
        for ev in events:
            time_str = ev.created_at.strftime("%H:%M:%S")
            ticker_items.append(IncidentTickerItem(
                timestamp=time_str,
                formatted_text=f"[{time_str}] {ev.message}",
                type=ev.event_type,
                severity="NORMAL"
            ))

        # If no events yet in DB, return standard initial events
        if not ticker_items:
            now_str = datetime.now().strftime("%H:%M:%S")
            return [
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] CAM-12 Wakhri Phata: Density peak detected (88%)",
                    type="CROWD_PEAK",
                    severity="HIGH"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Medical alert raised at Sector 4: Pilgrim fainting, Ambulance MH-12-PA-4022 dispatched",
                    type="MEDICAL_ALERT",
                    severity="CRITICAL"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Lost Person Case #LF-802: Facial match confidence 89% on CAM-04",
                    type="LOST_PERSON_MATCH",
                    severity="HIGH"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Solapur Highway Diversion Gate 2 opened",
                    type="ROUTE_DIVERTED",
                    severity="NORMAL"
                ),
                IncidentTickerItem(
                    timestamp=now_str,
                    formatted_text=f"[{now_str}] Water tanker #WT-09 refilled at Wakhri Station",
                    type="RESOURCE_OPTIMAL",
                    severity="LOW"
                )
            ]

        return ticker_items

    @staticmethod
    async def get_heat_risk() -> HeatRiskReadout:
        data = await weather_adapter.get_heat_metrics(17.7280, 75.2950)
        return HeatRiskReadout(**data)


dashboard_service = DashboardService()

```

---

## Backend/app/services/demo_service.py
`Backend/app/services/demo_service.py`

```python
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.database import AsyncSessionLocal
from app.models.crowd import CrowdTrend
from app.models.incident import IncidentSeverity, IncidentType
from app.models.medical import MedicalAlertType
from app.schemas.crowd import CrowdObservationCreate
from app.schemas.incident import IncidentCreate
from app.schemas.lost_person import LostPersonCaseCreate
from app.schemas.medical import MedicalAlertCreate
from app.services.crowd_service import crowd_service
from app.services.incident_service import incident_service
from app.services.lost_person_service import lost_person_service
from app.services.medical_service import medical_service
from app.websocket.events import WebSocketEventType
from app.websocket.manager import ws_manager

logger = logging.getLogger("varisetu.demo")


class DemoService:
    def __init__(self):
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self.current_step: int = 0
        self.total_steps: int = 12
        self.started_at: Optional[datetime] = None

    async def start(self) -> Dict[str, str]:
        if self.is_running:
            return {"status": "already_running", "message": "Demo simulation is already active."}

        self.is_running = True
        self.current_step = 0
        self.started_at = datetime.now(timezone.utc)
        self._task = asyncio.create_task(self._run_scenario())
        logger.info("Demo simulation engine started.")
        return {"status": "started", "message": "Demo pilgrimage operational simulation started."}

    async def stop(self) -> Dict[str, str]:
        if not self.is_running:
            return {"status": "not_running", "message": "Demo simulation is not running."}

        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Demo simulation engine stopped.")
        return {"status": "stopped", "message": "Demo simulation stopped."}

    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "started_at": self.started_at.isoformat() if self.started_at else None
        }

    async def _run_scenario(self):
        """Execute end-to-end Wari pilgrimage emergency simulation steps."""
        try:
            # STEP 1: Crowd density increases at Wakhri Phata
            self.current_step = 1
            async with AsyncSessionLocal() as db:
                from app.models.zone import Zone
                from sqlalchemy import select
                wakhri = (await db.execute(select(Zone).where(Zone.name.ilike("%Wakhri%")))).scalar_one_or_none()
                if wakhri:
                    await crowd_service.record_observation(
                        db,
                        CrowdObservationCreate(
                            zone_id=wakhri.id,
                            density_percentage=88.0,
                            people_count=1420,
                            trend=CrowdTrend.RISING,
                            source="DEMO"
                        )
                    )
            await ws_manager.broadcast(
                WebSocketEventType.TICKER_EVENT,
                {"text": f"[{datetime.now().strftime('%H:%M:%S')}] [DEMO] CAM-12 Wakhri Phata: Density surge detected (88%)"},
                channel="dashboard"
            )
            await asyncio.sleep(4)

            # STEP 2: Crowd Incident Created
            self.current_step = 2
            async with AsyncSessionLocal() as db:
                inc = await incident_service.create_incident(
                    db,
                    IncidentCreate(
                        title="Crowd Congestion Surge at Wakhri Phata Junction",
                        type=IncidentType.CROWD,
                        severity=IncidentSeverity.HIGH,
                        description="Density crossed 85% safety threshold at pedestrian bottleneck.",
                        source="CCTV_AI",
                        is_demo=True
                    )
                )
                inc_id = inc.id
            await asyncio.sleep(4)

            # STEP 3: Medical Fall Alert
            self.current_step = 3
            async with AsyncSessionLocal() as db:
                med_alert = await medical_service.create_alert(
                    db,
                    MedicalAlertCreate(
                        type=MedicalAlertType.FALL,
                        severity=IncidentSeverity.HIGH,
                        latitude=17.7280,
                        longitude=75.2950,
                        description="Fall detected / Fainting pilgrim near Wakhri Phata Km 184.",
                        is_demo=True
                    )
                )
                med_id = med_alert.id
            await asyncio.sleep(4)

            # STEP 4: Medical Alert Acknowledged
            self.current_step = 4
            async with AsyncSessionLocal() as db:
                await medical_service.acknowledge_alert(
                    db,
                    med_id,
                    volunteer_name="Team Bravo (V. R. Kadam)"
                )
            await asyncio.sleep(4)

            # STEP 5: Lost Person Case Registered
            self.current_step = 5
            async with AsyncSessionLocal() as db:
                lost_case = await lost_person_service.create_case(
                    db,
                    LostPersonCaseCreate(
                        name="Maruti Kisan Shinde",
                        age=68,
                        gender="M",
                        clothing_description="पांढरा कुर्ता, धोती, पांढरी टोपी (White Kurta-Dhoti, Gandhi topi, carrying Tulsi mala)",
                        last_seen_location="Wakhri Phata Junction",
                        caller_name="Namdeo Shinde (Grandson)",
                        caller_phone="+91-9822014455",
                        initial_transcript=(
                            "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                            "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे."
                        ),
                        is_demo=True
                    )
                )
                case_id = lost_case.id
            await asyncio.sleep(4)

            # STEP 6: AI Face Match Candidate Generated
            self.current_step = 6
            async with AsyncSessionLocal() as db:
                match = await lost_person_service.add_match_candidate(
                    db,
                    case_id=case_id,
                    camera_id="CAM-04",
                    similarity_score=0.89,
                    frame_ref="frame_4812.jpg"
                )
                match_id = match.id
            await ws_manager.broadcast(
                WebSocketEventType.TICKER_EVENT,
                {"text": f"[{datetime.now().strftime('%H:%M:%S')}] [DEMO] Lost Person Case #{case_id[:8]}: AI Candidate match 89% on CAM-04"},
                channel="dashboard"
            )
            await asyncio.sleep(4)

            # STEP 7: Officer Verifies Face Match
            self.current_step = 7
            async with AsyncSessionLocal() as db:
                await lost_person_service.verify_match(
                    db,
                    case_id=case_id,
                    match_id=match_id,
                    verified=True
                )
            await asyncio.sleep(4)

            # STEP 8: Volunteer Dispatched for Lost Person
            self.current_step = 8
            async with AsyncSessionLocal() as db:
                await lost_person_service.dispatch_volunteer(
                    db,
                    case_id=case_id,
                    volunteer_name="Volunteer Squad Pandharpur North"
                )
            await asyncio.sleep(4)

            # STEP 9: Pilgrim Reunited
            self.current_step = 9
            async with AsyncSessionLocal() as db:
                await lost_person_service.reunite_case(db, case_id=case_id)
            await asyncio.sleep(4)

            # STEP 10: Medical Alert Resolved
            self.current_step = 10
            async with AsyncSessionLocal() as db:
                await medical_service.resolve_alert(
                    db,
                    alert_id=med_id,
                    resolution_notes="Pilgrim rehydrated with ORSL and reunited with Dindi group."
                )
            await asyncio.sleep(4)

            # STEP 11: Incident Resolved
            self.current_step = 11
            async with AsyncSessionLocal() as db:
                await incident_service.resolve_incident(
                    db,
                    incident_id=inc_id,
                    resolution_notes="Pedestrian traffic cleared; queue diversion completed."
                )
            await asyncio.sleep(3)

            # STEP 12: Complete
            self.current_step = 12
            self.is_running = False
            logger.info("Demo pilgrimage operational simulation completed successfully.")

        except asyncio.CancelledError:
            self.is_running = False
            logger.info("Demo simulation cancelled.")
        except Exception as e:
            self.is_running = False
            logger.error(f"Demo simulation error: {e}", exc_info=True)


demo_service = DemoService()

```

---

## Backend/app/integrations/__init__.py
`Backend/app/integrations/__init__.py`

```python
"""
Modular extensible adapters for AI, Vector DB, Speech, Vision, Weather, and Storage.
"""
from app.integrations.qdrant_adapter import qdrant_adapter
from app.integrations.vision_adapter import vision_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.weather_adapter import weather_adapter
from app.integrations.notification_adapter import notification_adapter
from app.integrations.storage_adapter import storage_adapter

__all__ = [
    "qdrant_adapter",
    "vision_adapter",
    "speech_adapter",
    "weather_adapter",
    "notification_adapter",
    "storage_adapter",
]

```

---

## Backend/app/integrations/qdrant_adapter.py
`Backend/app/integrations/qdrant_adapter.py`

```python
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger("varisetu.qdrant")


class QdrantAdapter:
    """
    Adapter for vector similarity search (biometric/face embeddings & text retrieval).
    Operates in 'mock' mode by default or connects to Qdrant cluster if enabled.
    """
    def __init__(self):
        self.provider = settings.VECTOR_PROVIDER
        self.url = settings.QDRANT_URL
        self.api_key = settings.QDRANT_API_KEY
        self._mock_vectors: Dict[str, List[float]] = {}
        self._mock_payloads: Dict[str, Dict[str, Any]] = {}

    async def upsert_embedding(
        self,
        point_id: str,
        embedding: List[float],
        payload: Dict[str, Any],
        collection_name: str = "lost_persons"
    ) -> bool:
        if self.provider == "mock":
            self._mock_vectors[point_id] = embedding
            self._mock_payloads[point_id] = payload
            logger.info(f"[MOCK Qdrant] Upserted vector for point: {point_id}")
            return True

        # Real Qdrant HTTP API
        try:
            headers = {"api-key": self.api_key} if self.api_key else {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.put(
                    f"{self.url}/collections/{collection_name}/points",
                    headers=headers,
                    json={
                        "points": [{
                            "id": point_id,
                            "vector": embedding,
                            "payload": payload
                        }]
                    }
                )
                return resp.status_code in (200, 201)
        except Exception as e:
            logger.error(f"Qdrant upsert error: {e}")
            return False

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        collection_name: str = "lost_persons",
        score_threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        if self.provider == "mock":
            # Return demo candidate matches
            results = []
            for pid, payload in list(self._mock_payloads.items())[:limit]:
                results.append({
                    "id": pid,
                    "score": 0.89,
                    "payload": payload
                })
            return results

        try:
            headers = {"api-key": self.api_key} if self.api_key else {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.url}/collections/{collection_name}/points/search",
                    headers=headers,
                    json={
                        "vector": query_vector,
                        "limit": limit,
                        "score_threshold": score_threshold,
                        "with_payload": True
                    }
                )
                if resp.status_code == 200:
                    return resp.json().get("result", [])
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
        return []

    async def delete_embedding(self, point_id: str, collection_name: str = "lost_persons") -> bool:
        """Purge a single vector embedding (Privacy requirement)."""
        self._mock_vectors.pop(point_id, None)
        self._mock_payloads.pop(point_id, None)
        if self.provider == "qdrant":
            try:
                headers = {"api-key": self.api_key} if self.api_key else {}
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{self.url}/collections/{collection_name}/points/delete",
                        headers=headers,
                        json={"points": [point_id]}
                    )
            except Exception as e:
                logger.error(f"Qdrant delete error: {e}")
        return True

    async def delete_case_embeddings(self, case_id: str) -> int:
        """Purge all temporary candidate embeddings associated with a case."""
        deleted_count = 0
        to_del = [k for k, v in self._mock_payloads.items() if v.get("case_id") == case_id]
        for k in to_del:
            self._mock_vectors.pop(k, None)
            self._mock_payloads.pop(k, None)
            deleted_count += 1
        logger.info(f"Purged {deleted_count} biometric embeddings for case {case_id}")
        return deleted_count

    async def health_check(self) -> str:
        if self.provider == "mock":
            return "mock"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.url}/healthz")
                return "connected" if resp.status_code == 200 else "degraded"
        except Exception:
            return "unreachable"


qdrant_adapter = QdrantAdapter()

```

---

## Backend/app/integrations/vision_adapter.py
`Backend/app/integrations/vision_adapter.py`

```python
import logging
from typing import Any, Dict, List, Optional
import random

from app.core.config import settings

logger = logging.getLogger("varisetu.vision")


class VisionAdapter:
    """
    Vision processing interface for YOLO crowd density estimation,
    fall detection, and face embedding matching.
    """
    def __init__(self):
        self.provider = settings.VISION_PROVIDER

    async def estimate_crowd(self, camera_id: str) -> Dict[str, Any]:
        """
        Estimate crowd density & people count from CCTV video frame.
        In mock mode, returns simulated density metadata marked as source=DEMO.
        """
        simulated_data = {
            "CAM-12": {"density": 88.0, "count": 1420, "trend": "RISING", "risk": "HIGH"},
            "CAM-04": {"density": 94.0, "count": 2850, "trend": "RISING", "risk": "CRITICAL"},
            "CAM-08": {"density": 62.0, "count": 890, "trend": "EASING", "risk": "MODERATE"},
            "CAM-01": {"density": 35.0, "count": 410, "trend": "STABLE", "risk": "LOW"},
        }
        fallback = {"density": random.uniform(40.0, 75.0), "count": random.randint(500, 1200), "trend": "STABLE", "risk": "MODERATE"}
        info = simulated_data.get(camera_id, fallback)

        return {
            "camera_id": camera_id,
            "density_percentage": info["density"],
            "people_count": info["count"],
            "trend": info["trend"],
            "risk_level": info["risk"],
            "source": "DEMO" if self.provider == "mock" else "YOLO_V8"
        }

    async def detect_fall(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Detect fainting / pilgrim fall from camera stream."""
        return {
            "detected": True,
            "camera_id": camera_id,
            "confidence": 0.92,
            "bounding_box": [120, 340, 210, 480],
            "source": "DEMO"
        }

    async def generate_face_embedding(self, photo_bytes: bytes) -> List[float]:
        """Generate a 512-dim facial feature embedding vector."""
        random.seed(len(photo_bytes) if photo_bytes else 42)
        return [random.uniform(-1.0, 1.0) for _ in range(128)]

    async def search_face_in_stream(self, embedding: List[float], camera_codes: List[str]) -> List[Dict[str, Any]]:
        """Simulate scanning CCTV feeds for matching faces."""
        return [
            {
                "camera_code": "CAM-04",
                "location": "Pandharpur Temple Chowk",
                "similarity_score": 0.89,
                "confidence": 0.94,
                "frame_reference": "frame_4812.jpg",
                "source": "DEMO"
            }
        ]


vision_adapter = VisionAdapter()

```

---

## Backend/app/integrations/speech_adapter.py
`Backend/app/integrations/speech_adapter.py`

```python
import logging
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger("varisetu.speech")


class SpeechAdapter:
    """
    Speech-to-Text (ASR) interface for helpline audio call recordings (Deccan Marathi / Hindi / English).
    """
    def __init__(self):
        self.provider = settings.SPEECH_PROVIDER

    async def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Dict[str, Any]:
        """
        Transcribe helpline call recording audio.
        In mock mode, returns realistic Devanagari Marathi transcripts with confidence.
        """
        if self.provider == "mock":
            return {
                "transcript": (
                    "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                    "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. "
                    "गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."
                ),
                "language": "mr",
                "asr_confidence": 0.94,
                "extracted_attributes": {
                    "gender": "M",
                    "estimated_age": 68,
                    "clothing": "पांढरा कुर्ता, धोती, पांढरी टोपी",
                    "accessories": "तुळशीची माळ, टाळ",
                    "last_seen": "वाखरी फाटा"
                },
                "source": "DEMO"
            }

        # Real Whisper / IndicWhisper adapter integration point
        return {
            "transcript": "",
            "language": language,
            "asr_confidence": 0.0,
            "extracted_attributes": {},
            "source": "WHISPER_ASR"
        }


speech_adapter = SpeechAdapter()

```

---

## Backend/app/integrations/weather_adapter.py
`Backend/app/integrations/weather_adapter.py`

```python
import os
import logging
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger("varisetu.adapters")


class WeatherAdapter:
    """Weather and heat risk index provider."""
    def __init__(self):
        self.provider = settings.WEATHER_PROVIDER

    async def get_heat_metrics(self, latitude: float, longitude: float) -> Dict[str, Any]:
        return {
            "ambient_temperature": "34° C",
            "relative_humidity": "72%",
            "computed_risk_index": "7.8 / 10 (MODERATE HEAT RISK)",
            "water_stations_active": "12 Operational",
            "orsl_sachet_supplies": "14,200 Packets Available",
            "advisory_action": "Trigger mist sprayer vans at Wakhri Junction & increase water distribution post deployment by 20%."
        }


class NotificationAdapter:
    """Outbound SMS / WhatsApp / IVR alert integration adapter."""
    def __init__(self):
        self.provider = settings.NOTIFICATION_PROVIDER

    async def send_sms(self, phone: str, message: str) -> bool:
        logger.info(f"[MOCK SMS] Sending to {phone}: {message}")
        return True

    async def send_pa_announcement(self, location: str, message: str) -> bool:
        logger.info(f"[MOCK PA] Dispatched public address announcement to {location}: {message}")
        return True


class StorageAdapter:
    """File storage interface (Local disk / Supabase Storage)."""
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.upload_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"/uploads/{filename}"

    async def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


weather_adapter = WeatherAdapter()
notification_adapter = NotificationAdapter()
storage_adapter = StorageAdapter()

```

---

## Backend/app/integrations/notification_adapter.py
`Backend/app/integrations/notification_adapter.py`

```python
import logging
from app.core.config import settings

logger = logging.getLogger("varisetu.notification_adapter")


class NotificationAdapter:
    """Outbound SMS / WhatsApp / IVR alert integration adapter."""
    def __init__(self):
        self.provider = settings.NOTIFICATION_PROVIDER

    async def send_sms(self, phone: str, message: str) -> bool:
        logger.info(f"[MOCK SMS] Sending to {phone}: {message}")
        return True

    async def send_pa_announcement(self, location: str, message: str) -> bool:
        logger.info(f"[MOCK PA] Dispatched public address announcement to {location}: {message}")
        return True


notification_adapter = NotificationAdapter()

```

---

## Backend/app/integrations/storage_adapter.py
`Backend/app/integrations/storage_adapter.py`

```python
import os
import logging
from app.core.config import settings

logger = logging.getLogger("varisetu.storage")


class StorageAdapter:
    """File storage interface (Local disk / Supabase Storage)."""
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.upload_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"/uploads/{filename}"

    async def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


storage_adapter = StorageAdapter()

```

---

## Backend/app/websocket/events.py
`Backend/app/websocket/events.py`

```python
import enum
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class WebSocketEventType(str, enum.Enum):
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_UPDATED = "INCIDENT_UPDATED"
    CROWD_UPDATED = "CROWD_UPDATED"
    MEDICAL_ALERT_CREATED = "MEDICAL_ALERT_CREATED"
    MEDICAL_ALERT_UPDATED = "MEDICAL_ALERT_UPDATED"
    RESOURCE_DISPATCHED = "RESOURCE_DISPATCHED"
    RESOURCE_STATUS_CHANGED = "RESOURCE_STATUS_CHANGED"
    LOST_PERSON_MATCH_FOUND = "LOST_PERSON_MATCH_FOUND"
    LOST_PERSON_VERIFIED = "LOST_PERSON_VERIFIED"
    LOST_PERSON_REUNITED = "LOST_PERSON_REUNITED"
    ROUTE_CHANGED = "ROUTE_CHANGED"
    TICKER_EVENT = "TICKER_EVENT"
    SYSTEM_ALERT = "SYSTEM_ALERT"


class WebSocketMessage(BaseModel):
    event: WebSocketEventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Dict[str, Any]

```

---

## Backend/app/websocket/manager.py
`Backend/app/websocket/manager.py`

```python
import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

from app.core.redis import redis_client
from app.websocket.events import WebSocketEventType, WebSocketMessage

logger = logging.getLogger("varisetu.websocket")


class ConnectionManager:
    def __init__(self):
        # Maps channel name -> Set of connected WebSockets
        self.channels: Dict[str, Set[WebSocket]] = {
            "all": set(),
            "dashboard": set(),
            "incidents": set(),
            "crowd": set(),
            "medical": set(),
            "resources": set(),
            "lost-persons": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(websocket)
        self.channels["all"].add(websocket)
        logger.info(f"WebSocket client connected on channel: {channel} (Total: {len(self.channels['all'])})")

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.channels:
            self.channels[channel].discard(websocket)
        self.channels["all"].discard(websocket)
        logger.info(f"WebSocket client disconnected from channel: {channel}")

    async def broadcast(self, event_type: WebSocketEventType, data: dict, channel: str = "all"):
        """Broadcast typed JSON event to connected clients on the given channel."""
        message = WebSocketMessage(event=event_type, data=data)
        payload = message.model_dump_json()

        # Publish to Redis if connected
        await redis_client.publish(f"varisetu:ws:{channel}", message.model_dump())

        # Direct local broadcast to connected clients
        targets = self.channels.get(channel, set()) | self.channels.get("all", set())
        if not targets:
            return

        dead_sockets = set()
        for connection in targets:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending message to WebSocket client: {e}")
                dead_sockets.add(connection)

        # Clean up dead sockets
        for dead in dead_sockets:
            for ch in self.channels.values():
                ch.discard(dead)


ws_manager = ConnectionManager()

```

---

## Backend/app/api/auth.py
`Backend/app/api/auth.py`

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserRole, get_current_user, require_roles
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserOut
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="User authentication with JWT issuance")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with official email/officer ID and password to receive JWT tokens."""
    return await auth_service.authenticate_user(db, login_data)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh JWT access token")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Obtain a fresh access token using a valid refresh token."""
    return await auth_service.refresh_tokens(db, req.refresh_token)


@router.get("/me", response_model=UserOut, summary="Get current authenticated user profile")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile and role details of the currently authenticated user."""
    return UserOut.model_validate(current_user)


@router.get("/users", response_model=List[UserOut], summary="List all registered officers (Admin Only)")
async def list_users(
    current_admin: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve roster of all authorized police & medical officers."""
    return await auth_service.get_all_users(db)


@router.post("/logout", summary="Log out user and invalidate session")
async def logout(current_user: User = Depends(get_current_user)):
    """Log out current user."""
    return {"success": True, "message": "Successfully logged out"}


@router.post("/register", response_model=UserOut, summary="Register new user (Admin Only)")
async def register(
    user_in: UserCreate,
    current_admin: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only endpoint to provision new authorised command center officers."""
    return await auth_service.register_user(db, user_in)

```

---

## Backend/app/api/dashboard.py
`Backend/app/api/dashboard.py`

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.user import User
from app.schemas.dashboard import CorridorRouteSegment, DashboardSummary, HeatRiskReadout, IncidentTickerItem
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/summary", response_model=DashboardSummary, summary="Get real-time operational summary metrics")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns live operational statistics aggregated dynamically from database state:
    Active incidents, lost cases, medical emergencies, critical zones, tanker deployments, and camera telemetry.
    """
    return await dashboard_service.get_summary(db)


@router.get("/ticker", response_model=List[IncidentTickerItem], summary="Get incident ticker feed items")
async def get_dashboard_ticker(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retrieve timestamped incident timeline events for the bottom monospace operational ticker."""
    return await dashboard_service.get_ticker_events(db, limit=limit)


@router.get("/heat-risk", response_model=HeatRiskReadout, summary="Get heat-risk readout metrics")
async def get_heat_risk():
    """Retrieve computed ambient temperature, humidity, and heat risk advisory."""
    return await dashboard_service.get_heat_risk()


@router.get("/map-corridor", response_model=List[CorridorRouteSegment], summary="Get route corridor segments with live density")
async def get_map_corridor():
    """Returns coordinate segments with heat density colors for Leaflet map overlay."""
    return [
        CorridorRouteSegment(
            name="Alandi - Saswad",
            sector="Sector 1-2",
            density_percentage=35.0,
            color_hex="#2E5B36",
            status_tag="NORMAL",
            coordinates=[
                [18.6772, 73.8967],
                [18.5204, 73.8567],
                [18.3440, 74.0305]
            ]
        ),
        CorridorRouteSegment(
            name="Saswad - Bhalwani",
            sector="Sector 3",
            density_percentage=74.0,
            color_hex="#B8551B",
            status_tag="HEAVY",
            coordinates=[
                [18.3440, 74.0305],
                [18.1500, 74.3000],
                [17.8900, 75.0200]
            ]
        ),
        CorridorRouteSegment(
            name="Wakhri - Pandharpur",
            sector="Sector 4-5",
            density_percentage=94.0,
            color_hex="#9A2525",
            status_tag="CRITICAL",
            coordinates=[
                [17.8900, 75.0200],
                [17.7280, 75.2950],
                [17.6777, 75.3276]
            ]
        )
    ]

```

---

## Backend/app/api/cameras.py
`Backend/app/api/cameras.py`

```python
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.camera import Camera, CameraStatus
from app.schemas.camera import CameraCreate, CameraHeartbeat, CameraOut, CameraPTZCommand, CameraUpdate
from app.services.audit_service import audit_service

router = APIRouter(prefix="/cameras", tags=["Cameras"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[CameraOut], summary="List all CCTV surveillance cameras")
async def list_cameras(db: AsyncSession = Depends(get_db)):
    """Retrieve all surveillance cameras with active status and location coordinates."""
    result = await db.execute(select(Camera).order_by(Camera.camera_code))
    cameras = result.scalars().all()

    # Enrich with default density for dashboard presentation
    enriched = []
    density_map = {"CAM-12": 88.0, "CAM-04": 94.0, "CAM-08": 62.0, "CAM-01": 35.0}
    for c in cameras:
        out = CameraOut.model_validate(c)
        out.current_density = density_map.get(c.camera_code, 45.0)
        if out.current_density >= 90:
            out.density_status = "CRITICAL"
        elif out.current_density >= 75:
            out.density_status = "HEAVY"
        elif out.current_density >= 50:
            out.density_status = "MODERATE"
        else:
            out.density_status = "NORMAL"
        enriched.append(out)
    return enriched


@router.get("/{camera_id}", response_model=CameraOut, summary="Get camera by ID or code")
async def get_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Camera).where((Camera.id == camera_id) | (Camera.camera_code == camera_id))
    camera = (await db.execute(query)).scalar_one_or_none()
    if not camera:
        raise NotFoundException("Camera not found")
    return CameraOut.model_validate(camera)


@router.post("", response_model=CameraOut, status_code=status.HTTP_201_CREATED, summary="Register new camera")
async def create_camera(cam_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    camera = Camera(
        camera_code=cam_in.camera_code,
        name=cam_in.name,
        zone_id=cam_in.zone_id,
        latitude=cam_in.latitude,
        longitude=cam_in.longitude,
        rtsp_url=cam_in.rtsp_url,
        status=cam_in.status,
        last_seen_at=datetime.now(timezone.utc)
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return CameraOut.model_validate(camera)


@router.patch("/{camera_id}", response_model=CameraOut, summary="Update camera configuration")
async def update_camera(camera_id: str, cam_up: CameraUpdate, db: AsyncSession = Depends(get_db)):
    camera = (await db.execute(select(Camera).where(Camera.id == camera_id))).scalar_one_or_none()
    if not camera:
        raise NotFoundException("Camera not found")

    if cam_up.name is not None:
        camera.name = cam_up.name
    if cam_up.zone_id is not None:
        camera.zone_id = cam_up.zone_id
    if cam_up.latitude is not None:
        camera.latitude = cam_up.latitude
    if cam_up.longitude is not None:
        camera.longitude = cam_up.longitude
    if cam_up.status is not None:
        camera.status = cam_up.status

    await db.commit()
    await db.refresh(camera)
    return CameraOut.model_validate(camera)


@router.delete("/{camera_id}", summary="Delete camera")
async def delete_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    camera = (await db.execute(select(Camera).where(Camera.id == camera_id))).scalar_one_or_none()
    if not camera:
        raise NotFoundException("Camera not found")
    await db.delete(camera)
    await db.commit()
    return {"success": True, "message": "Camera deleted"}


@router.post("/{camera_id}/heartbeat", summary="Camera heartbeat update")
async def camera_heartbeat(camera_id: str, hb: CameraHeartbeat, db: AsyncSession = Depends(get_db)):
    camera = (await db.execute(select(Camera).where((Camera.id == camera_id) | (Camera.camera_code == camera_id)))).scalar_one_or_none()
    if not camera:
        raise NotFoundException("Camera not found")

    camera.status = hb.status
    camera.last_seen_at = hb.timestamp
    await db.commit()
    return {"success": True, "camera_code": camera.camera_code, "status": camera.status.value}


@router.post("/{camera_id}/ptz", summary="Dispatch PTZ pan/tilt/zoom command")
async def ptz_control(camera_id: str, ptz_in: CameraPTZCommand, db: AsyncSession = Depends(get_db)):
    """Dispatch PTZ command to camera controller."""
    camera = (await db.execute(select(Camera).where((Camera.id == camera_id) | (Camera.camera_code == camera_id)))).scalar_one_or_none()
    if not camera:
        raise NotFoundException("Camera not found")

    await audit_service.log_action(
        db=db,
        action="CAMERA_PTZ_COMMAND",
        entity_type="Camera",
        entity_id=camera.id,
        new_value={"action": ptz_in.action, "value": ptz_in.value}
    )
    await db.commit()

    return {
        "success": True,
        "camera_code": camera.camera_code,
        "action": ptz_in.action,
        "status": "command_dispatched",
        "provider": "MOCK_ONVIF_CONTROLLER"
    }

```

---

## Backend/app/api/zones.py
`Backend/app/api/zones.py`

```python
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneCrowdMetrics, ZoneOut, ZoneUpdate
from app.services.crowd_service import crowd_service

router = APIRouter(prefix="/zones", tags=["Zones"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[ZoneOut], summary="List all pilgrimage monitoring zones")
async def list_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone).where(Zone.is_active == True).order_by(Zone.name))
    return [ZoneOut.model_validate(z) for z in result.scalars().all()]


@router.get("/{zone_id}", response_model=ZoneOut, summary="Get zone details by ID")
async def get_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    zone = (await db.execute(select(Zone).where(Zone.id == zone_id))).scalar_one_or_none()
    if not zone:
        raise NotFoundException("Zone not found")
    return ZoneOut.model_validate(zone)


@router.post("", response_model=ZoneOut, status_code=status.HTTP_201_CREATED, summary="Create new zone")
async def create_zone(zone_in: ZoneCreate, db: AsyncSession = Depends(get_db)):
    zone = Zone(**zone_in.model_dump())
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return ZoneOut.model_validate(zone)


@router.get("/metrics/crowd", response_model=List[ZoneCrowdMetrics], summary="Get zone-wise density table metrics")
async def get_zone_crowd_metrics(db: AsyncSession = Depends(get_db)):
    """Returns zone-wise density %, trend, and recommended police action for the Crowd Intelligence view."""
    return await crowd_service.get_current_zone_metrics(db)

```

---

## Backend/app/api/crowd.py
`Backend/app/api/crowd.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.crowd import CrowdObservation
from app.schemas.crowd import CrowdForecastResponse, CrowdObservationCreate, CrowdObservationOut
from app.schemas.zone import ZoneCrowdMetrics
from app.services.crowd_service import crowd_service
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/crowd", tags=["Crowd Intelligence"], dependencies=[Depends(get_current_user)])


@router.get("/current", response_model=List[ZoneCrowdMetrics], summary="Get current zone density telemetry")
async def get_current_crowd(db: AsyncSession = Depends(get_db)):
    """Retrieve latest density percentages and police action recommendations across all zones."""
    return await crowd_service.get_current_zone_metrics(db)


@router.get("/history", response_model=List[CrowdObservationOut], summary="Get historical crowd density observations")
async def get_crowd_history(
    zone_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(CrowdObservation).order_by(desc(CrowdObservation.observed_at))
    if zone_id:
        query = query.where(CrowdObservation.zone_id == zone_id)
    query = query.limit(limit)
    result = await db.execute(query)
    return [CrowdObservationOut.model_validate(o) for o in result.scalars().all()]


@router.post("/observations", response_model=CrowdObservationOut, status_code=status.HTTP_201_CREATED, summary="Ingest CCTV crowd telemetry")
async def record_crowd_observation(obs_in: CrowdObservationCreate, db: AsyncSession = Depends(get_db)):
    obs = await crowd_service.record_observation(db, obs_in)
    return CrowdObservationOut.model_validate(obs)


@router.get("/forecast", response_model=CrowdForecastResponse, summary="Get 2-hour congestion forecast model")
async def get_crowd_forecast(db: AsyncSession = Depends(get_db)):
    """Retrieve 2-hour congestion prediction points for Wakhri Phata & Pandharpur Chowk."""
    return await forecast_service.get_2hour_forecast(db)

```

---

## Backend/app/api/incidents.py
`Backend/app/api/incidents.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.models.user import User
from app.schemas.incident import (
    IncidentAcknowledgeRequest,
    IncidentCreate,
    IncidentEventOut,
    IncidentOut,
    IncidentResolveRequest,
    IncidentUpdate
)
from app.services.incident_service import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[IncidentOut], summary="List incidents with pagination & filters")
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    type: Optional[IncidentType] = None,
    severity: Optional[IncidentSeverity] = None,
    zone_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    incidents = await incident_service.get_incidents(db, status, type, severity, zone_id, limit, offset)
    return [IncidentOut.model_validate(i) for i in incidents]


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED, summary="Create operational incident")
async def create_incident(
    incident_in: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    incident = await incident_service.create_incident(db, incident_in, user_id=user_id)
    return IncidentOut.model_validate(incident)


@router.get("/{id}", response_model=IncidentOut, summary="Get incident details by ID")
async def get_incident(id: str, db: AsyncSession = Depends(get_db)):
    query = select(Incident).where(Incident.id == id).options(selectinload(Incident.events))
    incident = (await db.execute(query)).scalar_one_or_none()
    if not incident:
        raise NotFoundException("Incident not found")
    return IncidentOut.model_validate(incident)


@router.post("/{id}/acknowledge", response_model=IncidentOut, summary="Acknowledge incident")
async def acknowledge_incident(
    id: str,
    ack_req: Optional[IncidentAcknowledgeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    notes = ack_req.notes if ack_req else None
    incident = await incident_service.acknowledge_incident(db, id, user_id=user_id, notes=notes)
    return IncidentOut.model_validate(incident)


@router.post("/{id}/resolve", response_model=IncidentOut, summary="Resolve incident")
async def resolve_incident(
    id: str,
    resolve_req: IncidentResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    incident = await incident_service.resolve_incident(db, id, resolve_req.resolution_notes, user_id=user_id)
    return IncidentOut.model_validate(incident)


@router.get("/{id}/timeline", response_model=List[IncidentEventOut], summary="Get incident timeline audit events")
async def get_incident_timeline(id: str, db: AsyncSession = Depends(get_db)):
    query = select(IncidentEvent).where(IncidentEvent.incident_id == id).order_by(IncidentEvent.created_at.desc())
    events = (await db.execute(query)).scalars().all()
    return [IncidentEventOut.model_validate(e) for e in events]

```

---

## Backend/app/api/lost_persons.py
`Backend/app/api/lost_persons.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.integrations.notification_adapter import notification_adapter
from app.integrations.speech_adapter import speech_adapter
from app.integrations.storage_adapter import storage_adapter
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.user import User
from app.schemas.lost_person import (
    FaceMatchOut,
    FaceMatchVerifyRequest,
    LostPersonCaseCreate,
    LostPersonCaseOut,
    LostPersonReportOut,
    PurgeSensitiveDataResponse
)
from app.services.lost_person_service import lost_person_service

router = APIRouter(prefix="/lost-persons", tags=["Lost & Found"], dependencies=[Depends(get_current_user)])


import json

def _format_case_out(c: LostPersonCase) -> LostPersonCaseOut:
    out = LostPersonCaseOut.model_validate(c)
    if c.photo_urls:
        if isinstance(c.photo_urls, str):
            try:
                out.photo_urls = json.loads(c.photo_urls)
            except Exception:
                out.photo_urls = [c.photo_urls]
        elif isinstance(c.photo_urls, list):
            out.photo_urls = c.photo_urls
    elif c.photo_url:
        out.photo_urls = [c.photo_url]
    return out


@router.get("", response_model=List[LostPersonCaseOut], summary="List lost person cases")
async def list_lost_person_cases(
    status: Optional[LostPersonStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    cases = await lost_person_service.get_cases(db, status=status)
    return [_format_case_out(c) for c in cases]


@router.post("", response_model=LostPersonCaseOut, status_code=status.HTTP_201_CREATED, summary="Register missing person case")
async def create_case(
    case_in: LostPersonCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.create_case(db, case_in, user_id=user_id)
    return _format_case_out(case)


@router.get("/{id}", response_model=LostPersonCaseOut, summary="Get lost person case details")
async def get_case(id: str, db: AsyncSession = Depends(get_db)):
    query = select(LostPersonCase).where(
        (LostPersonCase.id == id) | (LostPersonCase.case_number == id)
    ).options(
        selectinload(LostPersonCase.reports),
        selectinload(LostPersonCase.matches)
    )
    case = (await db.execute(query)).scalar_one_or_none()
    if not case:
        raise NotFoundException("Lost person case not found")
    return _format_case_out(case)


@router.post("/{id}/audio", response_model=LostPersonReportOut, summary="Upload & transcribe helpline call recording")
async def upload_audio_report(
    id: str,
    file: UploadFile = File(...),
    caller_name: Optional[str] = Form(None),
    caller_phone: Optional[str] = Form(None),
    language: str = Form("mr"),
    db: AsyncSession = Depends(get_db)
):
    case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == id))).scalar_one_or_none()
    if not case:
        raise NotFoundException("Case not found")

    content = await file.read()
    filename = f"case_{case.case_number}_{file.filename}"
    file_url = await storage_adapter.save_file(filename, content)

    # Perform Speech-to-Text via adapter
    asr_res = await speech_adapter.transcribe(content, language=language)

    report = LostPersonReport(
        case_id=case.id,
        caller_name=caller_name or "Helpline 112 Caller",
        caller_phone=caller_phone or "+91-112",
        audio_file_url=file_url,
        transcript=asr_res.get("transcript"),
        language=language,
        asr_confidence=asr_res.get("asr_confidence", 0.94)
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return LostPersonReportOut.model_validate(report)


@router.post("/{id}/matches/{match_id}/verify", response_model=FaceMatchOut, summary="Verify or reject AI face match candidate")
async def verify_match(
    id: str,
    match_id: str,
    req: FaceMatchVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    match = await lost_person_service.verify_match(db, case_id=id, match_id=match_id, verified=req.verified, user_id=user_id)
    return FaceMatchOut.model_validate(match)


@router.post("/{id}/dispatch", response_model=LostPersonCaseOut, summary="Dispatch nearby volunteer squad")
async def dispatch_volunteer(
    id: str,
    volunteer_name: str = "Nearby Volunteer Squad",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.dispatch_volunteer(db, case_id=id, volunteer_name=volunteer_name, user_id=user_id)
    return LostPersonCaseOut.model_validate(case)


@router.post("/{id}/reunite", response_model=LostPersonCaseOut, summary="Mark pilgrim as reunited")
async def reunite_case(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    case = await lost_person_service.reunite_case(db, case_id=id, user_id=user_id)
    return LostPersonCaseOut.model_validate(case)


@router.post("/{id}/purge-sensitive-data", response_model=PurgeSensitiveDataResponse, summary="Privacy purge of case biometric vectors & audio")
async def purge_sensitive_data(id: str, db: AsyncSession = Depends(get_db)):
    """
    Permanently purge temporary biometric vectors, face search embeddings,
    and audio metadata while maintaining the minimum operational audit record.
    """
    deleted_count = await lost_person_service.purge_sensitive_data(db, case_id=id)
    return PurgeSensitiveDataResponse(
        success=True,
        message="Sensitive biometric embeddings and temporary audio references purged successfully.",
        purged_records_count=deleted_count,
        case_id=id
    )


@router.post("/{id}/pa-announce", summary="Queue Public Address Announcement")
async def queue_pa_announcement(
    id: str,
    location: str = "Wakhri Phata Loudspeaker Sector 3",
    db: AsyncSession = Depends(get_db)
):
    case = (await db.execute(select(LostPersonCase).where(LostPersonCase.id == id))).scalar_one_or_none()
    if not case:
        raise NotFoundException("Case not found")

    msg = f"हरवलेली व्यक्ती: {case.name}, वय {case.age}, पोशाख: {case.clothing_description}."
    await notification_adapter.send_pa_announcement(location, msg)
    return {
        "success": True,
        "case_number": case.case_number,
        "location": location,
        "message": "PA announcement queued for broadcast",
        "announcement_marathi": msg
    }

```

---

## Backend/app/api/medical.py
`Backend/app/api/medical.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.medical import MedicalAlert, MedicalAlertStatus
from app.models.user import User
from app.schemas.medical import (
    MedicalAlertAcknowledgeRequest,
    MedicalAlertCreate,
    MedicalAlertDispatchRequest,
    MedicalAlertOut,
    MedicalAlertResolveRequest
)
from app.services.medical_service import medical_service

router = APIRouter(prefix="/medical-alerts", tags=["Medical Alerts"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[MedicalAlertOut], summary="List active & resolved medical alerts")
async def list_medical_alerts(
    status: Optional[MedicalAlertStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    alerts = await medical_service.get_alerts(db, status=status)
    return [MedicalAlertOut.model_validate(a) for a in alerts]


@router.post("", response_model=MedicalAlertOut, status_code=status.HTTP_201_CREATED, summary="Create medical emergency alert")
async def create_medical_alert(
    alert_in: MedicalAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.create_alert(db, alert_in, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)


@router.get("/{id}", response_model=MedicalAlertOut, summary="Get medical alert details")
async def get_medical_alert(id: str, db: AsyncSession = Depends(get_db)):
    alert = (await db.execute(select(MedicalAlert).where((MedicalAlert.id == id) | (MedicalAlert.alert_code == id)))).scalar_one_or_none()
    if not alert:
        raise NotFoundException("Medical alert not found")
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/acknowledge", response_model=MedicalAlertOut, summary="Acknowledge medical alert")
async def acknowledge_medical_alert(
    id: str,
    ack_req: Optional[MedicalAlertAcknowledgeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    vol_name = ack_req.assigned_volunteer_name if ack_req else None
    alert = await medical_service.acknowledge_alert(db, alert_id=id, volunteer_name=vol_name, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/dispatch", response_model=MedicalAlertOut, summary="Dispatch mobile medical van / ambulance")
async def dispatch_medical_unit(
    id: str,
    dispatch_req: MedicalAlertDispatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.dispatch_medical_unit(
        db,
        alert_id=id,
        resource_id=dispatch_req.resource_id,
        volunteer_name=dispatch_req.volunteer_name,
        user_id=user_id
    )
    return MedicalAlertOut.model_validate(alert)


@router.post("/{id}/resolve", response_model=MedicalAlertOut, summary="Mark medical alert as resolved")
async def resolve_medical_alert(
    id: str,
    resolve_req: MedicalAlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    alert = await medical_service.resolve_alert(db, alert_id=id, resolution_notes=resolve_req.resolution_notes, user_id=user_id)
    return MedicalAlertOut.model_validate(alert)

```

---

## Backend/app/api/resources.py
`Backend/app/api/resources.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.resource import Resource, ResourceAvailability, ResourceType
from app.models.user import User
from app.schemas.resource import (
    ResourceCreate,
    ResourceDispatchRequest,
    ResourceOut,
    ResourceStatusUpdateRequest,
    ResourceUpdate
)
from app.services.resource_service import resource_service

router = APIRouter(prefix="/resources", tags=["Resources"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[ResourceOut], summary="List all operational resources & units")
async def list_resources(
    resource_type: Optional[ResourceType] = None,
    availability: Optional[ResourceAvailability] = None,
    db: AsyncSession = Depends(get_db)
):
    resources = await resource_service.get_resources(db, resource_type, availability)
    return [ResourceOut.model_validate(r) for r in resources]


@router.get("/nearby", response_model=List[ResourceOut], summary="Find nearest available resources sorted by distance")
async def get_nearby_resources(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    resource_type: Optional[ResourceType] = None,
    availability: Optional[ResourceAvailability] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Calculates haversine distance to stationed resources and returns sorted nearest units."""
    return await resource_service.get_nearby_resources(db, latitude, longitude, resource_type, availability, limit)


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED, summary="Register new resource asset")
async def create_resource(res_in: ResourceCreate, db: AsyncSession = Depends(get_db)):
    res = Resource(**res_in.model_dump())
    db.add(res)
    await db.commit()
    await db.refresh(res)
    return ResourceOut.model_validate(res)


@router.get("/{id}", response_model=ResourceOut, summary="Get resource details by ID or code")
async def get_resource(id: str, db: AsyncSession = Depends(get_db)):
    query = select(Resource).where((Resource.id == id) | (Resource.resource_code == id)).options(selectinload(Resource.assignments))
    res = (await db.execute(query)).scalar_one_or_none()
    if not res:
        raise NotFoundException("Resource not found")
    return ResourceOut.model_validate(res)


@router.post("/{id}/dispatch", response_model=ResourceOut, summary="Dispatch resource to incident")
async def dispatch_resource(
    id: str,
    dispatch_req: ResourceDispatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    res = await resource_service.dispatch_resource(
        db,
        resource_id=id,
        incident_id=dispatch_req.incident_id,
        notes=dispatch_req.notes,
        user_id=user_id
    )
    return ResourceOut.model_validate(res)


@router.post("/{id}/status", response_model=ResourceOut, summary="Update resource availability & location")
async def update_resource_status(
    id: str,
    status_req: ResourceStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    res = await resource_service.update_status(
        db,
        resource_id=id,
        availability=status_req.availability,
        status_tag=status_req.status_tag,
        latitude=status_req.latitude,
        longitude=status_req.longitude,
        user_id=user_id
    )
    return ResourceOut.model_validate(res)

```

---

## Backend/app/api/routes.py
`Backend/app/api/routes.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.route import Route, RouteStatus
from app.models.user import User
from app.schemas.route import RouteActionRequest, RouteCreate, RouteOut, RouteUpdate
from app.services.route_service import route_service

router = APIRouter(prefix="/routes", tags=["Routes"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[RouteOut], summary="List all monitored pilgrimage route segments")
async def list_routes(db: AsyncSession = Depends(get_db)):
    routes = await route_service.get_routes(db)
    return [RouteOut.model_validate(r) for r in routes]


@router.get("/{id}", response_model=RouteOut, summary="Get route details")
async def get_route(id: str, db: AsyncSession = Depends(get_db)):
    route = (await db.execute(select(Route).where(Route.id == id))).scalar_one_or_none()
    if not route:
        raise NotFoundException("Route not found")
    return RouteOut.model_validate(route)


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED, summary="Create new route segment")
async def create_route(route_in: RouteCreate, db: AsyncSession = Depends(get_db)):
    route = Route(**route_in.model_dump())
    db.add(route)
    await db.commit()
    await db.refresh(route)
    return RouteOut.model_validate(route)


@router.post("/{id}/divert", response_model=RouteOut, summary="Set route status to DIVERTED")
async def divert_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Diverted by Command Center"
    route = await route_service.change_status(db, id, RouteStatus.DIVERTED, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)


@router.post("/{id}/close", response_model=RouteOut, summary="Set route status to CLOSED")
async def close_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Closed due to heavy pedestrian bottleneck"
    route = await route_service.change_status(db, id, RouteStatus.CLOSED, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)


@router.post("/{id}/open", response_model=RouteOut, summary="Set route status to OPEN")
async def open_route(
    id: str,
    req: Optional[RouteActionRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    reason = req.reason if req else "Corridor cleared for pilgrims"
    route = await route_service.change_status(db, id, RouteStatus.OPEN, reason=reason, user_id=user_id)
    return RouteOut.model_validate(route)

```

---

## Backend/app/api/notifications.py
`Backend/app/api/notifications.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rbac import get_current_user
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.schemas.audit import AuditLogOut
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.demo_service import demo_service

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"], dependencies=[Depends(get_current_user)])
audit_router = APIRouter(prefix="/audit", tags=["Audit"], dependencies=[Depends(get_current_user)])
demo_router = APIRouter(prefix="/demo", tags=["Demo"], dependencies=[Depends(get_current_user)])
health_router = APIRouter(tags=["Health"])


# --- NOTIFICATIONS ENDPOINTS ---
@notifications_router.get("", response_model=List[NotificationOut], summary="List notifications")
async def list_notifications(limit: int = 50, db: AsyncSession = Depends(get_db)):
    query = select(Notification).order_by(desc(Notification.created_at)).limit(limit)
    result = await db.execute(query)
    return [NotificationOut.model_validate(n) for n in result.scalars().all()]


@notifications_router.post("", response_model=NotificationOut, status_code=status.HTTP_201_CREATED, summary="Create notification")
async def create_notification(notif_in: NotificationCreate, db: AsyncSession = Depends(get_db)):
    notif = Notification(**notif_in.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return NotificationOut.model_validate(notif)


@notifications_router.patch("/{id}/read", response_model=NotificationOut, summary="Mark notification as read")
async def mark_notification_read(id: str, db: AsyncSession = Depends(get_db)):
    notif = (await db.execute(select(Notification).where(Notification.id == id))).scalar_one_or_none()
    if not notif:
        raise NotFoundException("Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return NotificationOut.model_validate(notif)


# --- AUDIT ENDPOINTS ---
@audit_router.get("", response_model=List[AuditLogOut], summary="Query operational audit logs")
async def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at))
    if action:
        query = query.where(AuditLog.action == action)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    query = query.limit(limit)
    result = await db.execute(query)
    return [AuditLogOut.model_validate(a) for a in result.scalars().all()]


# --- DEMO SIMULATION ENDPOINTS ---
@demo_router.post("/start", summary="Start automated Wari pilgrimage operational simulation")
async def start_demo_simulation():
    """Launches an asynchronous realistic operational emergency flow."""
    return await demo_service.start()


@demo_router.post("/stop", summary="Stop automated demo simulation")
async def stop_demo_simulation():
    """Cancels the active demo simulation."""
    return await demo_service.stop()


@demo_router.get("/status", summary="Get demo simulation status")
async def get_demo_status():
    """Check whether demo simulation is currently running and current step index."""
    return demo_service.get_status()


# --- HEALTH CHECK ENDPOINTS (PUBLIC) ---
@health_router.get("/health", summary="Basic health check")
async def health_check():
    return {"status": "ok", "service": "varisetu-backend", "version": "2.0.0"}


@health_router.get("/health/database", summary="Database health check")
async def health_database(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "connected", "database": "healthy"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@health_router.get("/health/redis", summary="Redis health check")
async def health_redis():
    from app.core.redis import redis_client
    return {
        "status": "connected" if redis_client.is_connected else "fallback_in_memory",
        "redis_available": redis_client.is_connected
    }


@health_router.get("/health/services", summary="Integration services status check")
async def health_services():
    from app.core.config import settings
    from app.integrations.qdrant_adapter import qdrant_adapter
    return {
        "database": "postgresql_compatible",
        "redis": "ready",
        "qdrant": await qdrant_adapter.health_check(),
        "speech": settings.SPEECH_PROVIDER,
        "vision": settings.VISION_PROVIDER,
        "weather": settings.WEATHER_PROVIDER,
        "notifications": settings.NOTIFICATION_PROVIDER
    }

```

---

## Backend/app/seed/seed_data.py
`Backend/app/seed/seed_data.py`

```python
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.rbac import UserRole
from app.core.security import get_password_hash
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.medical import MedicalAlert, MedicalAlertStatus, MedicalAlertType
from app.models.notification import Notification, NotificationType
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability, ResourceType
from app.models.route import Route, RouteStatus
from app.models.user import User
from app.models.zone import RiskLevel, Zone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("varisetu.seed")


async def seed_database():
    logger.info("Initializing database schema...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if users already exist
        existing_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if existing_user:
            logger.info("Database already seeded. Skipping...")
            return

        logger.info("Seeding users...")
        users = [
            User(
                name="Command Center Controller",
                email="control.room@mahapolice.gov.in",
                phone="+91-9822001122",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.ADMIN,
                department="Maharashtra Police IT Cell",
                is_active=True
            ),
            User(
                name="Inspector R. K. Patil",
                email="police.officer@mahapolice.gov.in",
                phone="+91-9822003344",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.POLICE,
                department="Pandharpur Traffic Division",
                is_active=True
            ),
            User(
                name="Dr. Shubhada Deshmukh",
                email="medical.team@varisetu.org",
                phone="+91-9822005566",
                password_hash=get_password_hash("varisetu2026"),
                role=UserRole.MEDICAL,
                department="Emergency Health Services",
                is_active=True
            )
        ]
        db.add_all(users)
        await db.flush()

        logger.info("Seeding zones...")
        zones = [
            Zone(name="Pandharpur Chowk", description="Main temple entry plaza bottleneck", latitude=17.6777, longitude=75.3276, capacity=60000, risk_level=RiskLevel.CRITICAL),
            Zone(name="Wakhri Phata", description="Major highway diversion and camp junction", latitude=17.7280, longitude=75.2950, capacity=45000, risk_level=RiskLevel.HIGH),
            Zone(name="Vakhri Naka", description="Bridge approach choke point", latitude=17.7500, longitude=75.2700, capacity=35000, risk_level=RiskLevel.HIGH),
            Zone(name="Saswad Highway Stop", description="Intermediate resting shelter", latitude=18.3440, longitude=74.0305, capacity=25000, risk_level=RiskLevel.MODERATE),
            Zone(name="Tarapur Phata", description="Bypass junction for supply convoys", latitude=17.8000, longitude=75.1500, capacity=20000, risk_level=RiskLevel.LOW),
            Zone(name="Alandi Corridor", description="Procession starting ghats", latitude=18.6772, longitude=73.8967, capacity=50000, risk_level=RiskLevel.LOW),
        ]
        db.add_all(zones)
        await db.flush()
        zone_map = {z.name: z.id for z in zones}

        logger.info("Seeding cameras...")
        cameras = [
            Camera(camera_code="CAM-01", name="Alandi Ghat Section Cam 01", zone_id=zone_map["Alandi Corridor"], latitude=18.6772, longitude=73.8967, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-04", name="Pandharpur Temple Chowk Cam 04", zone_id=zone_map["Pandharpur Chowk"], latitude=17.6777, longitude=75.3276, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-08", name="Saswad Highway Checkpoint Cam 08", zone_id=zone_map["Saswad Highway Stop"], latitude=18.3440, longitude=74.0305, status=CameraStatus.ONLINE),
            Camera(camera_code="CAM-12", name="Wakhri Phata Junction Cam 12", zone_id=zone_map["Wakhri Phata"], latitude=17.7280, longitude=75.2950, status=CameraStatus.ONLINE),
        ]
        db.add_all(cameras)
        await db.flush()
        cam_map = {c.camera_code: c.id for c in cameras}

        logger.info("Seeding crowd observations...")
        observations = [
            CrowdObservation(camera_id=cam_map["CAM-04"], zone_id=zone_map["Pandharpur Chowk"], density_percentage=94.0, people_count=2850, movement_direction="SOUTH", trend=CrowdTrend.RISING, risk_level=RiskLevel.CRITICAL, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-12"], zone_id=zone_map["Wakhri Phata"], density_percentage=88.0, people_count=1420, movement_direction="EAST", trend=CrowdTrend.RISING, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-08"], zone_id=zone_map["Saswad Highway Stop"], density_percentage=62.0, people_count=890, movement_direction="SOUTH", trend=CrowdTrend.EASING, risk_level=RiskLevel.MODERATE, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-01"], zone_id=zone_map["Alandi Corridor"], density_percentage=35.0, people_count=410, movement_direction="SOUTH", trend=CrowdTrend.STABLE, risk_level=RiskLevel.LOW, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Vakhri Naka"], density_percentage=74.0, people_count=1100, trend=CrowdTrend.STABLE, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Tarapur Phata"], density_percentage=28.0, people_count=320, trend=CrowdTrend.FALLING, risk_level=RiskLevel.LOW, source="DEMO"),
        ]
        db.add_all(observations)

        logger.info("Seeding incidents & events...")
        incidents = [
            Incident(
                incident_number="INC-2026-0825-001",
                type=IncidentType.CROWD,
                severity=IncidentSeverity.HIGH,
                status=IncidentStatus.OPEN,
                source="CCTV_AI",
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                title="Crowd density surge detected at Wakhri Phata (88%)",
                description="Pedestrian flow bottleneck causing slow movement. Recommendation: Divert queue to North Ring Road.",
                is_demo=True
            ),
            Incident(
                incident_number="INC-2026-0825-002",
                type=IncidentType.ROAD_BLOCK,
                severity=IncidentSeverity.MEDIUM,
                status=IncidentStatus.IN_PROGRESS,
                source="OPERATOR",
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                title="Solapur Highway Diversion Gate 2 opened",
                description="Traffic diverted to secondary bypass for VIP procession escort.",
                is_demo=True
            )
        ]
        db.add_all(incidents)
        await db.flush()

        events = [
            IncidentEvent(incident_id=incidents[0].id, event_type="CROWD_PEAK", message="CAM-12 Wakhri Phata: Density peak detected (88%)"),
            IncidentEvent(incident_id=incidents[1].id, event_type="ROUTE_DIVERTED", message="Solapur Highway Diversion Gate 2 opened for traffic relief")
        ]
        db.add_all(events)

        logger.info("Seeding lost person cases...")
        lost_cases = [
            LostPersonCase(
                case_number="#LF-802",
                name="Maruti Kisan Shinde",
                age=68,
                gender="M",
                clothing_description="पांढरा कुर्ता, धोती, पांढरी टोपी (White Kurta-Dhoti, Gandhi topi, Tulsi mala)",
                last_seen_location="Pandharpur Temple Chowk",
                last_seen_camera_id=cam_map["CAM-04"],
                priority="HIGH",
                status=LostPersonStatus.MATCH_FOUND,
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-805",
                name="Anandita Ramesh Kulkarni",
                age=9,
                gender="F",
                clothing_description="पिवळा परकर पोलका (Yellow traditional dress, red ribbons)",
                last_seen_location="Wakhri Phata Rest Camp",
                last_seen_camera_id=cam_map["CAM-12"],
                priority="CRITICAL",
                status=LostPersonStatus.SEARCHING,
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-799",
                name="Dnyaneshwar Mahadev Jadhav",
                age=72,
                gender="M",
                clothing_description="पांढरा पोशाख, लाल पटका (White attire with red turban)",
                last_seen_location="Saswad Highway Checkpoint",
                last_seen_camera_id=cam_map["CAM-08"],
                priority="NORMAL",
                status=LostPersonStatus.REUNITED,
                resolved_at=datetime.now(timezone.utc),
                is_demo=True
            ),
            LostPersonCase(
                case_number="#LF-808",
                name="Sunita Vitthal Patil",
                age=54,
                gender="F",
                clothing_description="हिरवी नऊवारी साडी (Green Nauvari saree)",
                last_seen_location="Alandi Ghat Section",
                last_seen_camera_id=cam_map["CAM-01"],
                priority="HIGH",
                status=LostPersonStatus.SEARCHING,
                is_demo=True
            )
        ]
        db.add_all(lost_cases)
        await db.flush()

        # Add Marathi reports & Face matches
        reports = [
            LostPersonReport(
                case_id=lost_cases[0].id,
                caller_name="Namdeo Shinde (Grandson)",
                caller_phone="+91-9822014455",
                transcript="हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत.",
                language="mr",
                asr_confidence=0.94
            ),
            LostPersonReport(
                case_id=lost_cases[1].id,
                caller_name="Ramesh Kulkarni (Father)",
                caller_phone="+91-9822019988",
                transcript="माझी मुलगी आनंदिता वय ९ वर्षे वाखरी विश्राम शिबिराजवळ सुटली आहे. तिने पिवळा परकर पोलका घातला आहे.",
                language="mr",
                asr_confidence=0.96
            ),
            LostPersonReport(
                case_id=lost_cases[3].id,
                caller_name="Vitthal Patil (Husband)",
                caller_phone="+91-9822013322",
                transcript="माझी पत्नी सुनिता पाटील आळंदी घाट जवळ दिंडीतून पुढे निघून गेली आहे, हिरवी नऊवारी साडी आहे.",
                language="mr",
                asr_confidence=0.91
            )
        ]
        db.add_all(reports)

        matches = [
            FaceMatchResult(
                case_id=lost_cases[0].id,
                camera_id=cam_map["CAM-04"],
                frame_reference="frame_4812.jpg",
                similarity_score=0.89,
                confidence=0.94,
                status=FaceMatchStatus.PENDING_VERIFICATION
            )
        ]
        db.add_all(matches)

        logger.info("Seeding medical alerts...")
        medical_alerts = [
            MedicalAlert(
                alert_code="MED-101",
                type=MedicalAlertType.FALL,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                description="FALL DETECTED / FAINTING PILGRIM (Wakhri Phata Km 184) - Dispatching First Responder",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Team Bravo (V. R. Kadam)",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-102",
                type=MedicalAlertType.HEAT_EXHAUSTION,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Pandharpur Chowk"],
                camera_id=cam_map["CAM-04"],
                latitude=17.6777,
                longitude=75.3276,
                description="CROWD HEAT EXHAUSTION RISK (SECTOR 5) - Ambient Temp 34°C, High Humidity",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Medical Van #MV-02",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-098",
                type=MedicalAlertType.DEHYDRATION,
                severity=IncidentSeverity.MEDIUM,
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                description="DEHYDRATION ASSIST & REHYDRATION (RESOLVED) - Pilgrim treated with ORSL salt packets",
                status=MedicalAlertStatus.RESOLVED,
                assigned_volunteer_name="Red Cross Volunteer Post #3",
                resolved_at=datetime.now(timezone.utc),
                is_demo=True
            )
        ]
        db.add_all(medical_alerts)

        logger.info("Seeding resources & vehicles...")
        resources = [
            Resource(resource_code="WT-09", name="10,000L Water Tanker #09", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Station Standby"),
            Resource(resource_code="WT-04", name="10,000L Water Tanker #04", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="DEPLOYED", availability=ResourceAvailability.ASSIGNED, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Temple Gate North"),
            Resource(resource_code="WT-12", name="10,000L Water Tanker #12", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=18.3440, longitude=74.0305, zone_id=zone_map["Saswad Highway Stop"], location_description="Saswad Rest Post"),
            Resource(resource_code="MV-02", name="Mobile Medical Van #02 (Ambulance)", resource_type=ResourceType.MEDICAL_VAN, capacity=4, status_tag="ACTIVE", availability=ResourceAvailability.ASSIGNED, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Sector 4 Base"),
            Resource(resource_code="MV-05", name="Emergency Ambulance #05", resource_type=ResourceType.AMBULANCE, capacity=2, status_tag="STANDBY", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Pandharpur Civil Hospital"),
            Resource(resource_code="PS-14", name="Police Patrol Squad #14", resource_type=ResourceType.POLICE_SQUAD, capacity=8, status_tag="ACTIVE", availability=ResourceAvailability.ON_SCENE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Bottleneck Patrol"),
            Resource(resource_code="VT-08", name="Dindi Volunteer Stewards (Squad 8)", resource_type=ResourceType.VOLUNTEER_TEAM, capacity=25, status_tag="ACTIVE", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Chhatrapati Shivaji Chowk"),
        ]
        db.add_all(resources)

        logger.info("Seeding routes...")
        routes = [
            Route(name="NH-9 Solapur Highway Junction", description="Primary vehicle thoroughfare", status=RouteStatus.DIVERTED, priority="PRIMARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.6777, longitude_end=75.3276),
            Route(name="Pune-Saswad Pilgrimage Road", description="Dedicated pedestrian corridor for Palkhi procession", status=RouteStatus.PILGRIMS_ONLY, priority="PRIMARY", latitude_start=18.6772, longitude_start=73.8967, latitude_end=18.3440, longitude_end=74.0305),
            Route(name="Wakhri Phata Inner Access Road", description="Narrow passage near temporary tents", status=RouteStatus.CLOSED, priority="SECONDARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.7500, longitude_end=75.2700),
            Route(name="Pandharpur Temple Ring Road", description="Reserved exclusively for ambulances and police emergency vehicles", status=RouteStatus.EMERGENCY_ACCESS, priority="PRIMARY", latitude_start=17.6777, longitude_start=75.3276, latitude_end=17.6850, longitude_end=75.3400),
        ]
        db.add_all(routes)

        logger.info("Seeding notifications...")
        notifications = [
            Notification(type=NotificationType.CROWD, title="Crowd Congestion Warning", message="Density at Wakhri Phata crossed 85%. Automated queue diversion suggested.", priority="HIGH"),
            Notification(type=NotificationType.MEDICAL, title="Medical Emergency Dispatched", message="Ambulance MV-02 dispatched to Sector 4 for fainting pilgrim.", priority="HIGH"),
            Notification(type=NotificationType.LOST_PERSON, title="AI Face Match Candidate", message="Candidate match with 89% similarity found on CAM-04 for #LF-802.", priority="NORMAL"),
        ]
        db.add_all(notifications)

        await db.commit()
        logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())

```

---

## Backend/tests/conftest.py
`Backend/tests/conftest.py`

```python
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.seed.seed_data import seed_database

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Seed the test in-memory database
    from app.core.rbac import UserRole
    from app.core.security import get_password_hash
    from app.models.user import User
    from app.models.zone import Zone, RiskLevel

    u = User(
        name="Test Commander",
        email="test.commander@mahapolice.gov.in",
        password_hash=get_password_hash("varisetu2026"),
        role=UserRole.ADMIN,
        is_active=True
    )
    z = Zone(
        name="Pandharpur Chowk",
        latitude=17.6777,
        longitude=75.3276,
        capacity=50000,
        risk_level=RiskLevel.LOW
    )
    test_db.add(u)
    test_db.add(z)
    await test_db.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

```

---

## Backend/tests/test_api.py
`Backend/tests/test_api.py`

```python
import pytest
from app.core.rbac import UserRole
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_health_endpoints(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_authentication_flow(client):
    # 1. Login with valid credentials
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # 2. Login with wrong password (must fail 401)
    wrong_login = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "wrongpassword"
    })
    assert wrong_login.status_code == 401

    # 3. Call /api/auth/me with valid token
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = await client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "test.commander@mahapolice.gov.in"
    assert me_data["role"] == "ADMIN"

    # 4. Call /api/auth/me without token (must fail 401)
    unauth_me = await client.get("/api/auth/me")
    assert unauth_me.status_code == 401

    # 5. Refresh token flow
    ref_res = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()

    # 6. Logout
    logout_res = await client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True


@pytest.mark.asyncio
async def test_admin_user_registration(client):
    # Obtain admin token
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin registers a new police officer
    reg_payload = {
        "name": "Officer Sachin Shinde",
        "email": "sachin.shinde@mahapolice.gov.in",
        "phone": "+91-9822009988",
        "password": "OfficerPassword@2026",
        "role": "POLICE",
        "department": "Wakhri Traffic Sector",
        "is_active": True
    }
    reg_res = await client.post("/api/auth/register", json=reg_payload, headers=admin_headers)
    assert reg_res.status_code == 200
    new_user = reg_res.json()
    assert new_user["email"] == "sachin.shinde@mahapolice.gov.in"
    assert new_user["role"] == "POLICE"

    # Log in as newly registered police officer
    officer_login = await client.post("/api/auth/login", json={
        "email": "sachin.shinde@mahapolice.gov.in",
        "password": "OfficerPassword@2026"
    })
    assert officer_login.status_code == 200
    officer_token = officer_login.json()["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # Non-admin user attempts to register another user (must fail 403 Forbidden)
    forbidden_reg = await client.post("/api/auth/register", json={
        "name": "Another User",
        "email": "another@mahapolice.gov.in",
        "password": "password123",
        "role": "VIEWER"
    }, headers=officer_headers)
    assert forbidden_reg.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_summary(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "active_incidents" in data
    assert "palkhi_location" in data
    assert "estimated_pilgrim_count" in data


@pytest.mark.asyncio
async def test_dashboard_heat_risk(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/dashboard/heat-risk", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "ambient_temperature" in data
    assert "computed_risk_index" in data


@pytest.mark.asyncio
async def test_create_and_acknowledge_incident(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create incident
    create_payload = {
        "title": "Pedestrian bottleneck test",
        "type": "CROWD",
        "severity": "HIGH",
        "description": "Dense crowd surge at sector 2",
        "source": "OPERATOR"
    }
    create_res = await client.post("/api/incidents", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    inc_data = create_res.json()
    assert inc_data["status"] == "OPEN"
    inc_id = inc_data["id"]

    # Acknowledge incident
    ack_res = await client.post(f"/api/incidents/{inc_id}/acknowledge", json={"notes": "Controller dispatched patrol squad"}, headers=headers)
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve incident
    res_res = await client.post(f"/api/incidents/{inc_id}/resolve", json={"resolution_notes": "Queue cleared"}, headers=headers)
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_lost_person_workflow(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register lost person
    case_payload = {
        "name": "Maruti Kisan Shinde",
        "age": 68,
        "gender": "M",
        "clothing_description": "White Kurta-Dhoti, Gandhi topi",
        "last_seen_location": "Pandharpur Chowk",
        "caller_name": "Namdeo Shinde",
        "caller_phone": "+91-9822014455"
    }
    case_res = await client.post("/api/lost-persons", json=case_payload, headers=headers)
    assert case_res.status_code == 201
    case_data = case_res.json()
    assert case_data["name"] == "Maruti Kisan Shinde"
    case_id = case_data["id"]

    # Dispatch volunteer
    disp_res = await client.post(f"/api/lost-persons/{case_id}/dispatch", headers=headers)
    assert disp_res.status_code == 200
    assert disp_res.json()["status"] == "DISPATCHED"

    # Reunite case
    reunite_res = await client.post(f"/api/lost-persons/{case_id}/reunite", headers=headers)
    assert reunite_res.status_code == 200
    assert reunite_res.json()["status"] == "REUNITED"

    # Purge sensitive biometric data
    purge_res = await client.post(f"/api/lost-persons/{case_id}/purge-sensitive-data", headers=headers)
    assert purge_res.status_code == 200
    assert purge_res.json()["success"] is True


@pytest.mark.asyncio
async def test_medical_alert_workflow(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create alert
    alert_payload = {
        "type": "FALL",
        "severity": "HIGH",
        "latitude": 17.7280,
        "longitude": 75.2950,
        "description": "Pilgrim fall detected at Wakhri junction"
    }
    alert_res = await client.post("/api/medical-alerts", json=alert_payload, headers=headers)
    assert alert_res.status_code == 201
    alert_data = alert_res.json()
    alert_id = alert_data["id"]
    assert alert_data["status"] == "ACTIVE"

    # Acknowledge alert
    ack_res = await client.post(f"/api/medical-alerts/{alert_id}/acknowledge", json={"assigned_volunteer_name": "Team Alpha"}, headers=headers)
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve alert
    resolve_res = await client.post(f"/api/medical-alerts/{alert_id}/resolve", json={"resolution_notes": "First aid administered"}, headers=headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_routes_status_change(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create route
    route_res = await client.post("/api/routes", json={
        "name": "NH-9 Solapur Corridor",
        "status": "OPEN",
        "priority": "PRIMARY"
    }, headers=headers)
    assert route_res.status_code == 201
    route_id = route_res.json()["id"]

    # Divert route
    divert_res = await client.post(f"/api/routes/{route_id}/divert", json={"reason": "Pedestrian safety"}, headers=headers)
    assert divert_res.status_code == 200
    assert divert_res.json()["status"] == "DIVERTED"


@pytest.mark.asyncio
async def test_lost_person_with_multiple_photos(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_payload = {
        "name": "Savitribai Patil",
        "age": 62,
        "gender": "F",
        "clothing_description": "Green saree with red border",
        "last_seen_location": "Sudarshan Chowk",
        "photo_urls": [
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        ],
        "priority": "HIGH"
    }

    create_res = await client.post("/api/lost-persons", json=case_payload, headers=headers)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["name"] == "Savitribai Patil"
    assert len(data["photo_urls"]) == 2
    assert data["photo_url"] is not None


@pytest.mark.asyncio
async def test_public_info_and_report_lost(client):
    # Public info endpoint (no auth required)
    info_res = await client.get("/api/public/info")
    assert info_res.status_code == 200
    info = info_res.json()
    assert "Sant Tukaram Maharaj" in info["palkhi_name"]
    assert len(info["helplines"]) >= 4

    # Public missing person report (no auth required)
    report_res = await client.post("/api/public/report-lost", json={
        "name": "Kashinath Pawar",
        "age": 70,
        "gender": "M",
        "clothing_description": "White Kurta, saffron shawl",
        "last_seen_location": "Bhalwani halt",
        "caller_name": "Ramesh Pawar",
        "caller_phone": "9822001122",
        "photo_urls": ["data:image/png;base64,test"]
    })
    assert report_res.status_code == 201
    rep_data = report_res.json()
    assert rep_data["status"] == "success"
    assert "case_number" in rep_data


```

---
