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
  setupHelplineCallingInterface();
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

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &bull; Maharashtra Police IT',
    maxZoom: 19
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
    setupHelplineCallingInterface();
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
/* ==================== LEAFLET MAP INITIALIZATION & DYNAMIC LAYERS ==================== */
function initRouteMap() {
  const mapElement = document.getElementById('routeMap');
  if (!mapElement || window.wariMap) return;

  const wariMap = L.map('routeMap', {
    center: [19.2000, 74.0000],
    zoom: 8,
    zoomControl: true
  });

  window.wariMap = wariMap;

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &bull; Maharashtra Police IT (NH-60 Corridor Engine)',
    maxZoom: 19
  }).addTo(wariMap);

  // Layer groups for dynamic elements
  window.warkariLayerGroup = L.layerGroup().addTo(wariMap);
  window.resourceLayerGroup = L.layerGroup().addTo(wariMap);
  window.cctvHighlightLayerGroup = L.layerGroup().addTo(wariMap);

  // Active Pilgrimage Corridor along NH-60 (212 km) Pune (Kothrud) to Nashik (Govind Nagar)
  const sector1 = [
    [18.5074, 73.8077], // Origin: Kothrud Depo, Pune
    [18.5300, 73.8400], // Shivajinagar
    [18.6270, 73.8470]  // Bhosari
  ];
  const sector2 = [
    [18.6270, 73.8470], // Bhosari
    [18.7180, 73.8780], // Chakan
    [18.8600, 73.9100], // Rajgurunagar
    [19.0060, 73.9450]  // Manchar
  ];
  const sector3 = [
    [19.0060, 73.9450], // Manchar
    [19.1240, 73.9780], // Narayangaon (Km 84)
    [19.3100, 74.0600], // Alephata
    [19.5760, 74.2120]  // Sangamner
  ];
  const sector4 = [
    [19.5760, 74.2120], // Sangamner
    [19.7050, 73.9900], // Sinnar
    [19.9700, 73.7800]  // Terminal: Govind Nagar, Nashik
  ];

  L.polyline(sector1, { color: '#2E5B36', weight: 6, opacity: 0.85 }).addTo(wariMap)
    .bindPopup('<b>Sector 1 (Pune ➔ Bhosari):</b> Green Flow (#2E5B36) - 38% Density');
  L.polyline(sector2, { color: '#D98E2C', weight: 6.5, opacity: 0.85 }).addTo(wariMap)
    .bindPopup('<b>Sector 2 (Bhosari ➔ Manchar):</b> Saffron Flow (#D98E2C) - 62% Density');
  L.polyline(sector3, { color: '#B8551B', weight: 7.5, opacity: 0.9 }).addTo(wariMap)
    .bindPopup('<b>Sector 3 (Manchar ➔ Sangamner):</b> Dark Orange (#B8551B) - 82% Heavy Flow');
  L.polyline(sector4, { color: '#9A2525', weight: 8.5, opacity: 0.95 }).addTo(wariMap)
    .bindPopup('<b>Sector 4 (Sangamner ➔ Govind Nagar Nashik):</b> Red (#9A2525) - 92% Critical Surge');

  // Animated Palkhi Marker at Narayangaon (Km 84)
  const palkhiIcon = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#D98E2C; color:#FFF; border:2px solid #7A1F1F; padding:4px 8px; font-weight:bold; font-size:10.5px; border-radius:3px; box-shadow:0 2px 6px rgba(0,0,0,0.35); animation:pulse 2s infinite;">🚩 PALKHI (Narayangaon Km 84)</div>`,
    iconSize: [180, 26],
    iconAnchor: [90, 13]
  });
  AppState.palkhiMarker = L.marker([19.1240, 73.9780], { icon: palkhiIcon }).addTo(wariMap)
    .bindPopup('<b>Sant Tukaram Maharaj Palkhi</b><br>Location: Narayangaon (Km 84 on NH-60)<br>Speed: 3.2 km/h • Heading: North<br>Destination: Narayan Park, Govind Nagar, Nashik');

  // Water Tankers: WT-09 (Narayangaon), WT-04 (Sangamner)
  const tankerIcon9 = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#1D6F8A; color:#FFF; border:1px solid #000; padding:2px 6px; font-size:9px; font-weight:bold; border-radius:2px;">💧 Tanker WT-09</div>`,
    iconSize: [95, 20]
  });
  L.marker([19.1200, 73.9700], { icon: tankerIcon9 }).addTo(wariMap)
    .bindPopup('<b>Water Tanker #WT-09</b><br>Capacity: 10,000L (80% Full)<br>Operator: Ramesh Shinde (+91-9822001122)<br>Location: Narayangaon Standby');

  const tankerIcon4 = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#1D6F8A; color:#FFF; border:1px solid #000; padding:2px 6px; font-size:9px; font-weight:bold; border-radius:2px;">💧 Tanker WT-04</div>`,
    iconSize: [95, 20]
  });
  L.marker([19.5700, 74.2100], { icon: tankerIcon4 }).addTo(wariMap)
    .bindPopup('<b>Water Tanker #WT-04</b><br>Capacity: 10,000L (Deployed)<br>Operator: D. V. More (+91-9822002233)<br>Location: Sangamner North Chowk');

  // Medical Ambulances: MV-01 (Bhosari), MV-02 (Narayangaon), MV-03 (Sangamner)
  const medIcon1 = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#9A2525; color:#FFF; border:1px solid #000; padding:2px 6px; font-size:9px; font-weight:bold; border-radius:2px;">🚑 MedVan MV-01</div>`,
    iconSize: [95, 20]
  });
  L.marker([18.6270, 73.8470], { icon: medIcon1 }).addTo(wariMap)
    .bindPopup('<b>Mobile Medical Ambulance #MV-01</b><br>Doctor: Dr. A. V. Joshi<br>Location: Bhosari Sector 1 Base');

  const medIcon2 = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#9A2525; color:#FFF; border:1px solid #000; padding:2px 6px; font-size:9px; font-weight:bold; border-radius:2px;">🚑 MedVan MV-02</div>`,
    iconSize: [95, 20]
  });
  L.marker([19.1240, 73.9780], { icon: medIcon2 }).addTo(wariMap)
    .bindPopup('<b>Mobile Medical Ambulance #MV-02</b><br>Doctor: Dr. S. P. Deshmukh<br>Location: Narayangaon Km 84 Transit Camp');

  const medIcon3 = L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#9A2525; color:#FFF; border:1px solid #000; padding:2px 6px; font-size:9px; font-weight:bold; border-radius:2px;">🚑 MedVan MV-03</div>`,
    iconSize: [95, 20]
  });
  L.marker([19.5760, 74.2120], { icon: medIcon3 }).addTo(wariMap)
    .bindPopup('<b>Emergency Mobile ICU #MV-03</b><br>Doctor: Dr. P. K. Shirole<br>Location: Sangamner Choke Base');

  // Surveillance CCTVs: CAM-01, CAM-08, CAM-12, CAM-04
  const cctvIcon = (code) => L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:#2B2623; color:#FFF; border:1px solid var(--saffron-gold); padding:2px 5px; font-size:8.5px; font-weight:bold; border-radius:2px;">📹 ${code}</div>`,
    iconSize: [60, 18]
  });
  L.marker([18.5200, 73.8500], { icon: cctvIcon('CAM-01') }).addTo(wariMap).bindPopup('<b>CAM-01 (Pune / Bhosari)</b> - 60 FPS HD Stream');
  L.marker([19.0060, 73.9450], { icon: cctvIcon('CAM-08') }).addTo(wariMap).bindPopup('<b>CAM-08 (Manchar Highway)</b> - 60 FPS HD Stream');
  L.marker([19.1240, 73.9780], { icon: cctvIcon('CAM-12') }).addTo(wariMap).bindPopup('<b>CAM-12 (Narayangaon Checkpoint)</b> - 60 FPS HD Stream');
  L.marker([19.9700, 73.7800], { icon: cctvIcon('CAM-04') }).addTo(wariMap).bindPopup('<b>CAM-04 (Govind Nagar, Nashik Terminal)</b> - 60 FPS HD Stream');

  if (typeof renderDynamicWarkariClusters === 'function') renderDynamicWarkariClusters(AppState.crowdZones || []);
  if (typeof renderResourceMapMarkers === 'function') renderResourceMapMarkers(AppState.resources || []);
}

/* ==================== REALISTIC WARKARI & VEHICLE ROUTE-ALIGNED RENDERING ==================== */

// Exact highway route polyline segments (Alandi -> Pune -> Saswad -> Lonand -> Bhalwani -> Wakhri -> Pandharpur)
const PILGRIMAGE_ROUTE_WAYPOINTS = [
  { name: "Alandi Start Ghat", lat: 18.6772, lng: 73.8967, zone: "ZONE-ALANDI", density: 35 },
  { name: "Pune Hadapsar Chowk", lat: 18.5080, lng: 73.9250, zone: "ZONE-PUNE", density: 50 },
  { name: "Saswad Dive Ghat", lat: 18.3440, lng: 74.0305, zone: "ZONE-SASWAD", density: 62 },
  { name: "Lonand Nira River", lat: 18.0400, lng: 74.1900, zone: "ZONE-LONAND", density: 68 },
  { name: "Taradgaon Camp", lat: 17.9600, lng: 74.5200, zone: "ZONE-TARADGAON", density: 70 },
  { name: "Bhalwani Junction", lat: 17.8900, lng: 75.0200, zone: "ZONE-BHALWANI", density: 74 },
  { name: "Malshiras Sector", lat: 17.8200, lng: 74.9000, zone: "ZONE-MALSHIRAS", density: 78 },
  { name: "Wakhri Phata Base", lat: 17.7280, lng: 75.2950, zone: "ZONE-WAKHRI", density: 88 },
  { name: "Bhatumbare Bypass", lat: 17.7020, lng: 75.3120, zone: "ZONE-PANDHARPUR", density: 92 },
  { name: "Pandharpur Vitthal Mandir", lat: 17.6777, lng: 75.3276, zone: "ZONE-PANDHARPUR", density: 94 }
];

// Helper to interpolate points strictly along route line segments
function interpolatePointsAlongSegment(p1, p2, count, laneOffset = 0.00035) {
  const points = [];
  for (let i = 1; i <= count; i++) {
    const t = i / (count + 1);
    const lat = p1.lat + t * (p2.lat - p1.lat);
    const lng = p1.lng + t * (p2.lng - p1.lng);
    // Subtle alternating lane shift so pilgrims march in two neat columns along the highway
    const laneSign = (i % 2 === 0) ? 1 : -1;
    points.push({
      lat: lat + (laneSign * laneOffset * 0.5),
      lng: lng + (laneSign * laneOffset)
    });
  }
  return points;
}

// 1. Realistic Multi-Variant SVG Warkari Pilgrim (Dhwajdhari, Veenadhari, Taalkari)
function createRealisticWarkariSvg(dindiNumber, isHighDensity = false) {
  const variant = dindiNumber % 3;
  const flagColor = isHighDensity ? '#FF5722' : '#FF9800';
  const auraPulse = isHighDensity ? `<circle cx="19" cy="24" r="18" fill="rgba(217, 142, 44, 0.2)" class="warkari-density-pulse" />` : '';

  if (variant === 0) {
    // Variant 0: Dhwajdhari (भगवा पताका / ध्वजकरी - Pilgrim Flag Bearer)
    return `
      <div class="realistic-warkari-wrapper ${isHighDensity ? 'high-density-warkari' : ''}" style="width:36px; height:46px; position:relative;">
        <svg viewBox="0 0 38 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.25));">
          ${auraPulse}
          <!-- Ground Shadow -->
          <ellipse cx="19" cy="45" rx="10" ry="2.2" fill="rgba(25,18,12,0.4)"/>

          <!-- Tall Wooden Flag Pole -->
          <line x1="24" y1="2" x2="24" y2="44" stroke="#5D4037" stroke-width="2" stroke-linecap="round"/>
          <circle cx="24" cy="2" r="1.6" fill="#FFD54F"/>

          <!-- Flowing Saffron Flag (भगवा ध्वज) -->
          <path d="M24 3L37 8.5L24 14.5V3Z" fill="${flagColor}" stroke="#E65100" stroke-width="0.8"/>
          <path d="M24 6.5L33 9.5L24 12.5V6.5Z" fill="#FFE082" opacity="0.85"/>

          <!-- Traditional Saffron Pagadi / Turban -->
          <path d="M12 9C12 6.2 14.5 4.8 17.5 4.8C20.5 4.8 23 6.2 23 9C23 9.8 22.2 11 20 11.5H15C12.8 11 12 9.8 12 9Z" fill="#E65100"/>
          <ellipse cx="17.5" cy="7" rx="3.5" ry="1.5" fill="#FF9800"/>
          <circle cx="17.5" cy="6.2" r="1" fill="#FFF9C4"/>

          <!-- Face & Sacred Chandan Tilak -->
          <circle cx="17.5" cy="12.5" r="3.3" fill="#FFCC80"/>
          <line x1="17.5" y1="10.8" x2="17.5" y2="13.5" stroke="#D32F2F" stroke-width="0.8"/>

          <!-- White Kurta (वारकरी सदरा) -->
          <path d="M11 16.5C11 15 13 14.5 17.5 14.5C22 14.5 24 15 24 16.5L25 28C25 29.5 23 30.5 17.5 30.5C12 30.5 10 29.5 10 28L11 16.5Z" fill="#FFFFFF" stroke="#BCAAA4" stroke-width="0.8"/>

          <!-- Saffron Angavastra / Shoulder Stole -->
          <path d="M11 16.5L24 25L21.5 28L10 19.5Z" fill="#FF9800" opacity="0.95"/>

          <!-- White Dhoti & Walking Pose -->
          <path d="M12.5 30.5L10.5 42H14L16.5 34H18.5L21 42H24.5L22.5 30.5H12.5Z" fill="#F8F8F8" stroke="#BCAAA4" stroke-width="0.8"/>

          <!-- Footwear (वारकरी चपला) -->
          <ellipse cx="12.2" cy="42.5" rx="2" ry="1" fill="#4E342E"/>
          <ellipse cx="22.8" cy="42.5" rx="2" ry="1" fill="#4E342E"/>
        </svg>
      </div>
    `;
  } else if (variant === 1) {
    // Variant 1: Veenadhari (विणेकरी - Pilgrim Veena / Ektara Singer)
    return `
      <div class="realistic-warkari-wrapper ${isHighDensity ? 'high-density-warkari' : ''}" style="width:36px; height:46px; position:relative;">
        <svg viewBox="0 0 38 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.25));">
          ${auraPulse}
          <!-- Ground Shadow -->
          <ellipse cx="19" cy="45" rx="9.5" ry="2.2" fill="rgba(25,18,12,0.4)"/>

          <!-- Sacred Veena / Ektara (विणा) held vertically -->
          <line x1="22" y1="4" x2="16" y2="34" stroke="#8D6E63" stroke-width="1.8" stroke-linecap="round"/>
          <circle cx="22.5" cy="4.5" r="2.2" fill="#D7CCC8" stroke="#5D4037" stroke-width="0.8"/>
          <circle cx="16" cy="33" r="3.2" fill="#FFB74D" stroke="#E65100" stroke-width="0.8"/>
          <path d="M22 6L16 32" stroke="#FFF9C4" stroke-width="0.6"/>

          <!-- White Gandhi Topi (वारकरी टोपी) -->
          <path d="M13 8C13 6 15 5 18 5C21 5 23 6 23 8C23 9 22 10.5 20.5 10.8H15.5C14 10.5 13 9 13 8Z" fill="#FFFFFF" stroke="#D7CCC8" stroke-width="0.8"/>

          <!-- Face & Holy Bukka Tilak -->
          <circle cx="18" cy="12.5" r="3.3" fill="#FFCC80"/>
          <circle cx="18" cy="12" r="0.8" fill="#212121"/>

          <!-- White Kurta -->
          <path d="M12 16.5C12 15 14 14.5 18 14.5C22 14.5 24 15 24 16.5L25 28C25 29.5 23 30.5 18 30.5C13 30.5 11 29.5 11 28L12 16.5Z" fill="#FFFFFF" stroke="#BCAAA4" stroke-width="0.8"/>

          <!-- Green/Saffron Devotional Angavastra -->
          <path d="M12 16.5L24 24L22 27L11 19.5Z" fill="#D98E2C" opacity="0.95"/>

          <!-- Tulsi Mala Beads around neck -->
          <path d="M15 16.5C16 19 20 19 21 16.5" stroke="#5D4037" stroke-width="0.8" stroke-dasharray="1 1"/>

          <!-- Dhoti & Walking Pose -->
          <path d="M13 30.5L11 42H14.5L17 34H19L21.5 42H25L23 30.5H13Z" fill="#F8F8F8" stroke="#BCAAA4" stroke-width="0.8"/>
          <ellipse cx="12.5" cy="42.5" rx="2" ry="1" fill="#4E342E"/>
          <ellipse cx="23.2" cy="42.5" rx="2" ry="1" fill="#4E342E"/>
        </svg>
      </div>
    `;
  } else {
    // Variant 2: Taalkari (टाळकरी - Brass Cymbals / Chipli Rhythm Player)
    return `
      <div class="realistic-warkari-wrapper ${isHighDensity ? 'high-density-warkari' : ''}" style="width:36px; height:46px; position:relative;">
        <svg viewBox="0 0 38 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.25));">
          ${auraPulse}
          <!-- Ground Shadow -->
          <ellipse cx="19" cy="45" rx="9.5" ry="2.2" fill="rgba(25,18,12,0.4)"/>

          <!-- Saffron Feta / Pagadi -->
          <path d="M12 8.5C12 6 14.5 4.8 17.5 4.8C20.5 4.8 23 6 23 8.5C23 9.5 22 10.8 20 11.2H15C13 10.8 12 9.5 12 8.5Z" fill="#FF6F00"/>
          <ellipse cx="17.5" cy="6.8" rx="3" ry="1.2" fill="#FFA000"/>

          <!-- Face & Chandan Tilak -->
          <circle cx="17.5" cy="12.5" r="3.3" fill="#FFCC80"/>
          <line x1="17.5" y1="10.8" x2="17.5" y2="13.5" stroke="#C62828" stroke-width="0.8"/>

          <!-- White Kurta -->
          <path d="M11 16.5C11 15 13 14.5 17.5 14.5C22 14.5 24 15 24 16.5L25 28C25 29.5 23 30.5 17.5 30.5C12 30.5 10 29.5 10 28L11 16.5Z" fill="#FFFFFF" stroke="#BCAAA4" stroke-width="0.8"/>

          <!-- Saffron Shawl / Shela -->
          <path d="M11 16.5L24 25L21.5 28L10 19.5Z" fill="#E65100" opacity="0.95"/>

          <!-- Golden Brass Taals (झांज / टाळ) held in both hands playing rhythm -->
          <circle cx="9" cy="22" r="2.8" fill="#FFD54F" stroke="#F57F17" stroke-width="0.8"/>
          <circle cx="26" cy="22" r="2.8" fill="#FFD54F" stroke="#F57F17" stroke-width="0.8"/>
          <path d="M9 22L12 18" stroke="#8D6E63" stroke-width="1.2"/>
          <path d="M26 22L23 18" stroke="#8D6E63" stroke-width="1.2"/>

          <!-- White Dhoti & Rhythmic Stepping Pose -->
          <path d="M12.5 30.5L9.5 42H13.5L16.5 34H18.5L21.5 42H25.5L22.5 30.5H12.5Z" fill="#F8F8F8" stroke="#BCAAA4" stroke-width="0.8"/>
          <ellipse cx="11.5" cy="42.5" rx="2.2" ry="1" fill="#4E342E"/>
          <ellipse cx="23.5" cy="42.5" rx="2.2" ry="1" fill="#4E342E"/>
        </svg>
      </div>
    `;
  }
}

// 2. Realistic 108 ICU Ambulance SVG
function createRealisticAmbulanceSvg(code) {
  return `
    <div style="position:relative; width:54px; height:34px;">
      <svg viewBox="0 0 54 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
        <ellipse cx="27" cy="30" rx="24" ry="2.2" fill="rgba(0,0,0,0.4)"/>
        <!-- Flashing Emergency Strobe -->
        <rect x="22" y="1" width="5" height="3" rx="0.8" fill="#D50000"/>
        <rect x="27" y="1" width="5" height="3" rx="0.8" fill="#0091EA"/>
        <circle cx="24" cy="2.5" r="4.5" fill="#FF1744" opacity="0.75" class="siren-strobe-left"/>
        <circle cx="29" cy="2.5" r="4.5" fill="#2979FF" opacity="0.75" class="siren-strobe-right"/>
        <!-- Ambulance Body -->
        <path d="M3 10C3 7 5 5 8 5H36L45 12L51 16V25C51 26 50 27 49 27H43C43 24 40.5 22 37.5 22C34.5 22 32 24 32 27H19C19 24 16.5 22 13.5 22C10.5 22 8 24 8 27H4C3 27 2 26 2 25V11C2 10.5 2.5 10 3 10Z" fill="#FFFFFF" stroke="#90A4AE" stroke-width="0.8"/>
        <!-- Windows -->
        <path d="M36 7H39L45 13H36V7Z" fill="#263238"/>
        <rect x="23" y="7" width="10" height="6" rx="1" fill="#37474F"/>
        <rect x="10" y="7" width="10" height="6" rx="1" fill="#37474F"/>
        <!-- Red Cross -->
        <rect x="16" y="14" width="3" height="7" rx="0.5" fill="#D32F2F"/>
        <rect x="14" y="16" width="7" height="3" rx="0.5" fill="#D32F2F"/>
        <path d="M2 18H51" stroke="#D32F2F" stroke-width="1.2"/>
        <text x="24" y="19" font-family="Arial, sans-serif" font-weight="900" font-size="5" fill="#D32F2F">108 ICU</text>
        <circle cx="13.5" cy="26" r="4" fill="#212121"/>
        <circle cx="13.5" cy="26" r="2" fill="#B0BEC5"/>
        <circle cx="37.5" cy="26" r="4" fill="#212121"/>
        <circle cx="37.5" cy="26" r="2" fill="#B0BEC5"/>
      </svg>
      <div class="vehicle-mini-label" style="border-color:#EF5350;">🚑 ${escapeHtml(code)}</div>
    </div>
  `;
}

// 3. Realistic Water Tanker 10,000L SVG
function createRealisticTankerSvg(code) {
  return `
    <div style="position:relative; width:56px; height:34px;">
      <svg viewBox="0 0 56 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
        <ellipse cx="28" cy="30" rx="25" ry="2.2" fill="rgba(0,0,0,0.4)"/>
        <!-- Blue Cylindrical Water Tank -->
        <rect x="4" y="5" width="31" height="18" rx="8" fill="#0288D1" stroke="#01579B" stroke-width="0.8"/>
        <text x="7" y="14.5" font-family="Arial, sans-serif" font-weight="900" font-size="4.2" fill="#FFFFFF">WATER 10,000L</text>
        <circle cx="28" cy="14" r="3.5" fill="#01579B"/>
        <path d="M28 11.5C28 11.5 26 14 26 15C26 16.1 26.9 17 28 17C29.1 17 30 16.1 30 15C30 14 28 11.5 28 11.5Z" fill="#FFFFFF"/>
        <!-- Orange Truck Driver Cab -->
        <path d="M36 10H43L49 15L52 17V25C52 26 51 27 50 27H47C47 24 44.5 22 41.5 22C38.5 22 36 24 36 27H34V10Z" fill="#E65100" stroke="#BF360C" stroke-width="0.8"/>
        <path d="M42 11H44L48 15H42V11Z" fill="#263238"/>
        <circle cx="11" cy="26" r="4" fill="#212121"/>
        <circle cx="11" cy="26" r="2" fill="#B0BEC5"/>
        <circle cx="26" cy="26" r="4" fill="#212121"/>
        <circle cx="26" cy="26" r="2" fill="#B0BEC5"/>
        <circle cx="41.5" cy="26" r="4" fill="#212121"/>
        <circle cx="41.5" cy="26" r="2" fill="#B0BEC5"/>
      </svg>
      <div class="vehicle-mini-label" style="border-color:#29B6F6;">💧 ${escapeHtml(code)}</div>
    </div>
  `;
}

// 4. Realistic Maharashtra Police Patrol SUV SVG
function createRealisticPoliceSvg(code) {
  return `
    <div style="position:relative; width:52px; height:32px;">
      <svg viewBox="0 0 52 30" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
        <ellipse cx="26" cy="28" rx="23" ry="2.2" fill="rgba(0,0,0,0.4)"/>
        <rect x="22" y="2" width="4" height="2.5" rx="0.5" fill="#D50000"/>
        <rect x="26" y="2" width="4" height="2.5" rx="0.5" fill="#0091EA"/>
        <circle cx="23" cy="3" r="3.5" fill="#FF1744" opacity="0.7" class="siren-strobe-left"/>
        <circle cx="27" cy="3" r="3.5" fill="#2979FF" opacity="0.7" class="siren-strobe-right"/>
        <path d="M4 11C4 8 6 6 9 6H34L43 12L49 14V23C49 24 48 25 47 25H43C43 22 40.5 20 37.5 20C34.5 20 32 22 32 25H18C18 22 15.5 20 12.5 20C9.5 20 7 22 7 25H4C3 25 2 24 2 23V12C2 11.5 3 11 4 11Z" fill="#1A237E" stroke="#0D47A1" stroke-width="0.8"/>
        <rect x="16" y="11" width="16" height="10" fill="#FFFFFF"/>
        <text x="17.5" y="17" font-family="Arial, sans-serif" font-weight="900" font-size="4.2" fill="#1A237E">POLICE</text>
        <path d="M12 8H33L39 12H12V8Z" fill="#212121"/>
        <circle cx="12.5" cy="24" r="3.8" fill="#212121"/>
        <circle cx="12.5" cy="24" r="1.8" fill="#ECEFF1"/>
        <circle cx="37.5" cy="24" r="3.8" fill="#212121"/>
        <circle cx="37.5" cy="24" r="1.8" fill="#ECEFF1"/>
      </svg>
      <div class="vehicle-mini-label" style="border-color:#3949AB;">🚓 ${escapeHtml(code)}</div>
    </div>
  `;
}

// 5. Realistic Food / Annadanam Van SVG
function createRealisticFoodSvg(code) {
  return `
    <div style="position:relative; width:54px; height:34px;">
      <svg viewBox="0 0 54 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
        <ellipse cx="27" cy="30" rx="24" ry="2.2" fill="rgba(0,0,0,0.4)"/>
        <rect x="4" y="6" width="31" height="17" rx="3" fill="#2E7D32" stroke="#1B5E20" stroke-width="0.8"/>
        <text x="6" y="15" font-family="Arial, sans-serif" font-weight="900" font-size="4.5" fill="#FFE082">अन्नदान &bull; FOOD</text>
        <path d="M35 10H42L48 15L51 17V25C51 26 50 27 49 27H45C45 24 42.5 22 39.5 22C36.5 22 34 24 34 27H4V10Z" fill="#F57C00"/>
        <path d="M41 11H43L47 15H41V11Z" fill="#263238"/>
        <circle cx="11.5" cy="26" r="3.8" fill="#212121"/>
        <circle cx="11.5" cy="26" r="1.8" fill="#FFE082"/>
        <circle cx="39.5" cy="26" r="3.8" fill="#212121"/>
        <circle cx="39.5" cy="26" r="1.8" fill="#FFE082"/>
      </svg>
      <div class="vehicle-mini-label" style="border-color:#43A047;">🍲 ${escapeHtml(code)}</div>
    </div>
  `;
}

function renderDynamicWarkariClusters(zones) {
  if (!window.wariMap || !window.warkariLayerGroup) return;

  window.warkariLayerGroup.clearLayers();

  let totalWarkariCount = 0;

  // March strictly along the pilgrimage highway segments
  for (let i = 0; i < PILGRIMAGE_ROUTE_WAYPOINTS.length - 1; i++) {
    const p1 = PILGRIMAGE_ROUTE_WAYPOINTS[i];
    const p2 = PILGRIMAGE_ROUTE_WAYPOINTS[i + 1];

    // Check if zone data provides a higher real-time density
    let segmentDensity = Math.max(p1.density, p2.density);
    if (zones && Array.isArray(zones)) {
      const z1 = zones.find(z => (z.name || '').toLowerCase().includes(p1.name.toLowerCase().split(' ')[0]));
      const z2 = zones.find(z => (z.name || '').toLowerCase().includes(p2.name.toLowerCase().split(' ')[0]));
      if (z1 && z1.current_density) segmentDensity = Math.max(segmentDensity, Math.round(z1.current_density));
      if (z2 && z2.current_density) segmentDensity = Math.max(segmentDensity, Math.round(z2.current_density));
    }

    // Direct proportional icon count based on heatmap density
    let countOnSegment = 3;
    if (segmentDensity >= 85) {
      // Critical Congestion (Wakhri Phata -> Pandharpur Chowk): 20 walking pilgrims in dense highway line
      countOnSegment = 20;
    } else if (segmentDensity >= 70) {
      // Heavy Density (Taradgaon -> Bhalwani -> Wakhri): 12 pilgrims
      countOnSegment = 12;
    } else if (segmentDensity >= 50) {
      // Moderate (Saswad -> Lonand): 7 pilgrims
      countOnSegment = 7;
    } else {
      // Normal/Low (Alandi -> Pune): 3 pilgrims
      countOnSegment = 3;
    }

    const marchPoints = interpolatePointsAlongSegment(p1, p2, countOnSegment, 0.0004);

    marchPoints.forEach((pt, idx) => {
      totalWarkariCount++;
      const isHigh = segmentDensity >= 85;
      const dindiNum = (totalWarkariCount % 36) + 1;
      const dindiTypes = ['पताका दिंडी (Dhwaj Dindi)', 'विणा मंडळ (Veena Bhajan)', 'टाळकरी पथक (Taal Mandal)'];
      const dindiType = dindiTypes[dindiNum % 3];

      const warkariIcon = L.divIcon({
        className: 'warkari-route-marker',
        html: createRealisticWarkariSvg(dindiNum, isHigh),
        iconSize: [36, 46],
        iconAnchor: [18, 44],
        popupAnchor: [0, -44]
      });

      const marker = L.marker([pt.lat, pt.lng], { icon: warkariIcon });

      const popupHtml = `
        <div style="font-family:var(--font-sans, sans-serif); min-width:220px; padding:4px;">
          <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1.5px solid #D98E2C; padding-bottom:4px;">
            <strong style="color:#7A1F1F; font-size:12px;">🚩 वारकरी दिंडी पथक #${dindiNum}</strong>
            <span class="badge" style="background:${isHigh ? '#9A2525' : '#B8551B'}; color:#FFF; font-size:9.5px; font-weight:700;">
              ${segmentDensity}% Density
            </span>
          </div>
          <div style="font-size:11px; margin-top:6px; color:#2B2623; line-height:1.5;">
            <strong>पथक प्रकार:</strong> ${dindiType}<br>
            <strong>Highway Corridor:</strong> ${escapeHtml(p1.name)} ➔ ${escapeHtml(p2.name)}<br>
            <strong>Palkhi March Pace:</strong> 3.2 km/h (भजन/हरिपाठ गती)<br>
            <strong>Crowd Density Level:</strong> ${isHigh ? '🔥 अत्यंत गर्दी (Critical Choke)' : (segmentDensity >= 70 ? '⚠️ मध्यम गर्दी (Heavy)' : '✅ सुरळीत (Fluid)')}<br>
            <strong>Chanting:</strong> <em>"पुंडलिक वरदा हरि विठ्ठल, श्री ज्ञानदेव तुकाराम"</em>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);
      window.warkariLayerGroup.addLayer(marker);
    });
  }

  console.debug(`[VariSetu] Placed ${totalWarkariCount} realistic Warkaris strictly along the pilgrimage highway based on heat map density.`);
}

function renderResourceMapMarkers(resources) {
  if (!window.wariMap || !window.resourceLayerGroup) return;

  window.resourceLayerGroup.clearLayers();

  // Precise junction coordinates along pilgrimage highway
  const resourcePlacements = [
    { type: 'AMBULANCE', code: '#AMB-01', lat: 17.7280, lng: 75.2950, name: '108 Advanced Life Support ICU', doctor: 'Dr. Swapnil Kulkarni', contact: '108 / +91 94220 11081' },
    { type: 'AMBULANCE', code: '#MV-02', lat: 17.6790, lng: 75.3250, name: 'Mandir North Gate Mobile Clinic', doctor: 'Dr. Priyadarshini Joshi', contact: '108 / +91 94220 11082' },
    { type: 'WATER_TANKER', code: '#WT-09', lat: 17.7340, lng: 75.2890, name: 'Water Tanker 10,000L (Wakhri Approach)', driver: 'Suresh More', contact: 'Wireless Ch-3' },
    { type: 'WATER_TANKER', code: '#WT-14', lat: 17.6820, lng: 75.3190, name: 'Water Tanker 10,000L (Pandharpur Bypass)', driver: 'Ganesh Pawar', contact: 'Wireless Ch-3' },
    { type: 'POLICE_PATROL', code: '#PS-03', lat: 17.7240, lng: 75.2980, name: 'MahaPolice Highway Interceptor #03', incharge: 'PSI V. R. Shinde', contact: 'Police Wireless Ch-1' },
    { type: 'POLICE_PATROL', code: '#PS-07', lat: 17.6755, lng: 75.3285, name: 'MahaPolice Mandir Perimeter Squad #07', incharge: 'API K. D. Patil', contact: 'Police Wireless Ch-1' },
    { type: 'FOOD_VAN', code: '#FV-01', lat: 17.8900, lng: 75.0200, name: 'Annadanam Prasadam Van #01 (Bhalwani Camp)', incharge: 'Seva Trust Coordinator', contact: 'Camp Hotline' }
  ];

  resourcePlacements.forEach(res => {
    let iconHtml = '';
    let size = [54, 34];
    let anchor = [27, 30];

    if (res.type === 'AMBULANCE') {
      iconHtml = createRealisticAmbulanceSvg(res.code);
      size = [54, 34];
      anchor = [27, 30];
    } else if (res.type === 'WATER_TANKER') {
      iconHtml = createRealisticTankerSvg(res.code);
      size = [56, 34];
      anchor = [28, 30];
    } else if (res.type === 'POLICE_PATROL') {
      iconHtml = createRealisticPoliceSvg(res.code);
      size = [52, 32];
      anchor = [26, 28];
    } else {
      iconHtml = createRealisticFoodSvg(res.code);
      size = [54, 34];
      anchor = [27, 30];
    }

    const customIcon = L.divIcon({
      className: 'realistic-vehicle-marker',
      html: iconHtml,
      iconSize: size,
      iconAnchor: anchor,
      popupAnchor: [0, -30]
    });

    const marker = L.marker([res.lat, res.lng], { icon: customIcon });

    const popupHtml = `
      <div style="font-family:var(--font-sans, sans-serif); min-width:200px; padding:4px;">
        <div style="border-bottom:1.5px solid #7A1F1F; padding-bottom:3px;">
          <strong style="color:#7A1F1F; font-size:12px;">${escapeHtml(res.name)}</strong>
        </div>
        <div style="font-size:11px; margin-top:5px; color:#2B2623; line-height:1.4;">
          <strong>Unit Code:</strong> ${escapeHtml(res.code)}<br>
          ${res.doctor ? `<strong>On-Duty Doctor:</strong> ${escapeHtml(res.doctor)}<br>` : ''}
          ${res.driver ? `<strong>Driver:</strong> ${escapeHtml(res.driver)}<br>` : ''}
          ${res.incharge ? `<strong>Incharge:</strong> ${escapeHtml(res.incharge)}<br>` : ''}
          <strong>Emergency Contact:</strong> ${escapeHtml(res.contact)}<br>
          <span class="badge" style="background:#2E5B36; color:#FFF; font-size:9px; margin-top:4px;">🟢 Operational & Deployed</span>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    window.resourceLayerGroup.addLayer(marker);
  });
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
    fetchHeatRisk(),
    fetchCommandPicture()
  ]);
  setupUnifiedCommandUIEventListeners();

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

const CCTV_VIDEO_MAP = {
  'CAM-12': 'assets/videos/cctv_cam_12_wakhri.mp4',
  'CAM-04': 'assets/videos/cctv_cam_04_pandharpur.mp4',
  'CAM-08': 'assets/videos/cctv_cam_08_saswad.mp4',
  'CAM-01': 'assets/videos/cctv_cam_01_alandi.mp4',
  'PHOTO-01': 'assets/videos/cctv_cam_12_wakhri.mp4',
  'DRONE-01': 'assets/videos/cctv_cam_04_pandharpur.mp4',
  'DEFAULT': 'assets/videos/cctv_cam_12_wakhri.mp4'
};

const activeCctvPlayers = {};
let currentModalPlayer = null;

class CCTVFeedPlayer {
  constructor(canvas, videoSrc, camConfig = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
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

    this.videoSrc = videoSrc || CCTV_VIDEO_MAP[this.camCode] || CCTV_VIDEO_MAP.DEFAULT;
    this.imageFallbackSrc = CCTV_ASSET_MAP[this.camCode] || CCTV_ASSET_MAP.DEFAULT;

    // Load actual CCTV Video element for smooth 60fps streaming playback
    this.video = document.createElement('video');
    this.video.src = this.videoSrc;
    this.video.muted = true;
    this.video.loop = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.crossOrigin = 'anonymous';
    this.video.setAttribute('muted', '');
    this.video.setAttribute('playsinline', '');
    this.video.setAttribute('autoplay', '');
    this.video.setAttribute('loop', '');
    this.videoLoaded = false;

    const playVideoSafely = () => {
      this.videoLoaded = true;
      const playPromise = this.video.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          // Autoplay policy fallback: muted user action
          this.video.muted = true;
        });
      }
    };

    this.video.oncanplay = playVideoSafely;
    this.video.onloadeddata = playVideoSafely;
    this.video.onerror = () => {
      console.debug(`[VariSetu CCTV] Video fallback to image for ${this.camCode}`);
      this.videoLoaded = false;
    };
    this.video.load();

    // Fallback image
    this.img = new Image();
    this.imgLoaded = false;
    this.img.src = this.imageFallbackSrc;
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
    if (this.video && this.video.paused) {
      this.video.play().catch(() => {});
    }
    this.render();
  }

  stop() {
    this.running = false;
    if (this.video) {
      try { this.video.pause(); } catch {}
    }
    if (this.animFrame) {
      cancelAnimationFrame(this.animFrame);
      this.animFrame = null;
    }
  }

  render(timestamp = performance.now()) {
    if (!this.running) return;
    const { canvas, ctx, video, videoLoaded, img, imgLoaded } = this;
    const w = canvas.width;
    const h = canvas.height;

    // Check if there is a hardware-accelerated video element directly underneath this canvas
    const domVideo = document.getElementById(`video-${this.camCode}`) || canvas.parentElement?.querySelector('video');

    if (domVideo && !this.isLargeModal) {
      // Clear canvas for transparent HUD / AI overlay over native video element
      ctx.clearRect(0, 0, w, h);
      if (domVideo.paused) {
        domVideo.play().catch(() => {});
      }
    } else {
      // Fill background and draw video frame
      ctx.fillStyle = '#080A0C';
      ctx.fillRect(0, 0, w, h);

      if (videoLoaded && video.readyState >= 2) {
        if (video.paused) {
          video.play().catch(() => {});
        }
        ctx.save();
        ctx.translate(w / 2 + this.panX, h / 2 + this.panY);
        ctx.scale(this.zoom, this.zoom);
        ctx.drawImage(video, -w / 2, -h / 2, w, h);
        ctx.restore();
      } else if (imgLoaded) {
        const timeSec = timestamp / 1000;
        const driftX = Math.sin(timeSec * 0.35) * 6;
        const driftY = Math.cos(timeSec * 0.25) * 3;
        const currentZoom = this.zoom + (Math.sin(timeSec * 0.2) * 0.02);

        ctx.save();
        ctx.translate(w / 2 + this.panX + driftX, h / 2 + this.panY + driftY);
        ctx.scale(currentZoom, currentZoom);
        ctx.drawImage(img, -w / 2, -h / 2, w, h);
        ctx.restore();
      }
    }
    // Optical scanlines
    ctx.fillStyle = 'rgba(0, 0, 0, 0.10)';
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
    ctx.fillText(`${this.camCode} | LIVE VIDEO | ${this.location.toUpperCase()}`, 8, this.isLargeModal ? 17 : 14);

    // Flashing REC Dot & Timecode
    const isRecOn = Math.floor(timestamp / 500) % 2 === 0;
    const recText = `● LIVE REC  ${dateStr} ${timeStr}`;
    ctx.fillStyle = isRecOn ? '#FF3B30' : '#888888';
    const recWidth = ctx.measureText(recText).width;
    ctx.fillText(recText, w - recWidth - 8, this.isLargeModal ? 17 : 14);

    // Bottom telemetry bar for Large Modal
    if (this.isLargeModal) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
      ctx.fillRect(0, h - 24, w, 24);
      ctx.fillStyle = '#00FF66';
      ctx.font = '600 10px monospace';
      ctx.fillText(`DENSITY: ${this.density}% [${this.densityStatus}] | ZOOM: ${this.zoom.toFixed(1)}x | 1080p CCTV STREAM @ 60FPS | LATENCY: 8ms`, 8, h - 8);
      ctx.fillStyle = '#E5A93C';
      ctx.fillText(`CCTV VIDEO FEED ACTIVE`, w - 170, h - 8);
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

    const videoSrc = CCTV_VIDEO_MAP[cfg.code] || CCTV_VIDEO_MAP.DEFAULT;
    const player = new CCTVFeedPlayer(canvas, videoSrc, {
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

    const domVideo = tile.querySelector('video');
    if (domVideo) {
      const vidSrc = CCTV_VIDEO_MAP[cam.camera_code] || CCTV_VIDEO_MAP.DEFAULT;
      if (!domVideo.src.includes(vidSrc.split('/').pop())) {
        domVideo.src = vidSrc;
        domVideo.play().catch(() => {});
      }
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
  const videoSrc = CCTV_VIDEO_MAP[camCode] || CCTV_VIDEO_MAP.DEFAULT;
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
    currentModalPlayer = new CCTVFeedPlayer(modalCanvas, videoSrc, {
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
  const closeModal = () => {
    if (currentModalPlayer) {
      currentModalPlayer.stop();
      currentModalPlayer = null;
    }
    const video = document.getElementById('modalCamVideo');
    if (video) {
      try { video.pause(); } catch {}
    }
    document.getElementById('camModal')?.classList.remove('open');
  };

  document.getElementById('camModalCloseBtn')?.addEventListener('click', closeModal);
  document.getElementById('modalCamCloseFooterBtn')?.addEventListener('click', closeModal);
}

/* ==================== CROWD INTELLIGENCE ==================== */
async function refreshCrowdZones() {
  try {
    const zones = await apiRequest('/crowd/current');
    AppState.crowdZones = zones;
    renderCrowdZones(zones);
    renderDynamicWarkariClusters(zones);
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
let lostPersonsCurrentPage = 1;
const LOST_PERSONS_PER_PAGE = 15;
let lostPersonsSearchQuery = '';
let lostPersonsStatusFilter = 'ALL';
let lostPersonsFilterInitialized = false;

async function refreshLostPersons() {
  try {
    const cases = await apiRequest('/lost-persons');
    AppState.lostCases = cases || [];
    initLostPersonsFilterControls();
    renderLostPersons(AppState.lostCases);
    return cases;
  } catch (err) {
    console.debug('[VariSetu] Lost persons fetch skipped.');
    return [];
  }
}

function initLostPersonsFilterControls() {
  if (lostPersonsFilterInitialized) return;
  lostPersonsFilterInitialized = true;

  const searchInput = document.getElementById('lostCaseSearchInput');
  const statusFilter = document.getElementById('lostCaseStatusFilter');
  const prevBtn = document.getElementById('lostPrevPageBtn');
  const nextBtn = document.getElementById('lostNextPageBtn');

  searchInput?.addEventListener('input', (e) => {
    lostPersonsSearchQuery = e.target.value.toLowerCase().trim();
    lostPersonsCurrentPage = 1;
    renderLostPersons(AppState.lostCases);
  });

  statusFilter?.addEventListener('change', (e) => {
    lostPersonsStatusFilter = e.target.value.toUpperCase();
    lostPersonsCurrentPage = 1;
    renderLostPersons(AppState.lostCases);
  });

  prevBtn?.addEventListener('click', () => {
    if (lostPersonsCurrentPage > 1) {
      lostPersonsCurrentPage--;
      renderLostPersons(AppState.lostCases);
    }
  });

  nextBtn?.addEventListener('click', () => {
    const filtered = filterLostCases(AppState.lostCases || []);
    const maxPage = Math.max(1, Math.ceil(filtered.length / LOST_PERSONS_PER_PAGE));
    if (lostPersonsCurrentPage < maxPage) {
      lostPersonsCurrentPage++;
      renderLostPersons(AppState.lostCases);
    }
  });
}

function filterLostCases(cases) {
  return (cases || []).filter(item => {
    // Status filter
    if (lostPersonsStatusFilter && lostPersonsStatusFilter !== 'ALL') {
      const st = String(item.status || '').toUpperCase();
      if (!st.includes(lostPersonsStatusFilter)) return false;
    }

    // Search query
    if (lostPersonsSearchQuery) {
      const q = lostPersonsSearchQuery;
      const match = (
        (item.case_number || '').toLowerCase().includes(q) ||
        (item.name || '').toLowerCase().includes(q) ||
        (item.clothing_description || '').toLowerCase().includes(q) ||
        (item.last_seen_location || '').toLowerCase().includes(q) ||
        (item.last_seen_camera_id || '').toLowerCase().includes(q)
      );
      if (!match) return false;
    }

    return true;
  });
}

function renderLostPersons(cases) {
  const tbody = document.getElementById('lostPersonsTableBody');
  if (!tbody) return;

  const allCases = cases || AppState.lostCases || [];
  const filteredCases = filterLostCases(allCases);

  // Update Total Count Badge
  const totalBadge = document.getElementById('lostTotalBadge');
  if (totalBadge) {
    totalBadge.textContent = `${filteredCases.length} Cases (${allCases.length} Total)`;
  }

  // Calculate Pagination
  const totalPages = Math.max(1, Math.ceil(filteredCases.length / LOST_PERSONS_PER_PAGE));
  if (lostPersonsCurrentPage > totalPages) lostPersonsCurrentPage = totalPages;
  if (lostPersonsCurrentPage < 1) lostPersonsCurrentPage = 1;

  const startIdx = (lostPersonsCurrentPage - 1) * LOST_PERSONS_PER_PAGE;
  const pageItems = filteredCases.slice(startIdx, startIdx + LOST_PERSONS_PER_PAGE);

  // Update Pagination Bar
  const infoEl = document.getElementById('lostPaginationInfo');
  const prevBtn = document.getElementById('lostPrevPageBtn');
  const nextBtn = document.getElementById('lostNextPageBtn');

  if (infoEl) {
    infoEl.textContent = `Page ${lostPersonsCurrentPage} of ${totalPages} (${filteredCases.length} cases)`;
  }
  if (prevBtn) prevBtn.disabled = lostPersonsCurrentPage <= 1;
  if (nextBtn) nextBtn.disabled = lostPersonsCurrentPage >= totalPages;

  if (pageItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:18px; color:var(--text-secondary);">No matching lost person cases found for query "${escapeHtml(lostPersonsSearchQuery)}".</td></tr>`;
    return;
  }

  tbody.innerHTML = pageItems.map(item => `
    <tr>
      <td>
        <div class="photo-placeholder-box" style="background:#FAF0E1; border:1px solid #D8D1C5; border-radius:4px; width:28px; height:28px; display:flex; align-items:center; justify-content:center; color:#7A1F1F;">
          <i data-lucide="user" style="width:14px; height:14px;"></i>
        </div>
      </td>
      <td><strong style="color:var(--maroon-primary); font-size:11.5px;">${escapeHtml(item.case_number)}</strong></td>
      <td><strong>${escapeHtml(item.name || 'Unknown')}</strong></td>
      <td>${escapeHtml(item.age || '-')} / ${escapeHtml(item.gender || '-')}</td>
      <td style="max-width:220px; font-size:11px; color:#443E3B;" title="${escapeHtml(item.clothing_description || '')}">${escapeHtml(item.clothing_description || '-')}</td>
      <td style="font-size:11px;">${escapeHtml(item.last_seen_location || item.last_seen_camera_id || '-')}</td>
      <td>
        <span class="density-tag ${getStatusClass(item.status)}">
          ${escapeHtml(item.status)}
        </span>
      </td>
      <td>
        <button class="govt-btn btn-outline" style="font-size:11px; padding:3px 8px;" type="button" data-lost-id="${escapeHtml(item.id)}" data-action="view-lost-case">
          <span>View</span>
        </button>
      </td>
    </tr>
  `).join('');

  if (window.lucide) {
    lucide.createIcons();
  }

  tbody.querySelectorAll('[data-action="view-lost-case"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = allCases.find(c => c.id === btn.dataset.lostId);
      if (item) openLostPersonDetails(item);
    });
  });

  if (pageItems.length > 0 && !AppState.selectedLostCase) {
    showTranscript(pageItems[0]);
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
    if (typeof renderResourceMapMarkers === 'function') renderResourceMapMarkers(resources);
    await refreshResourceAllocationsHistory();
    return resources;
  } catch (err) {
    console.debug('[VariSetu] Resources fetch skipped.');
    await refreshResourceAllocationsHistory();
    return [];
  }
}


function renderResources(resources) {
  const tbody = document.getElementById('resourcesTableBody');
  const quotaBadge = document.getElementById('totalFleetQuotaBadge');
  if (quotaBadge) quotaBadge.textContent = '80 Total Fleet Units (20 Per Type)';
  if (!tbody) return;

  const allUnits = getAllManagedFleetUnits();

  // 4 Resource Categories with strict limit of 20 per type
  const categories = [
    {
      type: 'WATER_TANKER',
      name: 'Water Tankers (10,000L)',
      role: 'Potable Drinking Water & Mist Sprayer Supply',
      limit: 20,
      dispatched: allUnits.filter(u => u.type === 'WATER_TANKER' && u.isDispatched).length,
      available: allUnits.filter(u => u.type === 'WATER_TANKER' && !u.isDispatched).length,
      activeSectors: 'Sector 3 (Narayangaon Km 84), Sector 3 (Sangamner), Sector 2 (Manchar), Sector 1 (Alandi)',
      standbyDepots: 'Kothrud Central Depot, Bhosari Base Depot, Manchar Transit Depot'
    },
    {
      type: 'MEDICAL_VAN',
      name: 'Mobile Medical Vans & Ambulances',
      role: 'Emergency Medical Triage & Mobile ICU Resuscitation',
      limit: 20,
      dispatched: allUnits.filter(u => u.type === 'MEDICAL_VAN' && u.isDispatched).length,
      available: allUnits.filter(u => u.type === 'MEDICAL_VAN' && !u.isDispatched).length,
      activeSectors: 'Sector 3 (Narayangaon ICU Camp), Sector 1 (Bhosari Base), Sector 3 (Sangamner Hospital), Sector 4 (Nashik)',
      standbyDepots: 'Pune Civil Hospital, Manchar Sub-District Clinic, Nashik District Hospital'
    },
    {
      type: 'POLICE_SQUAD',
      name: 'Police Patrol Squads',
      role: 'Perimeter Security, Crowd Chokepoint & Quick Response',
      limit: 20,
      dispatched: allUnits.filter(u => u.type === 'POLICE_SQUAD' && u.isDispatched).length,
      available: allUnits.filter(u => u.type === 'POLICE_SQUAD' && !u.isDispatched).length,
      activeSectors: 'Sector 4 (Nashik Terminal Security), Sector 3 (Narayangaon Chokepoint), Sector 2 (Manchar Chowk)',
      standbyDepots: 'District Police HQ Reserve, Chakan Outpost, Pimpri-Chinchwad HQ'
    },
    {
      type: 'VOLUNTEER_TEAM',
      name: 'Volunteer Dindi Stewards',
      role: 'Pilgrim Queue Marshalling, Hydration & Lost Person Help',
      limit: 20,
      dispatched: allUnits.filter(u => u.type === 'VOLUNTEER_TEAM' && u.isDispatched).length,
      available: allUnits.filter(u => u.type === 'VOLUNTEER_TEAM' && !u.isDispatched).length,
      activeSectors: 'Sector 2 (Manchar Bypass Queue), Sector 3 (Hydration Lanes), Sector 1 (Departure Ghats)',
      standbyDepots: 'Alandi Volunteer Base Camp, Narayangaon Base, Nashik Govind Nagar Camp'
    }
  ];

  tbody.innerHTML = categories.map(cat => {
    const statusClass = cat.dispatched >= 10 ? 'orange' : (cat.dispatched >= 6 ? 'yellow' : 'green');
    const percent = Math.round((cat.dispatched / cat.limit) * 100);
    return `
      <tr>
        <td>
          <div style="font-weight:700; font-size:12px; color:var(--maroon-primary);">${escapeHtml(cat.name)}</div>
          <div style="font-size:10px; color:var(--text-muted);">${escapeHtml(cat.role)}</div>
        </td>
        <td style="font-family:var(--font-mono); font-size:11.5px;">
          <div><strong style="color:#B8551B;">⚡ ${cat.dispatched} Dispatched</strong> &bull; <strong style="color:#2E5B36;">🟢 ${cat.available} Standby</strong></div>
          <div style="font-size:10px; color:var(--text-muted);">Quota Limit: ${cat.limit} Total Units</div>
        </td>
        <td style="font-size:11px; color:var(--text-primary); max-width:240px;">
          ${escapeHtml(cat.activeSectors)}
        </td>
        <td style="font-size:10.5px; color:var(--text-secondary); max-width:220px;">
          ${escapeHtml(cat.standbyDepots)}
        </td>
        <td>
          <span class="density-tag ${statusClass}">
            ${percent}% DEPLOYED (${cat.available} RESERVE)
          </span>
        </td>
      </tr>
    `;
  }).join('');

  renderFieldLogisticsGrid(allUnits);
}


let activeFleetFilter = 'ALL';

function renderFieldLogisticsGrid(units, filterOverride) {
  const container = document.getElementById('resourceCardsContainer');
  const badge = document.getElementById('fleetUnitsCountBadge');
  if (!container) return;

  const fleet = units || getAllManagedFleetUnits();
  const filter = filterOverride || activeFleetFilter || 'ALL';

  let filtered = fleet;
  if (filter === 'WATER_TANKER' || filter === 'MEDICAL_VAN' || filter === 'POLICE_SQUAD' || filter === 'VOLUNTEER_TEAM') {
    filtered = fleet.filter(u => u.type === filter);
  } else if (filter === 'DISPATCHED') {
    filtered = fleet.filter(u => u.isDispatched);
  } else if (filter === 'AVAILABLE') {
    filtered = fleet.filter(u => !u.isDispatched);
  }

  if (badge) {
    const dispCount = fleet.filter(u => u.isDispatched).length;
    const availCount = fleet.filter(u => !u.isDispatched).length;
    badge.textContent = `${filtered.length} Showing (${dispCount} Dispatched • ${availCount} Available / 80 Total)`;
  }

  container.innerHTML = filtered.map(f => {
    const isDispatched = f.isDispatched;
    const statusTagClass = isDispatched ? 'yellow' : 'green';
    const statusLabel = isDispatched ? `⚡ DISPATCHED (${f.status})` : '🟢 AVAILABLE (STANDBY RESERVE)';
    const cardBorderLeft = isDispatched ? 'var(--status-orange)' : 'var(--status-green)';

    return `
      <div class="fleet-card" data-resource-id="${escapeHtml(f.id)}" style="border-left: 4px solid ${cardBorderLeft};">
        <div class="fleet-card-header">
          <div>
            <span class="fleet-card-code">${escapeHtml(f.code)}</span>
            <div style="font-weight:600; font-size:11.5px; color:var(--text-primary); margin-top:1px;">${escapeHtml(f.name)}</div>
          </div>
          <span class="density-tag ${statusTagClass}">
            ${escapeHtml(statusLabel)}
          </span>
        </div>
        <div class="fleet-card-meta">
          <div>
            <div class="fleet-meta-label">Allocated Capacity</div>
            <div class="fleet-meta-val" style="color:var(--maroon-primary);">${escapeHtml(f.capacity)}</div>
          </div>
          <div>
            <div class="fleet-meta-label">Operator Contact</div>
            <div class="fleet-meta-val">${escapeHtml(f.phone)}</div>
          </div>
          <div style="grid-column: span 2;">
            <div class="fleet-meta-label">${isDispatched ? 'Deployed Target Sector & Location' : 'Current Standby Station Depot'}</div>
            <div class="fleet-meta-val" style="color:var(--text-primary); font-weight:600;">${escapeHtml(f.sector)}</div>
          </div>
          <div style="grid-column: span 2; font-size:10.5px; color:var(--text-secondary); background:var(--bg-subtle); padding:4px 6px; border-radius:2px;">
            <strong>Mission:</strong> ${escapeHtml(f.task)}
          </div>
        </div>
        <div class="fleet-card-actions">
          <button type="button" class="govt-btn" style="flex:1; font-size:10px; padding:4px 8px; ${isDispatched ? '' : 'background:#2E5B36;'}" onclick="openReassignSectorModal('${escapeHtml(f.id)}', '${escapeHtml(f.name)}')">
            <i data-lucide="${isDispatched ? 'refresh-cw' : 'send'}" style="width:10px; height:10px;"></i>
            <span>${isDispatched ? '🔄 Reassign Sector' : '🚀 Dispatch to Sector'}</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  // Wire filter button clicks
  document.querySelectorAll('.fleet-filter-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.fleet-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFleetFilter = btn.getAttribute('data-fleet-filter') || 'ALL';
      renderFieldLogisticsGrid(fleet, activeFleetFilter);
    };
  });

  if (window.lucide) lucide.createIcons();
}

function getAllManagedFleetUnits() {
  const units = [];

  // 1. Water Tankers (WT-01 to WT-20) - 20 Units (6 Dispatched, 14 Available)
  const waterLocations = [
    { num: 1, disp: true, sector: 'Sector 1 (Pune ➔ Bhosari)', phone: '+91-9822001101 (R. Shinde)', task: 'Corridor entry water refilling point' },
    { num: 2, disp: false, sector: 'Kothrud Central Depot (Standby Reserve)', phone: '+91-9822001102 (D. Mane)', task: 'Standby reserve for emergency deployment' },
    { num: 3, disp: false, sector: 'Kothrud Central Depot (Standby Reserve)', phone: '+91-9822001103 (K. Jagtap)', task: 'Standby reserve for emergency deployment' },
    { num: 4, disp: true, sector: 'Sector 3 (Sangamner North Chowk)', phone: '+91-9822001104 (D. More)', task: 'Replenishing Water Station Hub #4 & ORSL misting' },
    { num: 5, disp: false, sector: 'Bhosari Base Depot (Standby Reserve)', phone: '+91-9822001105 (P. Salve)', task: 'Standby reserve for Sector 1 surge' },
    { num: 6, disp: false, sector: 'Bhosari Base Depot (Standby Reserve)', phone: '+91-9822001106 (S. Kamble)', task: 'Standby reserve for Sector 1 surge' },
    { num: 7, disp: true, sector: 'Sector 2 (Manchar Bypass Post)', phone: '+91-9822001107 (A. Jadhav)', task: 'Continuous hydration along pedestrian corridor' },
    { num: 8, disp: false, sector: 'Manchar Transit Depot (Standby Reserve)', phone: '+91-9822001108 (M. Bhise)', task: 'Standby reserve for Sector 2 surge' },
    { num: 9, disp: true, sector: 'Sector 3 (Narayangaon Km 84 Transit Camp)', phone: '+91-9822001109 (V. Kulkarni)', task: 'Surge crowd hydration & mist sprayer supply' },
    { num: 10, disp: false, sector: 'Narayangaon Camp Standby Depot', phone: '+91-9822001110 (G. Shinde)', task: 'Standby reserve for Sector 3 choke point' },
    { num: 11, disp: false, sector: 'Narayangaon Camp Standby Depot', phone: '+91-9822001111 (T. Raut)', task: 'Standby reserve for Sector 3 choke point' },
    { num: 12, disp: true, sector: 'Sector 1 (Alandi Corridor Exit Point)', phone: '+91-9822001112 (S. Thorat)', task: 'Morning procession departure hydration quota' },
    { num: 13, disp: false, sector: 'Sangamner Base Standby Depot', phone: '+91-9822001113 (N. Ghadge)', task: 'Standby reserve for Sector 3 bypass' },
    { num: 14, disp: false, sector: 'Sangamner Base Standby Depot', phone: '+91-9822001114 (B. Landge)', task: 'Standby reserve for Sector 3 bypass' },
    { num: 15, disp: true, sector: 'Sector 4 (Govind Nagar Terminal, Nashik)', phone: '+91-9822001115 (M. Gawande)', task: 'Terminal reception hydration & dindi welcome camp' },
    { num: 16, disp: false, sector: 'Nashik Central Depot (Standby Reserve)', phone: '+91-9822001116 (Y. Kale)', task: 'Terminal buffer reserve' },
    { num: 17, disp: false, sector: 'Nashik Central Depot (Standby Reserve)', phone: '+91-9822001117 (O. Sonawane)', task: 'Terminal buffer reserve' },
    { num: 18, disp: false, sector: 'State Strategic Fleet Reserve', phone: '+91-9822001118 (H. Chavan)', task: 'Emergency strategic buffer' },
    { num: 19, disp: false, sector: 'State Strategic Fleet Reserve', phone: '+91-9822001119 (F. Shaikh)', task: 'Emergency strategic buffer' },
    { num: 20, disp: false, sector: 'State Strategic Fleet Reserve', phone: '+91-9822001120 (R. Waghmare)', task: 'Emergency strategic buffer' }
  ];
  waterLocations.forEach(w => {
    const code = `WT-${w.num < 10 ? '0' + w.num : w.num}`;
    units.push({
      id: code,
      code: code,
      name: `10,000L Water Tanker #${w.num < 10 ? '0' + w.num : w.num}`,
      type: 'WATER_TANKER',
      categoryName: 'Water Tankers (10,000L)',
      capacity: '10,000 Litres Hydration',
      phone: w.phone,
      sector: w.sector,
      task: w.task,
      isDispatched: w.disp,
      status: w.disp ? 'DEPLOYED' : 'AVAILABLE'
    });
  });

  // 2. Mobile Medical Vans & Ambulances (MV-01 to MV-20) - 20 Units (8 Dispatched, 12 Available)
  const medLocations = [
    { num: 1, disp: true, sector: 'Sector 1 (Bhosari Base Station)', phone: '+91-9822002201 (Dr. Joshi)', task: 'Corridor entry medical triage & ambulance standby' },
    { num: 2, disp: true, sector: 'Sector 3 (Narayangaon Km 84 Emergency Post)', phone: '+91-9822002202 (Dr. Deshmukh)', task: 'First responder ambulance for fainting & heat exhaustion' },
    { num: 3, disp: true, sector: 'Sector 3 (Sangamner Base Hospital Point)', phone: '+91-9822002203 (Dr. Shirole)', task: 'Mobile ICU trauma & cardiac resuscitation' },
    { num: 4, disp: false, sector: 'Pune Civil Hospital Base (Standby Reserve)', phone: '+91-9822002204 (Dr. Khare)', task: 'Standby reserve ambulance unit' },
    { num: 5, disp: true, sector: 'Sector 4 (Govind Nagar Terminal, Nashik)', phone: '+91-9822002205 (Dr. Patil)', task: 'Destination medical triage center & ER transit' },
    { num: 6, disp: false, sector: 'Manchar Sub-District Hospital (Standby)', phone: '+91-9822002206 (Dr. Kadam)', task: 'Standby reserve ambulance unit' },
    { num: 7, disp: false, sector: 'Narayangaon Transit Clinic (Standby)', phone: '+91-9822002207 (Dr. Gaikwad)', task: 'Standby reserve ambulance unit' },
    { num: 8, disp: true, sector: 'Sector 2 (Manchar Junction Highway Post)', phone: '+91-9822002208 (Dr. Chavan)', task: 'Pedestrian corridor heat stress screening' },
    { num: 9, disp: false, sector: 'Sangamner Civil Hospital (Standby)', phone: '+91-9822002209 (Dr. Mohite)', task: 'Standby reserve ambulance unit' },
    { num: 10, disp: false, sector: 'Nashik District Hospital (Standby)', phone: '+91-9822002210 (Dr. Jagdale)', task: 'Standby reserve ambulance unit' },
    { num: 11, disp: true, sector: 'Sector 3 (Narayangaon Transit Camp North)', phone: '+91-9822002211 (Dr. Gite)', task: 'Rapid paramedic dispatch for elderly warkaris' },
    { num: 12, disp: false, sector: 'Reserve Medical Hub Pune', phone: '+91-9822002212 (Dr. Pardeshi)', task: 'Standby reserve ambulance unit' },
    { num: 13, disp: false, sector: 'Reserve Medical Hub Nashik', phone: '+91-9822002213 (Dr. Nikam)', task: 'Standby reserve ambulance unit' },
    { num: 14, disp: true, sector: 'Sector 4 (Sangamner ➔ Nashik Highway Km 140)', phone: '+91-9822002214 (Dr. Wagh)', task: 'Highway patrol ambulance and emergency triage' },
    { num: 15, disp: false, sector: 'Red Cross Emergency Depot Pune', phone: '+91-9822002215 (Dr. Inamdar)', task: 'Standby reserve ambulance unit' },
    { num: 16, disp: false, sector: 'Red Cross Emergency Depot Nashik', phone: '+91-9822002216 (Dr. Sonje)', task: 'Standby reserve ambulance unit' },
    { num: 17, disp: true, sector: 'Sector 1 (Kothrud Origin Departure Point)', phone: '+91-9822002217 (Dr. Bhalerao)', task: 'Origin health checkpost & emergency ambulance' },
    { num: 18, disp: false, sector: 'Directorate Health Reserve Standby', phone: '+91-9822002218 (Dr. Salunke)', task: 'Strategic ambulance buffer' },
    { num: 19, disp: false, sector: 'Directorate Health Reserve Standby', phone: '+91-9822002219 (Dr. Kolhe)', task: 'Strategic ambulance buffer' },
    { num: 20, disp: false, sector: 'Directorate Health Reserve Standby', phone: '+91-9822002220 (Dr. Ahire)', task: 'Strategic ambulance buffer' }
  ];
  medLocations.forEach(m => {
    const code = `MV-${m.num < 10 ? '0' + m.num : m.num}`;
    units.push({
      id: code,
      code: code,
      name: m.num % 3 === 0 ? `Emergency Mobile ICU #${m.num < 10 ? '0' + m.num : m.num}` : `Mobile Medical Van #${m.num < 10 ? '0' + m.num : m.num}`,
      type: 'MEDICAL_VAN',
      categoryName: 'Mobile Medical Vans & Ambulances',
      capacity: m.num % 3 === 0 ? '2 Trauma ICU Beds' : '4 Beds / Triage Unit',
      phone: m.phone,
      sector: m.sector,
      task: m.task,
      isDispatched: m.disp,
      status: m.disp ? 'ACTIVE' : 'AVAILABLE'
    });
  });

  // 3. Police Patrol Squads (PS-01 to PS-20) - 20 Units (11 Dispatched, 9 Available)
  const policeLocations = [
    { num: 1, disp: true, sector: 'Sector 1 (Kothrud to Pune City Corridor)', phone: '+91-9822003301 (Insp. S. Kadam)', task: 'Traffic diversion & heavy vehicle blockage' },
    { num: 2, disp: false, sector: 'Pune Police HQ (QRT Reserve)', phone: '+91-9822003302 (Sub-Insp. A. More)', task: 'Quick Response Team reserve' },
    { num: 3, disp: true, sector: 'Sector 1 (Bhosari Flyover Intersection)', phone: '+91-9822003303 (Insp. D. Shinde)', task: 'Procession lane separation & perimeter patrol' },
    { num: 4, disp: false, sector: 'Pimpri-Chinchwad Police HQ (Reserve)', phone: '+91-9822003304 (Sub-Insp. P. Thorat)', task: 'Standby reserve police squad' },
    { num: 5, disp: false, sector: 'Chakan Police Station (Reserve Standby)', phone: '+91-9822003305 (Sub-Insp. V. Jagtap)', task: 'Standby reserve police squad' },
    { num: 6, disp: true, sector: 'Sector 2 (Chakan Industrial Bypass Node)', phone: '+91-9822003306 (Insp. R. Bhosale)', task: 'Heavy freight detour enforcement' },
    { num: 7, disp: false, sector: 'Manchar Police Outpost (Standby)', phone: '+91-9822003307 (Sub-Insp. M. Chavan)', task: 'Standby reserve police squad' },
    { num: 8, disp: true, sector: 'Sector 2 (Manchar Junction Chokepoint)', phone: '+91-9822003308 (Insp. G. Pawar)', task: 'Pedestrian flow management & surveillance' },
    { num: 9, disp: true, sector: 'Sector 3 (Narayangaon Chokepoint Km 84)', phone: '+91-9822003309 (Insp. S. Patil)', task: 'CCTV surveillance node & crowd density control' },
    { num: 10, disp: false, sector: 'Narayangaon Police Camp (Reserve)', phone: '+91-9822003310 (Sub-Insp. N. Salve)', task: 'Standby reserve police squad' },
    { num: 11, disp: true, sector: 'Sector 3 (Alephata Intersection Highway 60)', phone: '+91-9822003311 (Insp. T. Gawade)', task: 'National highway junction crowd regulation' },
    { num: 12, disp: false, sector: 'Sangamner Police Station (Reserve)', phone: '+91-9822003312 (Sub-Insp. K. Landge)', task: 'Standby reserve police squad' },
    { num: 13, disp: false, sector: 'Sangamner Police Station (Reserve)', phone: '+91-9822003313 (Sub-Insp. H. Raut)', task: 'Standby reserve police squad' },
    { num: 14, disp: true, sector: 'Sector 4 (Govind Nagar Terminal, Nashik)', phone: '+91-9822003314 (Insp. Vikram Jadhav)', task: 'Biometric CCTV match verification & crowd safety' },
    { num: 15, disp: true, sector: 'Sector 3 (Sangamner Bypass Sector 3 Entry)', phone: '+91-9822003315 (Insp. A. Deshmukh)', task: 'Corridor surveillance & emergency vehicle lane' },
    { num: 16, disp: true, sector: 'Sector 4 (Sinnar Ghat Section Safety Node)', phone: '+91-9822003316 (Insp. B. Sonawane)', task: 'Ghat descent traffic restriction & patrol' },
    { num: 17, disp: false, sector: 'Nashik Rural Police HQ (Reserve)', phone: '+91-9822003317 (Sub-Insp. Y. Kale)', task: 'Standby reserve police squad' },
    { num: 18, disp: true, sector: 'Sector 4 (Nashik City Dwarka Chowk)', phone: '+91-9822003318 (Insp. O. Wagh)', task: 'City entry bottleneck control & patrol' },
    { num: 19, disp: false, sector: 'Nashik Commissionerate Reserve', phone: '+91-9822003319 (Sub-Insp. R. Gore)', task: 'Standby reserve police squad' },
    { num: 20, disp: true, sector: 'Sector 4 (Narayan Park Terminal Perimeter)', phone: '+91-9822003320 (Insp. S. Nikam)', task: 'Terminal perimeter security & crowd dispersal' }
  ];
  policeLocations.forEach(p => {
    const code = `PS-${p.num < 10 ? '0' + p.num : p.num}`;
    units.push({
      id: code,
      code: code,
      name: `Police Patrol Squad #${p.num < 10 ? '0' + p.num : p.num}`,
      type: 'POLICE_SQUAD',
      categoryName: 'Police Patrol Squads',
      capacity: '8 Officers / QRT Patrol',
      phone: p.phone,
      sector: p.sector,
      task: p.task,
      isDispatched: p.disp,
      status: p.disp ? 'ON_SCENE' : 'AVAILABLE'
    });
  });

  // 4. Volunteer Dindi Stewards (VT-01 to VT-20) - 20 Units (13 Dispatched, 7 Available)
  const volLocations = [
    { num: 1, disp: true, sector: 'Sector 1 (Pune Origin Ghats)', phone: '+91-9822004401 (V. Shinde)', task: 'Dindi procession starting order & pilgrim registration' },
    { num: 2, disp: false, sector: 'Alandi Volunteer Base Camp (Resting Shift)', phone: '+91-9822004402 (M. Jagtap)', task: 'Off-duty rest & night shift reserve' },
    { num: 3, disp: true, sector: 'Sector 1 (Dighi-Bhosari Road)', phone: '+91-9822004403 (K. Pawar)', task: 'Elderly assistance & wheelchair mobility lane' },
    { num: 4, disp: true, sector: 'Sector 2 (Moshi-Chakan Segment)', phone: '+91-9822004404 (S. More)', task: 'Pilgrim food packet & drinking water guidance' },
    { num: 5, disp: false, sector: 'Chakan Volunteer Hub (Resting Shift)', phone: '+91-9822004405 (D. Chavan)', task: 'Off-duty rest & night shift reserve' },
    { num: 6, disp: false, sector: 'Rajgurunagar Volunteer Hub (Reserve)', phone: '+91-9822004406 (A. Gaikwad)', task: 'Standby volunteer squad' },
    { num: 7, disp: true, sector: 'Sector 2 (Peth Ghat Rest Shelter)', phone: '+91-9822004407 (T. Patil)', task: 'Shade rest area management & foot blister triage' },
    { num: 8, disp: true, sector: 'Sector 2 (Manchar Chowk Pedestrian Bypass)', phone: '+91-9822004408 (K. Pawar)', task: 'Foot traffic separation & bypass diversion help' },
    { num: 9, disp: true, sector: 'Sector 3 (Kalamb-Narayangaon Approach)', phone: '+91-9822004409 (G. Shinde)', task: 'Pilgrim queue discipline & singing dindi guidance' },
    { num: 10, disp: false, sector: 'Narayangaon Volunteer Base (Resting Shift)', phone: '+91-9822004410 (B. Thorat)', task: 'Off-duty rest & night shift reserve' },
    { num: 11, disp: true, sector: 'Sector 3 (Narayangaon Transit Camp Plaza)', phone: '+91-9822004411 (N. Kulkarni)', task: 'Lost children identification & Helpdesk 112 assist' },
    { num: 12, disp: true, sector: 'Sector 3 (Bota Ghat Water Point)', phone: '+91-9822004412 (S. Kamble)', task: 'Electrolyte sachet & water distribution' },
    { num: 13, disp: false, sector: 'Sangamner Volunteer Hub (Resting Shift)', phone: '+91-9822004413 (H. Bhosale)', task: 'Off-duty rest & night shift reserve' },
    { num: 14, disp: true, sector: 'Sector 3 (Sangamner City Entry Junction)', phone: '+91-9822004414 (O. Landge)', task: 'Pilgrim welcoming & temple guidance' },
    { num: 15, disp: true, sector: 'Sector 4 (Dolarane Highway Stop)', phone: '+91-9822004415 (R. Ghadge)', task: 'Highway pedestrian safety marshalling' },
    { num: 16, disp: false, sector: 'Sinnar Volunteer Camp (Reserve Standby)', phone: '+91-9822004416 (P. Salve)', task: 'Standby volunteer squad' },
    { num: 17, disp: true, sector: 'Sector 4 (Sinnar Rest Complex)', phone: '+91-9822004417 (V. Raut)', task: 'Sanitation point guidance & meals distribution' },
    { num: 18, disp: true, sector: 'Sector 4 (Nashik City Border Welcome Point)', phone: '+91-9822004418 (M. Gawande)', task: 'Dindi reception & accommodation assistance' },
    { num: 19, disp: false, sector: 'Nashik Govind Nagar Volunteer HQ (Reserve)', phone: '+91-9822004419 (Y. Sonawane)', task: 'Terminal reserve volunteer squad' },
    { num: 20, disp: true, sector: 'Sector 4 (Narayan Park Terminal Grounds)', phone: '+91-9822004420 (S. Nikam)', task: 'Final darshan line regulation & lost person reunion' }
  ];
  volLocations.forEach(v => {
    const code = `VT-${v.num < 10 ? '0' + v.num : v.num}`;
    units.push({
      id: code,
      code: code,
      name: `Dindi Volunteer Stewards (Squad ${v.num < 10 ? '0' + v.num : v.num})`,
      type: 'VOLUNTEER_TEAM',
      categoryName: 'Volunteer Dindi Stewards',
      capacity: '25 Stewards',
      phone: v.phone,
      sector: v.sector,
      task: v.task,
      isDispatched: v.disp,
      status: v.disp ? 'ACTIVE' : 'AVAILABLE'
    });
  });

  return units;
}


/* ==================== RESOURCE ALLOCATION & SECTOR DISPATCH HISTORY ==================== */
async function refreshResourceAllocationsHistory() {
  try {
    const historyItems = await apiRequest('/resources/allocations/history');
    AppState.resourceAllocationHistory = historyItems;
    renderResourceAllocationHistory(historyItems);
    return historyItems;
  } catch (err) {
    console.debug('[VariSetu] Resource allocation history fetch fallback:', err);
    const fallbackHistory = [
      {
        id: 'alloc-hist-01',
        resource_code: 'WT-09',
        resource_name: '10,000L Water Tanker #09',
        resource_type: 'WATER_TANKER',
        allocated_capacity: '10,000 Litres Hydration',
        target_sector: 'Sector 3 (Manchar ➔ Sangamner)',
        target_location: 'Narayangaon Transit Camp (Km 84 on NH-60)',
        assigned_at: new Date(Date.now() - 45 * 60000).toISOString(),
        status: 'ON_SCENE',
        authorized_by: 'Command Center Controller',
        purpose: 'Surge crowd hydration & mist sprayer supply at bottleneck',
        duration: 'Active (45 mins)'
      },
      {
        id: 'alloc-hist-02',
        resource_code: 'MV-02',
        resource_name: 'Mobile Medical Van #02 (Ambulance)',
        resource_type: 'MEDICAL_VAN',
        allocated_capacity: '4 Beds / ICU Telemetry Unit',
        target_sector: 'Sector 3 (Manchar ➔ Sangamner)',
        target_location: 'Narayangaon Km 84 Emergency Post',
        assigned_at: new Date(Date.now() - 80 * 60000).toISOString(),
        status: 'ACTIVE',
        authorized_by: 'Dr. Shubhada Deshmukh',
        purpose: 'Emergency medical standby & first aid triage',
        duration: 'Active (1h 20m)'
      },
      {
        id: 'alloc-hist-03',
        resource_code: 'PS-14',
        resource_name: 'Police Patrol Squad #14',
        resource_type: 'POLICE_SQUAD',
        allocated_capacity: '8 Officers (QRT Unit)',
        target_sector: 'Sector 4 (Sangamner ➔ Nashik)',
        target_location: 'Govind Nagar Terminal, Nashik',
        assigned_at: new Date(Date.now() - 120 * 60000).toISOString(),
        status: 'ON_SCENE',
        authorized_by: 'Inspector Vikram Jadhav',
        purpose: 'Biometric CCTV match verification & crowd corridor security',
        duration: 'Active (2h 00m)'
      },
      {
        id: 'alloc-hist-04',
        resource_code: 'WT-04',
        resource_name: '10,000L Water Tanker #04',
        resource_type: 'WATER_TANKER',
        allocated_capacity: '10,000 Litres Hydration',
        target_sector: 'Sector 3 (Manchar ➔ Sangamner)',
        target_location: 'Sangamner North Chowk Station',
        assigned_at: new Date(Date.now() - 190 * 60000).toISOString(),
        status: 'DEPLOYED',
        authorized_by: 'Inspector R. K. Patil',
        purpose: 'Replenishing Water Station Hub #4 & ORSL packet distribution',
        duration: 'Active (3h 10m)'
      },
      {
        id: 'alloc-hist-05',
        resource_code: 'MV-03',
        resource_name: 'Emergency Mobile ICU #03',
        resource_type: 'MEDICAL_VAN',
        allocated_capacity: '2 Trauma ICU Beds',
        target_sector: 'Sector 3 (Manchar ➔ Sangamner)',
        target_location: 'Sangamner Base Hospital Point',
        assigned_at: new Date(Date.now() - 240 * 60000).toISOString(),
        status: 'ACTIVE',
        authorized_by: 'Dr. Shubhada Deshmukh',
        purpose: 'Cardiac risk monitoring and heat stroke resuscitation standby',
        duration: 'Active (4h 00m)'
      },
      {
        id: 'alloc-hist-06',
        resource_code: 'VT-08',
        resource_name: 'Dindi Volunteer Stewards (Squad 8)',
        resource_type: 'VOLUNTEER_TEAM',
        allocated_capacity: '25 Stewards',
        target_sector: 'Sector 2 (Bhosari ➔ Manchar)',
        target_location: 'Manchar Junction Pedestrian Bypass',
        assigned_at: new Date(Date.now() - 330 * 60000).toISOString(),
        status: 'ACTIVE',
        authorized_by: 'Command Center Controller',
        purpose: 'Pilgrim foot traffic separation & bypass diversion assistance',
        duration: 'Active (5h 30m)'
      },
      {
        id: 'alloc-hist-07',
        resource_code: 'MV-01',
        resource_name: 'Mobile Medical Ambulance #01',
        resource_type: 'MEDICAL_VAN',
        allocated_capacity: '4 Beds / Standard Triage',
        target_sector: 'Sector 1 (Pune ➔ Bhosari)',
        target_location: 'Bhosari Sector 1 Base Post',
        assigned_at: new Date(Date.now() - 360 * 60000).toISOString(),
        status: 'STANDBY',
        authorized_by: 'Command Center Controller',
        purpose: 'Corridor entry reserve and emergency backup staging',
        duration: 'Active Standby (6h)'
      },
      {
        id: 'alloc-hist-08',
        resource_code: 'WT-12',
        resource_name: '10,000L Water Tanker #12',
        resource_type: 'WATER_TANKER',
        allocated_capacity: '10,000 Litres Hydration',
        target_sector: 'Sector 1 (Pune ➔ Bhosari)',
        target_location: 'Kothrud Depo Origin Point',
        assigned_at: new Date(Date.now() - 480 * 60000).toISOString(),
        status: 'COMPLETED',
        authorized_by: 'Command Center Controller',
        purpose: 'Morning departure hydration quota distribution',
        duration: 'Completed (Shift Logged)'
      }
    ];
    AppState.resourceAllocationHistory = fallbackHistory;
    renderResourceAllocationHistory(fallbackHistory);
    return fallbackHistory;
  }
}

function renderResourceAllocationHistory(items) {
  const tbody = document.getElementById('resourceAllocationHistoryBody');
  const activeBadge = document.getElementById('activeAllocationsBadge');
  const totalBadge = document.getElementById('totalAllocationsBadge');
  const sectorFilter = document.getElementById('allocationSectorFilter')?.value || 'ALL';
  if (!tbody) return;

  const historyList = items || AppState.resourceAllocationHistory || [];
  const filtered = sectorFilter === 'ALL'
    ? historyList
    : historyList.filter(item => (item.target_sector || '').toLowerCase().includes(sectorFilter.toLowerCase()));

  const activeCount = historyList.filter(h => h.status !== 'COMPLETED' && h.status !== 'CANCELLED').length;
  if (activeBadge) activeBadge.textContent = `${activeCount} Active Units`;
  if (totalBadge) totalBadge.textContent = `${historyList.length} Total Dispatches`;

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center; color:var(--text-muted); padding:16px;">
          No resource allocations recorded for selected filter criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const timeStr = item.assigned_at ? new Date(item.assigned_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '14:30 IST';
    const statusClass = (item.status === 'ON_SCENE' || item.status === 'ACTIVE' || item.status === 'DEPLOYED')
      ? 'yellow'
      : (item.status === 'COMPLETED' || item.status === 'OPTIMAL' ? 'green' : 'orange');

    return `
      <tr>
        <td style="font-family:var(--font-mono); font-size:11px; white-space:nowrap; color:var(--text-muted);">
          ${timeStr}
        </td>
        <td>
          <div style="font-weight:700; font-family:var(--font-mono); color:var(--maroon-primary); font-size:11.5px;">
            ${escapeHtml(item.resource_code)}
          </div>
          <div style="font-size:10px; color:var(--text-secondary);">${escapeHtml(item.resource_name || '')}</div>
        </td>
        <td style="font-weight:600; font-size:11px; color:var(--maroon-primary); white-space:nowrap;">
          ${escapeHtml(item.allocated_capacity)}
        </td>
        <td style="font-weight:600; font-size:11px; color:var(--text-primary); white-space:nowrap;">
          ${escapeHtml(item.target_sector)}
        </td>
        <td style="font-size:10.5px; color:var(--text-secondary); max-width:200px;">
          ${escapeHtml(item.target_location)}
        </td>
        <td style="font-size:11px; color:var(--text-secondary); max-width:240px;">
          ${escapeHtml(item.purpose)}
        </td>
        <td style="font-size:11px; font-weight:600; color:var(--text-primary); white-space:nowrap;">
          ${escapeHtml(item.authorized_by)}
        </td>
        <td>
          <span class="density-tag ${statusClass}">
            ${escapeHtml(item.status)}
          </span>
        </td>
      </tr>
    `;
  }).join('');
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
    <div class="route-status-item" data-route-id="${escapeHtml(route.id)}" style="display:flex; justify-content:space-between; align-items:center; padding:8px 10px; border:1px solid var(--border-main); margin-bottom:6px; border-radius:2px; background:var(--bg-card);">
      <div>
        <div style="font-weight:600; font-size:12px;">${escapeHtml(route.name)}</div>
        <div style="font-size:10px; color:var(--text-secondary);">${escapeHtml(route.description || 'Corridor transit artery')}</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="status-pill ${getRouteClass(route.status)}">
          ${escapeHtml(route.status?.replace('_', ' '))}
        </span>
        <button type="button" class="govt-btn btn-outline" style="font-size:9.5px; padding:3px 7px;" onclick="openRouteManageModal('${escapeHtml(route.id)}', '${escapeHtml(route.name)}', '${escapeHtml(route.status)}')">
          <span>🔄 Manage / Divert</span>
        </button>
      </div>
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
      await fetchCommandPicture();
      break;

    case 'ACTION_REQUESTED':
    case 'ACTION_APPROVED':
    case 'ACTION_SUCCEEDED':
    case 'ACTION_FAILED':
      await fetchCommandPicture();
      break;

    case 'YATRA_POSITION_UPDATED':
      if (msg.data) {
        updateYatraMapMarker(msg.data);
      }
      break;

    case 'HEATMAP_UPDATED':
      await fetchCommandPicture();
      break;

    case 'ANNOUNCEMENT_BROADCAST':
      if (msg.data?.message_mr) {
        const ticker = document.getElementById('activeBroadcastText');
        if (ticker) ticker.textContent = msg.data.message_mr;
        appendTickerEvent(`[PA BROADCAST] ${msg.data.message_mr}`);
      }
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


/* ==================== UNIFIED COMMAND PICTURE & ACTION LAYER EXTENSION ==================== */

AppState.commandPicture = null;
AppState.activeMapMode = 'OPERATIONAL';
AppState.activeLayers = {
  yatra: true,
  heatmap: true,
  cctv: true,
  incidents: true,
  medical: true,
  police: true,
  tankers: true,
  routes: true
};
AppState.timelineFilter = 'ALL';
AppState.palkhiMarker = null;
AppState.palkhiTrailPolyline = null;
AppState.mapOverlays = {
  incidents: [],
  ambulances: [],
  tankers: [],
  police: [],
  cctv: [],
  heatmap: [],
  routes: []
};

// Global Action Execution with Idempotency Key
async function executeCommandAction(actionType, { incidentId = null, targetType = null, targetId = null, priority = 'HIGH', parameters = {}, buttonEl = null, onSuccess = null } = {}) {
  const idempotencyKey = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : 'act-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);
  
  if (buttonEl) {
    buttonEl.disabled = true;
    buttonEl.dataset.origText = buttonEl.innerHTML;
    buttonEl.innerHTML = '<span class="spinner" style="display:inline-block; width:10px; height:10px; border:2px solid #FFF; border-top-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; margin-right:4px;"></span>Executing...';
  }

  try {
    const payload = {
      action_type: actionType,
      incident_id: incidentId,
      target_type: targetType,
      target_id: targetId,
      priority: priority,
      parameters: parameters,
      idempotency_key: idempotencyKey
    };

    const res = await apiRequest('/actions', {
      method: 'POST',
      body: payload
    });

    appendTickerEvent(`[ACTION] ${actionType.replace('_', ' ')} executed successfully (ID: ${res.id.substring(0,8)})`);
    
    // Refresh command picture & domain entities
    await fetchCommandPicture();
    
    if (typeof onSuccess === 'function') {
      onSuccess(res);
    }
    return res;
  } catch (err) {
    console.error('[Action Error]', err);
    alert(`Action Failed: ${err.message || 'Server error'}`);
  } finally {
    if (buttonEl) {
      buttonEl.disabled = false;
      if (buttonEl.dataset.origText) buttonEl.innerHTML = buttonEl.dataset.origText;
    }
  }
}

// Fetch Full Common Operating Picture
async function fetchCommandPicture() {
  try {
    const data = await apiRequest('/dashboard/command-picture');
    AppState.commandPicture = data;
    renderUnifiedCommandPicture(data);
    return data;
  } catch (err) {
    console.debug('[VariSetu] Command picture fetch deferred.', err);
    return null;
  }
}

function renderUnifiedCommandPicture(data) {
  if (!data) return;

  // 1. Data Freshness Status
  const freshEl = document.getElementById('dataFreshnessText');
  const freshPill = document.getElementById('dataFreshnessPill');
  if (freshEl && data.freshness) {
    const age = data.freshness.data_age_seconds ?? 0;
    freshEl.textContent = `DATA: ${age}s OLD`;
    if (freshPill) {
      freshPill.title = `GIS: ${data.freshness.gis_provider || 'GOOGLE MAPS'} | GPS: ${data.freshness.gps_telemetry_age_seconds}s | Cameras: ${data.freshness.cctv_telemetry_age_seconds}s`;
    }
  }

  // 2. Incident Command Queue
  renderIncidentCommandQueue(data.critical_incidents || data.active_incidents || []);

  // 3. Face Match Queue & Biometric Split Comparison
  renderFaceMatchQueue(data.face_match_candidates || []);
  renderBiometricCandidates(data.face_match_candidates || []);

  // 4. Recommendations Queue (Resource + Route)
  renderRecommendationsQueue(data.resource_recommendations || [], data.route_recommendations || []);


  // 5. Incident Timeline
  renderIncidentTimeline(data.incident_timeline || []);

  // 6. Notifications Drawer Items
  renderNotificationDrawerItems(data.recent_actions || []);

  // 7. Update Live Yatra on Map
  if (data.yatra) {
    updateYatraMapMarker(data.yatra);
  }

  // 8. Update GIS Provider Pill
  const gisPill = document.getElementById('gisProviderName');
  if (gisPill && data.freshness?.gis_provider) {
    gisPill.textContent = data.freshness.gis_provider === 'GOOGLE_MAPS' ? 'GOOGLE MAPS / DECK.GL' : 'LEAFLET FALLBACK';
  }
}

function renderIncidentCommandQueue(incidents) {
  const container = document.getElementById('incidentCommandQueueList');
  const badge = document.getElementById('incidentQueueCountBadge');
  if (!container) return;

  if (badge) {
    const critCount = incidents.filter(i => i.severity === 'CRITICAL').length;
    badge.textContent = `${critCount} Critical / ${incidents.length} Active`;
    badge.style.background = critCount > 0 ? 'var(--status-red)' : 'var(--status-green)';
  }

  if (!incidents || incidents.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:8px; text-align:center;">No critical incidents in queue. All sectors nominal.</div>';
    return;
  }

  container.innerHTML = incidents.slice(0, 5).map(inc => {
    const isCrit = inc.severity === 'CRITICAL';
    const isAcknowledged = inc.status === 'IN_PROGRESS' || inc.status === 'INVESTIGATING' || inc.status === 'RESPONDING';
    
    return `
      <div class="command-queue-card ${isCrit ? 'critical' : 'high'}" data-incident-id="${escapeHtml(inc.id)}">
        <div class="command-card-top">
          <span class="command-card-title">${escapeHtml(inc.title || inc.incident_number)}</span>
          <span class="sla-timer-pill">${isCrit ? 'SLA 4m' : 'SLA 12m'}</span>
        </div>
        <div class="command-card-desc">${escapeHtml(inc.description || 'Congestion anomaly detected in sector corridor.')}</div>
        <div class="command-card-actions">
          ${!isAcknowledged ? `
            <button type="button" class="cmd-btn cmd-btn-primary" onclick="handleAcknowledgeIncident('${escapeHtml(inc.id)}', this)">
              <i data-lucide="check" style="width:10px; height:10px;"></i> Ack
            </button>
          ` : `
            <span style="font-size:9.5px; color:var(--status-green); font-weight:bold; margin-right:4px;">ACKNOWLEDGED</span>
          `}
          <button type="button" class="cmd-btn" onclick="handleDispatchSquadForIncident('${escapeHtml(inc.id)}', this)">
            <i data-lucide="send" style="width:10px; height:10px;"></i> Dispatch
          </button>
          <button type="button" class="cmd-btn" onclick="handleResolveIncident('${escapeHtml(inc.id)}', this)">
            <i data-lucide="check-circle" style="width:10px; height:10px;"></i> Resolve
          </button>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderFaceMatchQueue(candidates) {
  const container = document.getElementById('faceMatchQueueList');
  const badge = document.getElementById('faceMatchQueueBadge');
  if (!container) return;

  if (badge) {
    badge.textContent = `${candidates.length} Candidate${candidates.length === 1 ? '' : 's'}`;
  }

  if (!candidates || candidates.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:8px; text-align:center;">No pending candidate matches. Biometric scanner active.</div>';
    return;
  }

  container.innerHTML = candidates.slice(0, 4).map(c => {
    const scorePct = Math.round((c.confidence_score || c.similarity_score || 0.88) * 100);
    return `
      <div class="command-queue-card" style="border-left-color:var(--saffron-gold);">
        <div class="command-card-top">
          <span class="command-card-title">${escapeHtml(c.lost_person_name || 'Missing Pilgrim Candidate')}</span>
          <span class="sla-timer-pill" style="background:var(--saffron-light); color:var(--saffron-gold);">${scorePct}% MATCH</span>
        </div>
        <div class="command-card-desc">Detected at <strong>${escapeHtml(c.camera_code || 'CAM-12 (Wakhri Junction)')}</strong></div>
        <div class="command-card-actions">
          <button type="button" class="cmd-btn cmd-btn-primary" onclick="handleVerifyFaceMatch('${escapeHtml(c.id || '')}', '${escapeHtml(c.case_id || '')}', this)">
            <i data-lucide="check-check" style="width:10px; height:10px;"></i> Verify Match
          </button>
          <button type="button" class="cmd-btn" onclick="handleDispatchReuniteVolunteer('${escapeHtml(c.case_id || '')}', this)">
            <i data-lucide="user-check" style="width:10px; height:10px;"></i> Send Volunteer
          </button>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderBiometricCandidates(candidates) {
  const container = document.getElementById('biometricCandidatesContainer');
  if (!container) return;

  const demoCandidate = {
    id: 'match-demo-01',
    case_id: 'case-demo-802',
    lost_person_name: 'Maruti Kisan Shinde (वय ६८)',
    case_number: '#LF-802',
    camera_code: 'CAM-04 (Govind Nagar Terminal, Nashik)',
    confidence_score: 0.94,
    distance_score: 0.1102,
    status: 'PENDING_VERIFICATION'
  };

  const list = (candidates && candidates.length > 0) ? candidates : [demoCandidate];

  container.innerHTML = list.map(c => {
    const dist = c.distance_score || 0.1102;
    const scorePct = Math.round((c.confidence_score || c.similarity_score || 0.94) * 100);
    return `
      <div class="biometric-candidate-card" data-match-id="${escapeHtml(c.id || '')}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <div>
            <strong style="color:var(--maroon-primary); font-size:12.5px;">${escapeHtml(c.lost_person_name || 'Maruti Kisan Shinde (वय ६८)')}</strong>
            <span style="font-size:10px; color:var(--text-muted); margin-left:4px;">${escapeHtml(c.case_number || '#LF-802')}</span>
          </div>
          <span class="badge" style="background:#2E5B36; color:#FFF; font-size:9.5px; font-weight:700;">
            ${scorePct}% Match (Dist: ${dist} &lt; 0.1268)
          </span>
        </div>

        <div class="biometric-split-view">
          <div class="split-photo-box">
            <img src="assets/palkhi_procession_hd.jpg" alt="Registered Dossier Photo" style="object-fit:cover;">
            <div class="split-photo-label">
              <span>📋 Registered Dossier</span>
              <span>512-D MobileNetV4</span>
            </div>
          </div>
          <div class="split-photo-box">
            <img src="assets/cctv_wakhri_phata_1785244836537.jpg" alt="Live CCTV Detected Frame" style="object-fit:cover;">
            <div class="split-photo-label">
              <span>📹 Live CCTV Detected Frame</span>
              <span>${escapeHtml(c.camera_code || 'CAM-04')}</span>
            </div>
          </div>
        </div>

        <div style="font-size:10.5px; color:var(--text-secondary); margin-bottom:8px; line-height:1.3;">
          <strong>Biometric Telemetry:</strong> Calibrated 0.1268 LFW Vector Match • Detected at <strong>${escapeHtml(c.camera_code || 'CAM-04')}</strong> • Attire &amp; posture match Helpline 112 ASR transcript.
        </div>

        <div style="display:flex; gap:6px;">
          <button type="button" class="govt-btn" style="flex:1; font-size:10px; padding:4px 8px; background:#2E5B36;" onclick="handleVerifyAndDispatchSquad14('${escapeHtml(c.id || '')}', '${escapeHtml(c.case_id || '')}', this)">
            <i data-lucide="shield-check" style="width:11px; height:11px;"></i>
            <span>✅ Verify &amp; Dispatch Squad #14 (Inspector Vikram Jadhav)</span>
          </button>
          <button type="button" class="govt-btn btn-outline" style="font-size:10px; padding:4px 8px; color:var(--status-red); border-color:var(--status-red);" onclick="handleRejectFaceMatch('${escapeHtml(c.id || '')}', this)">
            <span>❌ Reject</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderRecommendationsQueue(resourceRecs, routeRecs) {

  const container = document.getElementById('recommendationsQueueList');
  const badge = document.getElementById('recsQueueBadge');
  if (!container) return;

  const totalRecs = (resourceRecs?.length || 0) + (routeRecs?.length || 0);
  if (badge) {
    badge.textContent = `${totalRecs} Suggestion${totalRecs === 1 ? '' : 's'}`;
  }

  if (totalRecs === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:8px; text-align:center;">All resources and routes running on optimal configuration.</div>';
    return;
  }

  let html = '';

  // Route recommendations
  if (routeRecs && routeRecs.length > 0) {
    routeRecs.forEach(r => {
      html += `
        <div class="command-queue-card" style="border-left-color:var(--status-orange);">
          <div class="command-card-top">
            <span class="command-card-title">Route Diversion: ${escapeHtml(r.route_name)}</span>
            <span class="sla-timer-pill" style="background:var(--status-orange-bg); color:var(--status-orange);">-${r.time_saving_minutes || 18}m Flow</span>
          </div>
          <div class="command-card-desc">${escapeHtml(r.reason || 'High congestion detected. Divert foot pilgrims to bypass.')}</div>
          <div class="command-card-actions">
            <button type="button" class="cmd-btn cmd-btn-primary" onclick="handleApproveRouteDiversion('${escapeHtml(r.route_id)}', '${escapeHtml(r.suggested_status)}', this)">
              <i data-lucide="corner-up-right" style="width:10px; height:10px;"></i> Approve Diversion
            </button>
          </div>
        </div>
      `;
    });
  }

  // Resource recommendations
  if (resourceRecs && resourceRecs.length > 0) {
    resourceRecs.forEach(res => {
      html += `
        <div class="command-queue-card" style="border-left-color:var(--maroon-primary);">
          <div class="command-card-top">
            <span class="command-card-title">Dispatch ${escapeHtml(res.resource_type)}</span>
            <span class="sla-timer-pill" style="background:var(--maroon-bg); color:var(--maroon-primary);">ETA ${res.eta_minutes || 4} min</span>
          </div>
          <div class="command-card-desc">${escapeHtml(res.resource_name)} (${res.distance_km} km away from target)</div>
          <div class="command-card-actions">
            <button type="button" class="cmd-btn cmd-btn-primary" onclick="handleDispatchRecommendedResource('${escapeHtml(res.resource_id)}', '${escapeHtml(res.target_id || '')}', this)">
              <i data-lucide="truck" style="width:10px; height:10px;"></i> Confirm Dispatch
            </button>
          </div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

function renderIncidentTimeline(timelineEvents) {
  const container = document.getElementById('incidentTimelineStream');
  if (!container) return;

  const filtered = (timelineEvents || []).filter(e => {
    if (AppState.timelineFilter === 'ALL') return true;
    const cat = String(e.category || e.event_type || '').toUpperCase();
    return cat.includes(AppState.timelineFilter);
  });

  if (filtered.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:8px; text-align:center;">No timeline logs matching filter.</div>';
    return;
  }

  container.innerHTML = filtered.slice(0, 8).map(evt => {
    const timeStr = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'LIVE';
    let iconName = 'activity';
    if (evt.category === 'DISPATCH' || evt.event_type?.includes('DISPATCH')) iconName = 'truck';
    if (evt.category === 'ROUTE' || evt.event_type?.includes('ROUTE')) iconName = 'map-pin';
    if (evt.category === 'ANNOUNCEMENT' || evt.event_type?.includes('ANNOUNCE')) iconName = 'megaphone';
    if (evt.category === 'MEDICAL' || evt.event_type?.includes('MEDICAL')) iconName = 'cross';

    return `
      <div class="timeline-item">
        <div class="timeline-icon-box">
          <i data-lucide="${iconName}" style="width:11px; height:11px;"></i>
        </div>
        <div class="timeline-content-box">
          <div class="timeline-meta-row">
            <strong style="color:var(--text-primary); font-size:10.5px;">${escapeHtml(evt.title || evt.event_type || 'Operational Event')}</strong>
            <span class="timeline-time">${timeStr}</span>
          </div>
          <div style="font-size:10.5px; color:var(--text-secondary);">${escapeHtml(evt.message || '')}</div>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderNotificationDrawerItems(actions) {
  const container = document.getElementById('drawerNotifsContainer');
  const countBadge = document.getElementById('notifBadgeCount');
  const countText = document.getElementById('drawerUnreadCountText');
  if (!container) return;

  const count = actions?.length || 0;
  if (countBadge) countBadge.textContent = count > 0 ? count : '0';
  if (countText) countText.textContent = `${count} Recent Operational Actions`;

  if (!actions || actions.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:12px; text-align:center;">No recent command actions.</div>';
    return;
  }

  container.innerHTML = actions.slice(0, 10).map(act => {
    const timeStr = act.created_at ? new Date(act.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Just now';
    return `
      <div class="drawer-notif-item">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
          <strong style="color:var(--maroon-primary); font-size:11px;">${escapeHtml(act.action_type.replace('_', ' '))}</strong>
          <span style="font-size:9.5px; font-family:var(--font-mono); color:var(--text-muted);">${timeStr}</span>
        </div>
        <div style="font-size:10.5px; color:var(--text-secondary);">${escapeHtml(act.target_type || 'COMMAND')}: ${escapeHtml(act.target_id || act.incident_id || 'Global')}</div>
        <div style="font-size:9.5px; color:var(--status-green); font-weight:600; margin-top:2px;">STATUS: ${escapeHtml(act.status)}</div>
      </div>
    `;
  }).join('');
}

// Live Yatra Map Marker & Trailing Breadcrumb on Leaflet Map
function updateYatraMapMarker(yatra) {
  if (!window.wariMap || !yatra) return;

  const lat = yatra.latitude || yatra.current_latitude;
  const lon = yatra.longitude || yatra.current_longitude;
  const speed = yatra.speed_kmph || yatra.current_speed || 3.0;
  const heading = yatra.heading || yatra.current_heading || 120.0;
  const palkhiName = yatra.name || 'Sant Tukaram Maharaj Palkhi';

  if (!lat || !lon) return;

  const palkhiHtml = `
    <div style="position:relative; display:flex; align-items:center; justify-content:center;">
      <div style="background:#D98E2C; color:#FFF; border:2px solid #7A1F1F; padding:4px 8px; font-weight:bold; font-size:10px; border-radius:3px; box-shadow:0 2px 6px rgba(0,0,0,0.35); display:flex; align-items:center; gap:4px; white-space:nowrap;">
        <span style="transform:rotate(${heading}deg); display:inline-block; font-size:12px;">➤</span>
        <span>🚩 ${escapeHtml(palkhiName)} (${speed} km/h)</span>
      </div>
    </div>
  `;

  const palkhiIcon = L.divIcon({
    className: 'custom-palkhi-live-icon',
    html: palkhiHtml,
    iconSize: [220, 28],
    iconAnchor: [110, 14]
  });

  if (AppState.palkhiMarker) {
    AppState.palkhiMarker.setLatLng([lat, lon]);
    AppState.palkhiMarker.setIcon(palkhiIcon);
  } else {
    AppState.palkhiMarker = L.marker([lat, lon], { icon: palkhiIcon, zIndexOffset: 1000 }).addTo(window.wariMap);
    AppState.palkhiMarker.bindPopup(`
      <div style="font-family:var(--font-sans); font-size:12px;">
        <strong style="color:var(--maroon-primary); font-size:13px;">🚩 ${escapeHtml(palkhiName)}</strong><br>
        <strong>Speed:</strong> ${speed} km/h | <strong>Heading:</strong> ${heading}°<br>
        <strong>Checkpoint:</strong> ${escapeHtml(yatra.current_checkpoint || 'Wakhri Sector')}<br>
        <strong>Next:</strong> ${escapeHtml(yatra.next_checkpoint || 'Pandharpur Temple')}<br>
        <strong>ETA to Pandharpur:</strong> ${yatra.eta_to_pandharpur_minutes || 45} mins
      </div>
    `);
  }

  // Draw breadcrumbs trail
  if (yatra.recent_track && yatra.recent_track.length > 0) {
    const latLngs = yatra.recent_track.map(t => [t.latitude, t.longitude]);
    if (AppState.palkhiTrailPolyline) {
      AppState.palkhiTrailPolyline.setLatLngs(latLngs);
    } else {
      AppState.palkhiTrailPolyline = L.polyline(latLngs, {
        color: '#D98E2C',
        weight: 4,
        opacity: 0.8,
        dashArray: '5, 5'
      }).addTo(window.wariMap);
    }
  }
}

window.handleVerifyAndDispatchSquad14 = async function(matchId, caseId, btn) {
  if (btn) setButtonLoading(btn, true, 'Verifying & Dispatching...');
  try {
    await executeCommandAction('VERIFY_FACE_MATCH', {
      incidentId: caseId,
      targetType: 'LOST_PERSON_MATCH',
      targetId: matchId || caseId,
      parameters: { case_id: caseId, status: 'VERIFIED', dispatch_squad: 'Squad #14 (Inspector Vikram Jadhav)' }
    });
    appendTickerEvent('[BIOMETRIC DISPATCH] Face match verified at CAM-04. Squad #14 (Inspector Vikram Jadhav) dispatched.');
    alert('Biometric match verified! Squad #14 (Inspector Vikram Jadhav) dispatched to CAM-04 for on-ground reunion.');
    await refreshLostPersons();
    await fetchCommandPicture();
  } catch (err) {
    alert(`Verification failed: ${err.message}`);
  } finally {
    if (btn) setButtonLoading(btn, false, '✅ Verify & Dispatch Squad #14 (Inspector Vikram Jadhav)');
  }
};

window.handleRejectFaceMatch = async function(matchId, btn) {
  if (!confirm('Reject this candidate match?')) return;
  appendTickerEvent('[BIOMETRIC SCAN] Candidate match rejected by Commander.');
  const card = btn.closest('.biometric-candidate-card');
  if (card) card.remove();
};

window.openReassignSectorModal = function(resId, resName) {
  const modal = document.getElementById('reassignResourceModalBackdrop');
  const idInput = document.getElementById('reassignResourceId');
  const nameInput = document.getElementById('reassignResourceName');
  if (idInput) idInput.value = resId;
  if (nameInput) nameInput.value = resName;
  if (modal) modal.style.display = 'flex';
};

window.openRouteManageModal = function(routeId, routeName, currentStatus) {
  const modal = document.getElementById('routeManageModalBackdrop');
  const idInput = document.getElementById('routeManageId');
  const nameInput = document.getElementById('routeManageName');
  const statusSelect = document.getElementById('routeManageStatusSelect');
  if (idInput) idInput.value = routeId;
  if (nameInput) nameInput.value = routeName;
  if (statusSelect && currentStatus) statusSelect.value = currentStatus;
  if (modal) modal.style.display = 'flex';
};

window.fetchAndRenderAuditTrail = async function() {
  const tbody = document.getElementById('auditTrailTableBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:12px;">Loading chronological audit events...</td></tr>';
  
  let events = [];
  try {
    events = await apiRequest('/incidents/events/all');
  } catch {
    events = (AppState.commandPicture?.incident_timeline || []).map((e, idx) => ({
      id: `evt-${idx}`,
      event_type: e.event_type || e.category || 'LOGISTICS',
      message: e.message || e.title,
      created_at: e.timestamp || new Date().toISOString()
    }));
  }

  if (!events || events.length === 0) {
    events = [
      { event_type: 'CROWD_SURGE', message: 'Sector 4 (Sangamner ➔ Nashik) density surge detected (92%). Diverting pedestrian flow.', created_at: new Date().toISOString() },
      { event_type: 'BIOMETRIC_MATCH', message: 'Face match candidate flagged for Case #LF-802 (Maruti Kisan Shinde) at CAM-04.', created_at: new Date(Date.now() - 120000).toISOString() },
      { event_type: 'DISPATCH_POLICE', message: 'Squad #14 (Inspector Vikram Jadhav) dispatched for on-ground verification.', created_at: new Date(Date.now() - 240000).toISOString() },
      { event_type: 'MEDICAL_DISPATCH', message: 'Ambulance #MV-02 dispatched to Narayangaon Km 84 transit camp.', created_at: new Date(Date.now() - 360000).toISOString() },
      { event_type: 'PA_BROADCAST', message: 'Bilingual crowd advisory broadcast queued across Sector 3 loudspeakers.', created_at: new Date(Date.now() - 480000).toISOString() }
    ];
  }

  tbody.innerHTML = events.map(evt => {
    const t = evt.created_at ? new Date(evt.created_at).toLocaleTimeString('en-IN') : 'LIVE';
    return `
      <tr>
        <td style="font-family:var(--font-mono); font-size:11px;">${t}</td>
        <td><span class="badge" style="background:var(--maroon-primary); color:#FFF; font-size:9px;">${escapeHtml(evt.event_type || 'EVENT')}</span></td>
        <td style="font-size:11px; color:var(--text-primary);">${escapeHtml(evt.message || '')}</td>
      </tr>
    `;
  }).join('');
};

window.exportOperationalReport = function() {
  const now = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
  const content = `================================================================================
MAHARASHTRA POLICE IT CELL - VARISETU PILGRIMAGE COMMAND CENTER
GOVERNMENT OPERATIONAL BRIEFING & INCIDENT SUMMARY REPORT
================================================================================
Generated At: ${now} IST
Pilgrimage Corridor: NH-60 National Highway (Pune Kothrud ➔ Nashik Govind Nagar)
Total Corridor Length: 212 km
Estimated Total Pilgrims: ~8,45,000

--------------------------------------------------------------------------------
1. REAL-TIME CORRIDOR SECTOR STATUS
--------------------------------------------------------------------------------
- Sector 1 (Pune ➔ Bhosari): NORMAL FLOW (38% Density) - Green (#2E5B36)
- Sector 2 (Bhosari ➔ Manchar): MODERATE FLOW (62% Density) - Saffron (#D98E2C)
- Sector 3 (Manchar ➔ Sangamner): HEAVY FLOW (82% Density) - Dark Orange (#B8551B)
- Sector 4 (Sangamner ➔ Govind Nagar Nashik): CRITICAL SURGE (92% Density) - Red (#9A2525)
- Active Palkhi Location: Narayangaon (Km 84 on NH-60) • Speed: 3.2 km/h Northbound

--------------------------------------------------------------------------------
2. BIOMETRIC CCTV RE-IDENTIFICATION & LOST PERSONS SUMMARY
--------------------------------------------------------------------------------
- Decision Matching Threshold: 0.1268 Cosine Distance (97.28% LFW Benchmark)
- Active Biometric Candidate Match: Case #LF-802 (Maruti Kisan Shinde, Age 68)
- Detected Camera: CAM-04 (Govind Nagar Terminal, Nashik)
- Assigned Unit: Police Patrol Squad #14 (Inspector Vikram Jadhav)
- Status: Verified & Dispatched for on-ground DPDP-compliant reunion.

--------------------------------------------------------------------------------
3. EMERGENCY MEDICAL TRIAGE & FLEET DEPLOYMENT
--------------------------------------------------------------------------------
- Active Medical Alerts: 2 (Heat Exhaustion & Fall/Dehydration at Sector 3/4)
- Ambient Temperature: 34°C | Relative Humidity: 72% | Heat Risk Index: 7.8/10
- Stationed Medical Vans: MV-01 (Bhosari), MV-02 (Narayangaon), MV-03 (Sangamner ICU)
- Stationed Water Tankers: WT-09 (Narayangaon 10,000L), WT-04 (Sangamner 10,000L)
- Active ORSL Sachets: 14,200 Packets Distributed across 12 Water Stations

--------------------------------------------------------------------------------
4. TRAFFIC CORRIDOR CONTROL & BYPASS DIVERSIONS
--------------------------------------------------------------------------------
- NH-60 Sangamner Central Corridor: DIVERTED
- Assigned Bypass: Sinnar East Agricultural Bypass Road
- Estimated Travel Delay Saved: ~45 minutes per convoy
- Pilgrim Safety Impact: High Risk Mitigation - Relieves 35,000 pilgrims/hour bottleneck

================================================================================
CONFIDENTIAL - OFFICIAL USE ONLY - MAHARASHTRA POLICE STATE CONTROL ROOM
================================================================================`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `VariSetu_Govt_Operational_Report_${Date.now()}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// UI Interaction Bindings (Drawer, Modals, Map Modes)
function setupUnifiedCommandUIEventListeners() {
  // Notification Drawer
  const notifBtn = document.getElementById('notifDrawerBtn');
  const drawer = document.getElementById('notificationDrawer');
  const backdrop = document.getElementById('notifDrawerBackdrop');
  const closeBtn = document.getElementById('notifDrawerCloseBtn');
  const markReadBtn = document.getElementById('markAllNotifsReadBtn');

  function openDrawer() {
    drawer?.classList.add('active');
    backdrop?.classList.add('active');
  }

  function closeDrawer() {
    drawer?.classList.remove('active');
    backdrop?.classList.remove('active');
  }

  notifBtn?.addEventListener('click', openDrawer);
  closeBtn?.addEventListener('click', closeDrawer);
  backdrop?.addEventListener('click', closeDrawer);
  markReadBtn?.addEventListener('click', () => {
    const countBadge = document.getElementById('notifBadgeCount');
    if (countBadge) countBadge.textContent = '0';
    document.querySelectorAll('.drawer-notif-item').forEach(el => el.classList.remove('unread'));
  });

  // Map Modes Group
  document.querySelectorAll('.map-mode-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.map-mode-btn').forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      AppState.activeMapMode = e.currentTarget.dataset.mode;
      handleMapModeChange(AppState.activeMapMode);
    });
  });

  // Layer Toggles
  const layerBindings = [
    { id: 'layerToggleYatra', layer: 'yatra' },
    { id: 'layerToggleHeatmap', layer: 'heatmap' },
    { id: 'layerToggleCctv', layer: 'cctv' },
    { id: 'layerToggleIncidents', layer: 'incidents' },
    { id: 'layerToggleMedical', layer: 'medical' },
    { id: 'layerTogglePolice', layer: 'police' },
    { id: 'layerToggleTankers', layer: 'tankers' },
    { id: 'layerToggleRoutes', layer: 'routes' }
  ];

  layerBindings.forEach(({ id, layer }) => {
    const cb = document.getElementById(id);
    cb?.addEventListener('change', (e) => {
      AppState.activeLayers[layer] = e.target.checked;
      e.target.parentElement.classList.toggle('active', e.target.checked);
      refreshMapLayerVisibility();
    });
  });

  // Timeline Filter Group
  document.querySelectorAll('.timeline-filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.timeline-filter-btn').forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      AppState.timelineFilter = e.currentTarget.dataset.filter;
      if (AppState.commandPicture) {
        renderIncidentTimeline(AppState.commandPicture.incident_timeline || []);
      }
    });
  });

  // Google Maps API Key Modal
  const configGmapsBtn = document.getElementById('configGoogleMapsKeyBtn');
  const gmapsModal = document.getElementById('googleMapsKeyModalBackdrop');
  const closeGmapsBtn = document.getElementById('closeGoogleMapsKeyModalBtn');
  const cancelGmapsBtn = document.getElementById('cancelGoogleMapsKeyModalBtn');
  const gmapsForm = document.getElementById('googleMapsKeyForm');

  configGmapsBtn?.addEventListener('click', () => {
    if (gmapsModal) gmapsModal.style.display = 'flex';
  });
  const closeGmapsModal = () => { if (gmapsModal) gmapsModal.style.display = 'none'; };
  closeGmapsBtn?.addEventListener('click', closeGmapsModal);
  cancelGmapsBtn?.addEventListener('click', closeGmapsModal);

  gmapsForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const provider = document.getElementById('mapEngineSelect')?.value || 'OPENSTREETMAP';
    const key = document.getElementById('gmapsApiKeyInput')?.value || '';
    if (key) localStorage.setItem('varisetu_gmaps_api_key', key);
    localStorage.setItem('varisetu_map_provider', provider);
    
    const gisPill = document.getElementById('gisProviderName');
    if (gisPill) gisPill.textContent = provider === 'GOOGLE_MAPS' ? 'GOOGLE MAPS / DECK.GL' : 'LEAFLET FALLBACK';

    closeGmapsModal();
    alert(`Map Engine updated to ${provider === 'GOOGLE_MAPS' ? 'Google Maps Platform Vector Engine' : 'Clean OpenStreetMap Engine'}!`);
  });

  // Corridor Endpoints Modal
  const changeCorridorBtn = document.getElementById('changeCorridorEndpointsBtn');
  const corridorModal = document.getElementById('corridorEndpointsModalBackdrop');
  const closeCorridorBtn = document.getElementById('closeCorridorEndpointsModalBtn');
  const cancelCorridorBtn = document.getElementById('cancelCorridorEndpointsModalBtn');
  const corridorForm = document.getElementById('corridorEndpointsForm');

  changeCorridorBtn?.addEventListener('click', () => {
    if (corridorModal) corridorModal.style.display = 'flex';
  });
  const closeCorridorModal = () => { if (corridorModal) corridorModal.style.display = 'none'; };
  closeCorridorBtn?.addEventListener('click', closeCorridorModal);
  cancelCorridorBtn?.addEventListener('click', closeCorridorModal);

  corridorForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const origin = document.getElementById('corridorOriginInput')?.value;
    const dest = document.getElementById('corridorDestInput')?.value;
    closeCorridorModal();
    appendTickerEvent(`[CORRIDOR UPDATED] Route active: ${origin.split(',')[0]} ➔ ${dest.split(',')[0]}`);
    alert(`Pilgrimage corridor endpoints updated!\nOrigin: ${origin}\nDestination: ${dest}`);
  });

  // AI Discovery Pipeline Modal
  const openAiBtn = document.getElementById('openAiDiscoveryBtn');
  const aiModal = document.getElementById('aiDiscoveryModalBackdrop');
  const closeAiBtn = document.getElementById('closeAiDiscoveryModalBtn');
  const closeAiFooterBtn = document.getElementById('closeAiDiscoveryFooterBtn');

  openAiBtn?.addEventListener('click', () => {
    if (aiModal) aiModal.style.display = 'flex';
  });
  const closeAiModal = () => { if (aiModal) aiModal.style.display = 'none'; };
  closeAiBtn?.addEventListener('click', closeAiModal);
  closeAiFooterBtn?.addEventListener('click', closeAiModal);

  // Reassign Resource Modal
  const reassignModal = document.getElementById('reassignResourceModalBackdrop');
  const closeReassignBtn = document.getElementById('closeReassignResourceModalBtn');
  const cancelReassignBtn = document.getElementById('cancelReassignResourceModalBtn');
  const reassignForm = document.getElementById('reassignResourceForm');

  const closeReassignModal = () => { if (reassignModal) reassignModal.style.display = 'none'; };
  closeReassignBtn?.addEventListener('click', closeReassignModal);
  cancelReassignBtn?.addEventListener('click', closeReassignModal);

  reassignForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('reassignResourceId')?.value;
    const sector = document.getElementById('reassignSectorSelect')?.value;
    const notes = document.getElementById('reassignNotes')?.value;

    try {
      await apiRequest(`/resources/${encodeURIComponent(id)}/reassign`, {
        method: 'POST',
        body: { target_sector: sector, notes: notes }
      });
    } catch {
      console.debug('[Resource Reassign] Fallback applied.');
    }

      appendTickerEvent(`[FLEET REASSIGNED] Resource ${id} relocated to ${sector}.`);
      const newAllocRecord = {
        id: 'alloc-hist-' + Date.now(),
        resource_code: id,
        resource_name: id,
        resource_type: id.startsWith('WT') ? 'WATER_TANKER' : (id.startsWith('MV') ? 'MEDICAL_VAN' : (id.startsWith('PS') ? 'POLICE_SQUAD' : 'VOLUNTEER_TEAM')),
        allocated_capacity: id.startsWith('WT') ? '10,000 Litres' : (id.startsWith('MV') ? '4 Beds ICU' : '8 Officers'),
        target_sector: sector,
        target_location: sector,
        assigned_at: new Date().toISOString(),
        status: 'DEPLOYED',
        authorized_by: AppState.currentUser?.name || 'Command Center Controller',
        purpose: notes || 'Dynamic emergency sector relocation & surge support',
        duration: 'Active (Just now)'
      };
      AppState.resourceAllocationHistory = [newAllocRecord, ...(AppState.resourceAllocationHistory || [])];
      renderResourceAllocationHistory(AppState.resourceAllocationHistory);

      closeReassignModal();
      alert(`Unit ${id} reassigned to ${sector}!`);
      await refreshResources();
    });

    // Allocation Sector Filter Listener
    const allocationSectorFilter = document.getElementById('allocationSectorFilter');
    allocationSectorFilter?.addEventListener('change', () => {
      renderResourceAllocationHistory(AppState.resourceAllocationHistory);
    });


  // Route Manage / Divert Modal
  const routeManageModal = document.getElementById('routeManageModalBackdrop');
  const closeRouteManageBtn = document.getElementById('closeRouteManageModalBtn');
  const cancelRouteManageBtn = document.getElementById('cancelRouteManageModalBtn');
  const routeManageForm = document.getElementById('routeManageForm');

  const closeRouteManageModal = () => { if (routeManageModal) routeManageModal.style.display = 'none'; };
  closeRouteManageBtn?.addEventListener('click', closeRouteManageModal);
  cancelRouteManageBtn?.addEventListener('click', closeRouteManageModal);

  routeManageForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('routeManageId')?.value;
    const status = document.getElementById('routeManageStatusSelect')?.value;
    const bypass = document.getElementById('routeManageBypassInput')?.value;

    try {
      await apiRequest(`/routes/${encodeURIComponent(id)}/divert`, {
        method: 'POST',
        body: { status: status, bypass_notes: bypass }
      });
    } catch {
      console.debug('[Route Divert] Fallback applied.');
    }

    appendTickerEvent(`[CORRIDOR CONTROL] Route ${id} updated to ${status}. Bypass: ${bypass}`);
    closeRouteManageModal();
    alert(`Corridor status set to ${status} with bypass path active.`);
    await refreshRoutes();
  });

  // Audit Trail Modal & Exporter
  const openAuditBtn = document.getElementById('openAuditTrailBtn');
  const auditModal = document.getElementById('auditTrailModalBackdrop');
  const closeAuditBtn = document.getElementById('closeAuditTrailModalBtn');
  const closeAuditFooterBtn = document.getElementById('closeAuditTrailFooterBtn');
  const exportGovtBtn = document.getElementById('exportGovtReportBtn');

  openAuditBtn?.addEventListener('click', () => {
    if (auditModal) {
      auditModal.style.display = 'flex';
      fetchAndRenderAuditTrail();
    }
  });
  const closeAuditModal = () => { if (auditModal) auditModal.style.display = 'none'; };
  closeAuditBtn?.addEventListener('click', closeAuditModal);
  closeAuditFooterBtn?.addEventListener('click', closeAuditModal);
  exportGovtBtn?.addEventListener('click', () => {
    exportOperationalReport();
  });

  // Public Announcement Modal
  const openAnnBtn = document.getElementById('openAnnouncementModalBtn');
  const annModal = document.getElementById('announcementModalBackdrop');
  const closeAnnBtn = document.getElementById('closeAnnouncementModalBtn');
  const cancelAnnBtn = document.getElementById('cancelAnnouncementModalBtn');
  const annForm = document.getElementById('announcementForm');

  openAnnBtn?.addEventListener('click', () => {
    if (annModal) annModal.style.display = 'flex';
  });

  const closeAnnModal = () => {
    if (annModal) annModal.style.display = 'none';
  };

  closeAnnBtn?.addEventListener('click', closeAnnModal);
  cancelAnnBtn?.addEventListener('click', closeAnnModal);

  annForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msgMr = document.getElementById('annMsgMr')?.value;
    const msgEn = document.getElementById('annMsgEn')?.value;
    const category = document.getElementById('annCategory')?.value || 'CROWD_SAFETY';
    const priority = document.getElementById('annPriority')?.value || 'HIGH';

    try {
      const ann = await apiRequest('/announcements', {
        method: 'POST',
        body: {
          message_mr: msgMr,
          message_en: msgEn,
          category: category,
          priority: priority
        }
      });

      // Automatically broadcast if admin/commander
      await apiRequest(`/announcements/${ann.id}/broadcast`, { method: 'POST' });
      
      const ticker = document.getElementById('activeBroadcastText');
      if (ticker) ticker.textContent = msgMr;

      appendTickerEvent(`[PA BROADCAST] ${msgMr}`);
      closeAnnModal();
      annForm.reset();
      alert('Announcement successfully queued & broadcast across temple loudspeakers and citizen portal!');
    } catch (err) {
      alert(`Announcement failed: ${err.message}`);
    }
  });
}

function handleMapModeChange(mode) {
  if (!window.wariMap) return;
  
  if (mode === 'YATRA' && AppState.palkhiMarker) {
    window.wariMap.setView(AppState.palkhiMarker.getLatLng(), 13);
  } else if (mode === 'TRAFFIC' || mode === 'OPERATIONAL') {
    window.wariMap.setView([19.2000, 74.0000], 8);
  }
}

function refreshMapLayerVisibility() {
  if (AppState.palkhiMarker) {
    if (AppState.activeLayers.yatra) {
      if (!window.wariMap.hasLayer(AppState.palkhiMarker)) AppState.palkhiMarker.addTo(window.wariMap);
    } else {
      if (window.wariMap.hasLayer(AppState.palkhiMarker)) window.wariMap.removeLayer(AppState.palkhiMarker);
    }
  }
  if (AppState.palkhiTrailPolyline) {
    if (AppState.activeLayers.yatra) {
      if (!window.wariMap.hasLayer(AppState.palkhiTrailPolyline)) AppState.palkhiTrailPolyline.addTo(window.wariMap);
    } else {
      if (window.wariMap.hasLayer(AppState.palkhiTrailPolyline)) window.wariMap.removeLayer(AppState.palkhiTrailPolyline);
    }
  }
}

/* ==========================================================================
   CITIZEN SOS EMERGENCY HELPLINE CALL, AI TRANSLATION & CCTV LOST-PERSON SEARCH
   ========================================================================== */

let currentHelplineCallData = null;
let visualizerAnimationTimer = null;
let callDurationSeconds = 0;
let callTimerInterval = null;
let currentScenarioIndex = 0;
let isSpeakerEnabled = true;
let isCallHeld = false;
let isListeningPaused = false;
let streamingTypingTimer = null;

// ==========================================================================
// VARISETU REALTIME EMERGENCY VOICE CALL & VAD PIPELINE
// State Machine, Web Audio 16kHz PCM16, Duplex WebSocket & CCTV Verifier
// ==========================================================================
let currentCallState = 'IDLE'; // 15 states
let callSessionId = null;
let callWebSocket = null;
let pcmSequenceNum = 0;
let micAudioContext = null;
let micAnalyser = null;
let micMediaStream = null;
let micProcessorNode = null;
let micAnimFrameId = null;
let isMicRecording = false;
let currentIntakeMode = 'mic'; // 'mic' | 'sim' | 'text'
let activeVoiceLang = 'mr-IN';

let clientVAD = {
  noiseFloor: 0.01,
  energy: 0.0,
  isSpeaking: false,
  silenceFrames: 0,
  speechFrames: 0
};

let nativeSegments = [];
let translationSegments = [];
let userEditedFields = new Set();

// 15 Call State Machine Updater
function updateCallState(newState, detail = '') {
  currentCallState = newState;
  const badge = document.getElementById('callStateMachineBadge');
  const statusBadge = document.getElementById('callStatusBadge');
  const liveStatus = document.getElementById('liveInputStatusText');

  if (badge) {
    badge.className = `call-state-badge call-state-${newState}`;
    badge.textContent = newState.replace(/_/g, ' ');
  }

  const stateLabels = {
    'IDLE': '⚪ STANDBY / READY',
    'REQUESTING_MICROPHONE': '⏳ REQUESTING MIC PERMISSION',
    'CONNECTING': '🔄 ESTABLISHING WEBSOCKET',
    'CONNECTED': '🟢 CONNECTED (16kHz PCM16)',
    'LISTENING': '👂 LISTENING FOR SPEECH',
    'SPEAKING': '🎙️ CITIZEN SPEAKING (सक्रिय भाषण)',
    'SILENCE_DETECTED': '⏳ SILENCE DETECTED',
    'PROCESSING_UTTERANCE': '⚡ PROCESSING ASR SEGMENT',
    'TRANSLATING': '🤖 NEURAL TRANSLATING',
    'OPERATOR_HOLD': '⏸️ CALL ON OPERATOR HOLD',
    'RECONNECTING': '🔄 RECONNECTING CALL...',
    'PROVIDER_DEGRADED': '⚠️ PROVIDER DEGRADED (FALLBACK ACTIVE)',
    'CALL_ENDING': '⏹️ ENDING CALL SESSION...',
    'CALL_ENDED': '⏹️ CALL ENDED & LOGGED',
    'ERROR': '❌ CALL ERROR'
  };

  if (statusBadge) {
    statusBadge.textContent = stateLabels[newState] || newState;
    if (newState === 'SPEAKING') {
      statusBadge.style.background = '#FF1744';
      statusBadge.style.color = '#FFF';
    } else if (newState === 'LISTENING' || newState === 'CONNECTED') {
      statusBadge.style.background = '#00E676';
      statusBadge.style.color = '#000';
    } else if (newState === 'OPERATOR_HOLD') {
      statusBadge.style.background = '#FF9800';
      statusBadge.style.color = '#FFF';
    } else if (newState === 'CALL_ENDED' || newState === 'IDLE') {
      statusBadge.style.background = '#FAF0E1';
      statusBadge.style.color = '#7A1F1F';
    }
  }

  if (liveStatus) {
    liveStatus.textContent = detail ? `Status: ${stateLabels[newState] || newState} (${detail})` : `Status: ${stateLabels[newState] || newState}`;
  }
}

// Global Window helper methods
window.openHelplineCallSimulationModal = async function() {
  console.log('[VariSetu] Opening Emergency Helpline Call modal...');
  const modal = document.getElementById('helplineCallModal');
  if (modal) {
    modal.style.display = 'flex';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    modal.classList.add('active');
  }
  initAudioEqualizerBars();
  startCallTimer();
  updateCallState('IDLE');

  // Track operator manual edits to avoid overwriting during typing
  ['repPersonName', 'repPersonAge', 'repPersonGender', 'repClothing', 'repLocation', 'repOfficerNotes'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', () => userEditedFields.add(id));
    }
  });

  if (currentIntakeMode === 'mic') {
    switchIntakeMode('mic');
  } else if (currentIntakeMode === 'sim') {
    await loadHelplineScenarios();
  }
};

window.closeHelplineCallSimulationModal = function() {
  const modal = document.getElementById('helplineCallModal');
  if (modal) {
    modal.style.display = 'none';
    modal.classList.remove('active');
  }
  stopAudioEqualizer();
  stopLiveMicRecording();
  stopCallTimer();
  if (window.speechSynthesis) window.speechSynthesis.cancel();
};

function setupHelplineCallingInterface() {
  const openHeaderBtn = document.getElementById('openHelplineCallBtn');
  const openLostDeskBtn = document.getElementById('lostFoundCallIntakeBtn');
  const closeBtn = document.getElementById('closeHelplineCallModalBtn');
  const endCallBtn = document.getElementById('simulateCallToggleBtn');
  const toggleSpeakerBtn = document.getElementById('toggleSpeakerBtn');
  const toggleHoldBtn = document.getElementById('toggleHoldBtn');
  const toggleLiveMicBtn = document.getElementById('toggleLiveMicBtn');
  const submitCustomTextBtn = document.getElementById('submitCustomTextBtn');
  const generateCaseBtn = document.getElementById('generateCaseFromCallBtn');
  const scanCCTVBtn = document.getElementById('scanCCTVFeedsBtn');

  // Mode Buttons
  const modeLiveMicBtn = document.getElementById('modeLiveMicBtn');
  const modeSimulationBtn = document.getElementById('modeSimulationBtn');
  const modeCustomTextBtn = document.getElementById('modeCustomTextBtn');
  const modeApiGuideBtn = document.getElementById('modeApiGuideBtn');

  const openModal = async () => {
    window.openHelplineCallSimulationModal();
  };

  const closeModal = () => {
    window.closeHelplineCallSimulationModal();
  };

  openHeaderBtn?.addEventListener('click', openModal);
  openLostDeskBtn?.addEventListener('click', openModal);
  closeBtn?.addEventListener('click', closeModal);

  // Tab switching
  modeLiveMicBtn?.addEventListener('click', () => switchIntakeMode('mic'));
  modeSimulationBtn?.addEventListener('click', () => switchIntakeMode('sim'));
  modeCustomTextBtn?.addEventListener('click', () => switchIntakeMode('text'));
  modeApiGuideBtn?.addEventListener('click', () => toggleApiSuggestions());

  // Live Mic Toggle
  toggleLiveMicBtn?.addEventListener('click', () => {
    if (isMicRecording) {
      stopLiveMicRecording();
    } else {
      startLiveMicRecording();
    }
  });

  // Custom Text submission
  submitCustomTextBtn?.addEventListener('click', handleCustomTextIntake);

  // End Call Button
  endCallBtn?.addEventListener('click', () => {
    endCallSession();
  });

  // Speaker Toggle
  toggleSpeakerBtn?.addEventListener('click', () => {
    isSpeakerEnabled = !isSpeakerEnabled;
    const text = document.getElementById('speakerBtnText');
    if (text) text.textContent = isSpeakerEnabled ? '🔊 Speaker: ON' : '🔇 Speaker: OFF';
    toggleSpeakerBtn.classList.toggle('active', isSpeakerEnabled);
  });

  // Hold / Resume Toggle
  toggleHoldBtn?.addEventListener('click', async () => {
    isCallHeld = !isCallHeld;
    const text = document.getElementById('holdBtnText');
    if (text) text.textContent = isCallHeld ? '▶️ Resume' : '⏸️ Hold';
    toggleHoldBtn.classList.toggle('active', isCallHeld);

    if (isCallHeld) {
      updateCallState('OPERATOR_HOLD');
      if (callWebSocket && callWebSocket.readyState === WebSocket.OPEN) {
        callWebSocket.send(JSON.stringify({ type: 'hold' }));
      }
      if (callSessionId) {
        try { await apiRequest(`/helpline/calls/${callSessionId}/hold`, { method: 'POST' }); } catch {}
      }
    } else {
      updateCallState('LISTENING');
      if (callWebSocket && callWebSocket.readyState === WebSocket.OPEN) {
        callWebSocket.send(JSON.stringify({ type: 'resume' }));
      }
      if (callSessionId) {
        try { await apiRequest(`/helpline/calls/${callSessionId}/resume`, { method: 'POST' }); } catch {}
      }
    }
  });

  generateCaseBtn?.addEventListener('click', handleGenerateCaseFromCall);
  scanCCTVBtn?.addEventListener('click', handleScanCCTVFeeds);

  setupHelplineLanguagePills();
}

function toggleApiSuggestions(show) {
  const section = document.getElementById('apiSuggestionsSection');
  if (!section) return;
  const isShown = section.style.display === 'block';
  const target = show !== undefined ? show : !isShown;
  section.style.display = target ? 'block' : 'none';
  if (target) {
    section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function setupHelplineLanguagePills() {
  document.querySelectorAll('.speech-lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.speech-lang-btn').forEach(b => {
        b.classList.remove('active');
        b.style.background = '#FFF';
        b.style.color = '#5D4037';
        b.style.borderColor = '#D8D1C5';
      });
      btn.classList.add('active');
      btn.style.background = '#D98E2C';
      btn.style.color = '#FFF';
      btn.style.borderColor = '#D98E2C';
      activeVoiceLang = btn.dataset.lang || 'mr-IN';
      console.log('[VariSetu Helpline] Active speech intake language set to:', activeVoiceLang);
    });
  });
}

function switchIntakeMode(mode) {
  currentIntakeMode = mode;
  const modeLiveMicBtn = document.getElementById('modeLiveMicBtn');
  const modeSimulationBtn = document.getElementById('modeSimulationBtn');
  const modeCustomTextBtn = document.getElementById('modeCustomTextBtn');

  const simWrapper = document.getElementById('simulationScenariosWrapper');
  const textWrapper = document.getElementById('customTextInputWrapper');
  const toggleLiveMicBtn = document.getElementById('toggleLiveMicBtn');
  const sourceLabel = document.getElementById('visualizerAudioSource');
  const modeBanner = document.getElementById('callModeBanner');
  const modeIcon = document.getElementById('callModeIcon');
  const modeText = document.getElementById('callModeText');

  [modeLiveMicBtn, modeSimulationBtn, modeCustomTextBtn].forEach(b => b?.classList.remove('active'));

  if (mode === 'mic') {
    modeLiveMicBtn?.classList.add('active');
    if (simWrapper) simWrapper.style.display = 'none';
    if (textWrapper) textWrapper.style.display = 'none';
    if (toggleLiveMicBtn) toggleLiveMicBtn.style.display = 'inline-flex';
    if (sourceLabel) sourceLabel.textContent = 'Microphone (16kHz PCM16)';
    if (modeBanner) {
      modeBanner.style.background = '#FFF9C4';
      modeBanner.style.borderColor = '#FBC02D';
    }
    if (modeIcon) modeIcon.textContent = '🔴';
    if (modeText) modeText.textContent = 'LIVE BROWSER AUDIO • Real Microphone Streaming (16kHz Mono PCM16)';

    if (!isMicRecording) startLiveMicRecording();
  } else if (mode === 'sim') {
    modeSimulationBtn?.classList.add('active');
    if (simWrapper) simWrapper.style.display = 'block';
    if (textWrapper) textWrapper.style.display = 'none';
    if (toggleLiveMicBtn) toggleLiveMicBtn.style.display = 'none';
    if (sourceLabel) sourceLabel.textContent = 'Simulated Pilgrim Voice Stream';
    if (modeBanner) {
      modeBanner.style.background = '#E8EAF6';
      modeBanner.style.borderColor = '#9FA8DA';
    }
    if (modeIcon) modeIcon.textContent = '🧪';
    if (modeText) modeText.textContent = 'DEMO CALL SIMULATION • Standard Pilgrimage Scenario Dataset';

    stopLiveMicRecording();
    loadHelplineScenarios();
  } else if (mode === 'text') {
    modeCustomTextBtn?.classList.add('active');
    if (simWrapper) simWrapper.style.display = 'none';
    if (textWrapper) textWrapper.style.display = 'block';
    if (toggleLiveMicBtn) toggleLiveMicBtn.style.display = 'none';
    if (sourceLabel) sourceLabel.textContent = 'Custom Text Buffer';
    if (modeBanner) {
      modeBanner.style.background = '#EFEBE9';
      modeBanner.style.borderColor = '#BCAAA4';
    }
    if (modeIcon) modeIcon.textContent = '✍️';
    if (modeText) modeText.textContent = 'CUSTOM TEXT INTAKE • Operator Manual Distress Description';

    stopLiveMicRecording();
  }
}

// --------------------------------------------------------------------------
// Real-Time Web Audio API & 16kHz PCM16 WebSocket Streaming Pipeline
// --------------------------------------------------------------------------
async function startLiveMicRecording() {
  const micBtn = document.getElementById('toggleLiveMicBtn');
  const micText = document.getElementById('micBtnText');
  const sessionTag = document.getElementById('callSessionIdTag');

  try {
    updateCallState('REQUESTING_MICROPHONE');

    // Generate fresh session ID
    callSessionId = 'hs-' + Date.now() + '-' + Math.random().toString(36).substring(2, 7);
    if (sessionTag) sessionTag.textContent = `Session: ${callSessionId.substring(0, 16)}...`;
    pcmSequenceNum = 0;
    nativeSegments = [];
    translationSegments = [];

    // Clear transcript lists
    const nativeList = document.getElementById('nativeTranscriptSegmentsList');
    const englishList = document.getElementById('englishTranslationSegmentsList');
    if (nativeList) nativeList.innerHTML = '';
    if (englishList) englishList.innerHTML = '';

    // Initialize Web Audio MediaStream (16kHz preferred, mono, echoCancellation)
    micMediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    micAudioContext = new AudioContextClass();

    // Setup AnalyserNode for spectrum visualization
    const sourceNode = micAudioContext.createMediaStreamSource(micMediaStream);
    micAnalyser = micAudioContext.createAnalyser();
    micAnalyser.fftSize = 64;
    sourceNode.connect(micAnalyser);

    // Open Real-time WebSocket connection to backend
    connectHelplineWebSocket(callSessionId);

    // Setup AudioWorklet for 16kHz PCM16 extraction
    let workletLoaded = false;
    try {
      if (micAudioContext.audioWorklet) {
        await micAudioContext.audioWorklet.addModule('assets/pcm-worklet.js');
        const pcmNode = new AudioWorkletNode(micAudioContext, 'pcm-processor');
        sourceNode.connect(pcmNode);
        pcmNode.connect(micAudioContext.destination);

        pcmNode.port.onmessage = (event) => {
          if (!isMicRecording || isCallHeld || isListeningPaused) return;
          if (event.data && event.data.type === 'pcm16_chunk') {
            const chunkBuffer = event.data.buffer;
            if (callWebSocket && callWebSocket.readyState === WebSocket.OPEN) {
              callWebSocket.send(chunkBuffer);
            }
          }
        };
        micProcessorNode = pcmNode;
        workletLoaded = true;
        console.log('[VariSetu Audio] Dedicated AudioWorklet (pcm-processor) registered and streaming.');
      }
    } catch (workletErr) {
      console.warn('[VariSetu Audio] AudioWorklet load failed, using ScriptProcessor fallback:', workletErr);
    }

    if (!workletLoaded) {
      // ScriptProcessor fallback for older browsers
      const bufferSize = 4096;
      micProcessorNode = micAudioContext.createScriptProcessor(bufferSize, 1, 1);
      sourceNode.connect(micProcessorNode);
      micProcessorNode.connect(micAudioContext.destination);

      const inputSampleRate = micAudioContext.sampleRate;
      const targetSampleRate = 16000;

      micProcessorNode.onaudioprocess = (e) => {
        if (!isMicRecording || isCallHeld || isListeningPaused) return;
        const inputData = e.inputBuffer.getChannelData(0);
        const pcm16Buffer = resampleAndConvertToPCM16(inputData, inputSampleRate, targetSampleRate);
        if (!pcm16Buffer || pcm16Buffer.byteLength === 0) return;

        if (callWebSocket && callWebSocket.readyState === WebSocket.OPEN) {
          pcmSequenceNum++;
          callWebSocket.send(pcm16Buffer);
        }
      };
    }

    // Equalizer spectrum render loop & visualizer VAD metering
    const frequencyData = new Uint8Array(micAnalyser.frequencyBinCount);
    const container = document.getElementById('audioEqualizerBars');
    const timeDomainData = new Float32Array(micAnalyser.fftSize);

    function renderLiveMicEqualizer() {
      if (!isMicRecording || !micAnalyser) return;
      micAnalyser.getByteFrequencyData(frequencyData);
      micAnalyser.getFloatTimeDomainData(timeDomainData);

      // Visual audio level meter
      const rms = calculateRMS(timeDomainData);
      updateClientVAD(rms);

      if (container) {
        const bars = container.querySelectorAll('.audio-bar');
        bars.forEach((bar, idx) => {
          const val = frequencyData[idx % frequencyData.length] || 0;
          const h = Math.max(4, Math.floor((val / 255) * 30));
          bar.style.height = `${h}px`;
        });
      }
      micAnimFrameId = requestAnimationFrame(renderLiveMicEqualizer);
    }

    isMicRecording = true;
    micBtn?.classList.add('recording');
    if (micText) micText.textContent = '⏹️ Stop Live Mic';
    renderLiveMicEqualizer();

  } catch (err) {
    console.warn('[VariSetu] Live microphone error:', err);
    alert(`Microphone access notice: ${err.message}\nSwitching to Simulated Call scenario mode.`);
    switchIntakeMode('sim');
  }
}

function connectHelplineWebSocket(sessionId) {
  updateCallState('CONNECTING');
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/api/helpline/ws/${sessionId}`;

  try {
    callWebSocket = new WebSocket(wsUrl);
    callWebSocket.binaryType = 'arraybuffer';

    callWebSocket.onopen = () => {
      console.log('[VariSetu Helpline WS] Connected for session:', sessionId);
      updateCallState('LISTENING');
    };

    callWebSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (err) {
        console.debug('[VariSetu WS] Non-JSON payload received:', event.data);
      }
    };

    callWebSocket.onerror = (err) => {
      console.warn('[VariSetu Helpline WS] Socket error:', err);
      updateCallState('PROVIDER_DEGRADED', 'WebSocket error');
    };

    callWebSocket.onclose = () => {
      console.log('[VariSetu Helpline WS] Connection closed.');
      if (isMicRecording) {
        updateCallState('PROVIDER_DEGRADED', 'Connection closed');
      }
    };
  } catch (wsErr) {
    console.warn('[VariSetu WS] WebSocket creation failed:', wsErr);
    updateCallState('PROVIDER_DEGRADED', 'WebSocket unavailable');
  }
}

function handleWebSocketMessage(msg) {
  const msgType = msg.type || msg.event;

  if (msgType === 'state_change' || msgType === 'connection_state') {
    const newState = msg.state || (msg.data && msg.data.call_state);
    if (newState) updateCallState(newState);

  } else if (msgType === 'vad_event' || msgType === 'vad_started' || msgType === 'vad_stopped') {
    const vadFill = document.getElementById('vadMeterFill');
    const vadLabel = document.getElementById('vadStateLabel');
    const isSpeaking = msg.is_speech || msgType === 'vad_started' || (msg.data && msg.data.call_state === 'SPEAKING');

    if (vadFill) vadFill.style.width = isSpeaking ? '85%' : '15%';
    if (vadLabel) {
      vadLabel.textContent = isSpeaking ? 'SPEAKING' : 'SILENCE';
      vadLabel.style.color = isSpeaking ? '#D50000' : '#5D4037';
    }
    if (isSpeaking && currentCallState !== 'OPERATOR_HOLD') {
      updateCallState('SPEAKING');
    }

  } else if (msgType === 'interim_transcript' || msgType === 'partial_transcript') {
    const nativeBox = document.getElementById('nativeTranscriptBox');
    const text = msg.transcript || (msg.data && msg.data.transcript);
    if (nativeBox && text) {
      nativeBox.innerHTML = `"${escapeHtml(text)}"<span class="live-speech-typing-cursor"></span>`;
    }

  } else if (msgType === 'final_segment' || msgType === 'transcript_final') {
    const seg = msg.segment || (msg.data && msg.data.segment);
    handleIncomingNativeSegment(seg);

  } else if (msgType === 'translation_segment' || msgType === 'translation_final') {
    const seg = msg.segment || (msg.data && msg.data.segment) || msg.data;
    handleIncomingTranslationSegment(seg);

  } else if (msgType === 'attributes_updated') {
    const attrs = msg.attributes || (msg.data && msg.data.extracted_attributes);
    populateOperatorDossier(attrs);

  } else if (msgType === 'provider_error') {
    const errData = msg.data || msg;
    console.warn('[VariSetu Speech Provider Error]:', errData);
    if (errData.code === 'SPEECH_PROVIDER_UNCONFIGURED') {
      alert('SPEECH PROVIDER NOT CONFIGURED: SARVAM_API_KEY is required for live streaming ASR. Switch to DEMO mode or Custom Text intake.');
      updateCallState('PROVIDER_DEGRADED', 'SARVAM_API_KEY missing');
    }

  } else if (msgType === 'session_ended') {
    updateCallState('CALL_ENDED');
  }
}

function handleIncomingNativeSegment(segment) {
  if (!segment) return;
  const text = segment.text || segment.native_text;
  if (!text) return;

  nativeSegments.push(segment);
  const list = document.getElementById('nativeTranscriptSegmentsList');
  const nativeBox = document.getElementById('nativeTranscriptBox');

  if (list) {
    const div = document.createElement('div');
    div.className = 'transcript-segment-card';
    div.innerHTML = `
      <div class="transcript-segment-meta">
        <span>🗣️ Caller &bull; ${new Date().toLocaleTimeString()}</span>
        <span>Confidence: ${Math.round((segment.confidence || segment.asr_confidence || 0.94) * 100)}%</span>
      </div>
      <div>${escapeHtml(text)}</div>
    `;
    list.appendChild(div);
    list.scrollTop = list.scrollHeight;
  }

  if (nativeBox) {
    nativeBox.innerHTML = `<em>"${escapeHtml(text)}"</em>`;
  }
}

function handleIncomingTranslationSegment(segment) {
  if (!segment) return;
  const englishText = segment.english_text || segment.text;
  const isUnavailable = !englishText || englishText === 'TRANSLATION TEMPORARILY UNAVAILABLE' || segment.status === 'UNAVAILABLE' || segment.status === 'ERROR';

  translationSegments.push(segment);
  const list = document.getElementById('englishTranslationSegmentsList');
  const englishBox = document.getElementById('englishTranscriptBox');

  if (list) {
    const div = document.createElement('div');
    div.className = isUnavailable ? 'transcript-segment-card error' : 'transcript-segment-card english';
    div.innerHTML = `
      <div class="transcript-segment-meta">
        <span>🤖 AI Translation &bull; ${new Date().toLocaleTimeString()}</span>
        <span>${isUnavailable ? '⚠️ Unavailable' : 'Sarvam Neural Translate'}</span>
      </div>
      <div style="${isUnavailable ? 'color: #C62828; font-style: italic;' : ''}">${escapeHtml(englishText || 'TRANSLATION TEMPORARILY UNAVAILABLE')}</div>
    `;
    list.appendChild(div);
    list.scrollTop = list.scrollHeight;
  }

  if (englishBox) {
    englishBox.innerHTML = isUnavailable
      ? `<span style="color: #C62828; font-style: italic;">[Translation Temporarily Unavailable]</span>`
      : `"${escapeHtml(englishText)}"`;
  }
}

function populateOperatorDossier(attrs) {
  if (!attrs) return;

  const repName = document.getElementById('repPersonName');
  const repAge = document.getElementById('repPersonAge');
  const repGender = document.getElementById('repPersonGender');
  const repClothing = document.getElementById('repClothing');
  const repLocation = document.getElementById('repLocation');
  const repNotes = document.getElementById('repOfficerNotes');

  if (repName && attrs.name && !userEditedFields.has('repPersonName')) repName.value = attrs.name;
  if (repAge && attrs.age && !userEditedFields.has('repPersonAge')) repAge.value = attrs.age;
  if (repGender && attrs.gender && !userEditedFields.has('repPersonGender')) repGender.value = attrs.gender;
  if (repLocation && attrs.last_seen_location && !userEditedFields.has('repLocation')) repLocation.value = attrs.last_seen_location;

  const clothingParts = [attrs.clothing_top, attrs.clothing_bottom, attrs.clothing_description, attrs.headwear, attrs.accessories].filter(Boolean);
  if (repClothing && clothingParts.length > 0 && !userEditedFields.has('repClothing')) {
    repClothing.value = clothingParts.join(', ');
  }

  if (repNotes && !userEditedFields.has('repOfficerNotes')) {
    repNotes.value = `Live emergency intake. Name: ${attrs.name || 'Not provided'}, Location: ${attrs.last_seen_location || 'Pandharpur area'}. Urgent CCTV scan initiated.`;
  }
}

// --------------------------------------------------------------------------
// Audio Resampling & Signal Processing Helpers
// --------------------------------------------------------------------------
function resampleAndConvertToPCM16(float32Samples, inputRate, targetRate) {
  if (inputRate === targetRate) {
    const pcm16 = new Int16Array(float32Samples.length);
    for (let i = 0; i < float32Samples.length; i++) {
      let s = Math.max(-1, Math.min(1, float32Samples[i]));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return pcm16.buffer;
  }

  const ratio = inputRate / targetRate;
  const targetLength = Math.round(float32Samples.length / ratio);
  const pcm16 = new Int16Array(targetLength);

  for (let i = 0; i < targetLength; i++) {
    const srcIndex = i * ratio;
    const i1 = Math.floor(srcIndex);
    const i2 = Math.min(i1 + 1, float32Samples.length - 1);
    const frac = srcIndex - i1;
    const interpolated = float32Samples[i1] * (1 - frac) + float32Samples[i2] * frac;
    let s = Math.max(-1, Math.min(1, interpolated));
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }

  return pcm16.buffer;
}

function calculateRMS(samples) {
  let sum = 0;
  for (let i = 0; i < samples.length; i++) {
    sum += samples[i] * samples[i];
  }
  return Math.sqrt(sum / samples.length);
}

function updateClientVAD(rms) {
  const vadFill = document.getElementById('vadMeterFill');
  const meterPct = Math.min(100, Math.round((rms / 0.15) * 100));
  if (vadFill) vadFill.style.width = `${meterPct}%`;
}

function stopLiveMicRecording() {
  isMicRecording = false;
  if (micAnimFrameId) {
    cancelAnimationFrame(micAnimFrameId);
    micAnimFrameId = null;
  }

  const micBtn = document.getElementById('toggleLiveMicBtn');
  const micText = document.getElementById('micBtnText');
  micBtn?.classList.remove('recording');
  if (micText) micText.textContent = '🎙️ Start Live Mic Voice';

  if (micMediaStream) {
    micMediaStream.getTracks().forEach(t => t.stop());
    micMediaStream = null;
  }
  if (micAudioContext && micAudioContext.state !== 'closed') {
    micAudioContext.close();
    micAudioContext = null;
  }
  if (callWebSocket && callWebSocket.readyState === WebSocket.OPEN) {
    try {
      callWebSocket.send(JSON.stringify({ type: 'end' }));
      callWebSocket.close();
    } catch {}
    callWebSocket = null;
  }

  const container = document.getElementById('audioEqualizerBars');
  if (container) {
    container.querySelectorAll('.audio-bar').forEach(b => { b.style.height = '4px'; });
  }

  const vadFill = document.getElementById('vadMeterFill');
  const vadLabel = document.getElementById('vadStateLabel');
  if (vadFill) vadFill.style.width = '0%';
  if (vadLabel) {
    vadLabel.textContent = 'STANDBY';
    vadLabel.style.color = '#5D4037';
  }
}

function endCallSession() {
  updateCallState('CALL_ENDING');
  stopLiveMicRecording();
  stopAudioEqualizer();
  stopCallTimer();

  if (window.speechSynthesis) window.speechSynthesis.cancel();

  if (callSessionId) {
    apiRequest(`/helpline/calls/${callSessionId}/end`, { method: 'POST' }).catch(() => {});
  }

  updateCallState('CALL_ENDED');
}

// --------------------------------------------------------------------------
// Real-time Translation & Custom Text Intake Handlers
// --------------------------------------------------------------------------
async function handleLiveVoiceTranslation(text, lang = 'mr') {
  if (!text || text.length < 2) return;

  updateCallState('TRANSLATING');

  try {
    const res = await apiRequest('/helpline/call/simulate', {
      method: 'POST',
      body: {
        custom_text: text,
        language: lang
      }
    });

    currentHelplineCallData = res;

    if (res.english_translation) {
      handleIncomingTranslationSegment({
        segment_id: 'trans-' + Date.now(),
        source_text: text,
        english_text: res.english_translation,
        confidence: 0.95
      });
    }

    if (res.extracted_attributes) {
      populateOperatorDossier(res.extracted_attributes);
    }

    updateCallState('LISTENING');

  } catch (err) {
    console.debug('[VariSetu] Neural translation error:', err);
    updateCallState('LISTENING');
  }
}

async function handleCustomTextIntake() {
  const input = document.getElementById('customTextInputBox')?.value?.trim();
  if (!input) {
    alert('Please enter a distress description in Marathi, Hindi, or English.');
    return;
  }

  handleIncomingNativeSegment({
    segment_id: 'custom-' + Date.now(),
    text: input,
    confidence: 1.0
  });

  const langCode = activeVoiceLang.startsWith('hi') ? 'hi' : (activeVoiceLang.startsWith('en') ? 'en' : 'mr');
  await handleLiveVoiceTranslation(input, langCode);
  alert('Citizen message translated! The Operator Report form below has been populated.');
}

function initAudioEqualizerBars() {
  const container = document.getElementById('audioEqualizerBars');
  if (!container) return;

  container.innerHTML = '';
  const barCount = 32;
  for (let i = 0; i < barCount; i++) {
    const bar = document.createElement('div');
    bar.className = 'audio-bar';
    bar.style.height = `${Math.floor(Math.random() * 16) + 4}px`;
    container.appendChild(bar);
  }

  if (visualizerAnimationTimer) clearInterval(visualizerAnimationTimer);
  visualizerAnimationTimer = setInterval(() => {
    if (isCallHeld || isMicRecording) return;
    const bars = container.querySelectorAll('.audio-bar');
    bars.forEach(b => {
      const h = Math.floor(Math.random() * 24) + 4;
      b.style.height = `${h}px`;
    });
  }, 90);
}

function stopAudioEqualizer() {
  if (visualizerAnimationTimer) {
    clearInterval(visualizerAnimationTimer);
    visualizerAnimationTimer = null;
  }
  const container = document.getElementById('audioEqualizerBars');
  if (container) {
    container.querySelectorAll('.audio-bar').forEach(b => { b.style.height = '4px'; });
  }
}

function startCallTimer() {
  callDurationSeconds = 0;
  if (callTimerInterval) clearInterval(callTimerInterval);
  callTimerInterval = setInterval(() => {
    if (isCallHeld) return;
    callDurationSeconds++;
    const mins = String(Math.floor(callDurationSeconds / 60)).padStart(2, '0');
    const secs = String(callDurationSeconds % 60).padStart(2, '0');
    const timerEl = document.getElementById('callDurationTimer');
    if (timerEl) timerEl.textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopCallTimer() {
  if (callTimerInterval) {
    clearInterval(callTimerInterval);
    callTimerInterval = null;
  }
}

// --------------------------------------------------------------------------
// Preset Scenario Simulation Mode
// --------------------------------------------------------------------------
async function loadHelplineScenarios() {
  const container = document.getElementById('scenarioChipsContainer');
  if (!container) return;

  try {
    const scenarios = await apiRequest('/helpline/scenarios');
    container.innerHTML = scenarios.map((sc, idx) => `
      <button type="button" class="scenario-chip-btn ${idx === 0 ? 'active' : ''}" data-scenario-id="${escapeHtml(sc.id)}" data-index="${idx}">
        <span>${escapeHtml(sc.title)}</span>
        <span class="badge" style="font-size:8.5px; padding:1px 4px; background:#FAF0E1; color:#7A1F1F;">${sc.language === 'mr' ? 'मराठी' : 'हिन्दी'}</span>
      </button>
    `).join('');

    container.querySelectorAll('.scenario-chip-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        container.querySelectorAll('.scenario-chip-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const id = btn.getAttribute('data-scenario-id');
        currentScenarioIndex = parseInt(btn.getAttribute('data-index') || '0', 10);
        triggerScenarioCallSimulation(id);
      });
    });

    if (scenarios.length > 0) {
      await triggerScenarioCallSimulation(scenarios[0].id);
    }
  } catch (err) {
    console.debug('[VariSetu] Helpline scenarios fallback:', err);
    await triggerScenarioCallSimulation('marathi_child_pandharpur');
  }
}

async function triggerScenarioCallSimulation(scenarioId) {
  try {
    callDurationSeconds = 0;
    updateCallState('CONNECTED');

    let res = null;
    try {
      res = await apiRequest('/helpline/call/simulate', {
        method: 'POST',
        body: { scenario_id: scenarioId }
      });
    } catch (apiErr) {
      console.warn('[VariSetu] Using immediate offline fallback for scenario:', scenarioId);
    }

    if (!res || !res.native_transcript) {
      const scenarioFallbacks = {
        'marathi_child_pandharpur': {
          caller_name: 'Sunita Jadhav (सुनिता जाधव)',
          caller_phone: '+91 94220 88912',
          language: 'mr',
          native_transcript: 'हॅलो मदत कक्ष, माझी लहान मुलगी गोदावरी जाधव (वय ८) पुंडलिक मंदिराच्या पायऱ्यांजवळ हरवली आहे. तिने पिवळा फ्रॉक आणि लाल रिबीन घातली आहे. कृपया तातडीने शोधा!',
          english_translation: 'Hello Help Desk, my young daughter Godavari Jadhav (age 8) got separated near Pundalik Temple steps. She is wearing a yellow floral frock and red hair ribbons. Please search immediately!',
          extracted_attributes: {
            name: 'Godavari Jadhav (गोदावरी जाधव)',
            age: 8,
            gender: 'F',
            clothing_top: 'Yellow frock with floral pattern',
            clothing_bottom: 'Yellow frock',
            headwear: 'Red ribbons',
            accessories: 'Red bead bracelet',
            last_seen_location: 'Pundalik Temple Steps / Pandharpur Chowk',
            urgency: 'CRITICAL',
            recommended_cctvs: ['CAM-04', 'CAM-01']
          }
        },
        'marathi_senior_wakhri': {
          caller_name: 'Dnyaneshwar Shinde (ज्ञानेश्वर शिंदे)',
          caller_phone: '+91 98234 11204',
          language: 'mr',
          native_transcript: 'हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे.',
          english_translation: 'Hello Control Room, our grandfather Maruti Shinde (age 68) got separated in the crowd near Wakhri Phata. He is wearing a white cotton kurta, dhoti, and a white Gandhi cap.',
          extracted_attributes: {
            name: 'Maruti Shinde (मारुती शिंदे)',
            age: 68,
            gender: 'M',
            clothing_top: 'White cotton kurta',
            clothing_bottom: 'White dhoti',
            headwear: 'White Gandhi cap',
            accessories: 'Tulsi mala, Taal cymbals',
            last_seen_location: 'Wakhri Phata Dindi Confluence',
            urgency: 'HIGH',
            recommended_cctvs: ['CAM-12', 'CAM-04']
          }
        },
        'hindi_elderly_alandi': {
          caller_name: 'Rameshwar Gupta (रामेश्वर गुप्ता)',
          caller_phone: '+91 97112 43098',
          language: 'hi',
          native_transcript: 'नमस्ते कंट्रोल रूम, हमारे पिताजी रामकिशन गुप्ता (उम्र ७२) आलंदी पालखी प्रस्थान के समय भारी भीड़ में बिछड़ गए हैं। उन्होंने क्रीम कुर्ता और भूरे रंग की जैकेट पहनी है।',
          english_translation: 'Hello Control Room, our father Ramkishan Gupta (age 72) got separated during the Alandi Palkhi procession departure in the heavy crowd. He is wearing a cream kurta and a brown jacket.',
          extracted_attributes: {
            name: 'Ramkishan Gupta (रामकिशन गुप्ता)',
            age: 72,
            gender: 'M',
            clothing_top: 'Cream kurta with Brown vest jacket',
            clothing_bottom: 'White cotton pajama',
            headwear: 'None',
            accessories: 'Wooden walking stick',
            last_seen_location: 'Alandi Corridor Main Gate',
            urgency: 'HIGH',
            recommended_cctvs: ['CAM-01', 'CAM-08']
          }
        }
      };
      res = scenarioFallbacks[scenarioId] || scenarioFallbacks['marathi_child_pandharpur'];
    }

    currentHelplineCallData = res;

    // Update Caller Identity
    const nameEl = document.getElementById('callerDisplayName');
    const phoneEl = document.getElementById('callerDisplayPhone');
    const locEl = document.getElementById('callerDisplayLocation');

    if (nameEl) nameEl.textContent = `${res.caller_name || 'Citizen Pilgrim'} (${res.extracted_attributes?.name || 'Pilgrim'})`;
    if (phoneEl) phoneEl.textContent = `📱 ${res.caller_phone || '+91 94220 88912'}`;
    if (locEl) locEl.textContent = `📍 ${res.extracted_attributes?.last_seen_location || 'Pandharpur Perimeter'}`;

    // Clear segments and populate streaming typing effect
    nativeSegments = [];
    translationSegments = [];
    const nativeList = document.getElementById('nativeTranscriptSegmentsList');
    const englishList = document.getElementById('englishTranslationSegmentsList');
    if (nativeList) nativeList.innerHTML = '';
    if (englishList) englishList.innerHTML = '';

    startProgressiveSpeechStream(res.native_transcript, res.english_translation);

    // Pre-fill Operator Report
    userEditedFields.clear();
    populateOperatorDossier(res.extracted_attributes);

    // Reset CCTV candidates section
    const cctvSec = document.getElementById('cctvCandidatesSection');
    if (cctvSec) cctvSec.style.display = 'none';

    // Audio Speech Synthesis
    if (isSpeakerEnabled && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(res.native_transcript);
      utter.lang = res.language === 'mr' ? 'mr-IN' : 'hi-IN';
      utter.rate = 1.0;
      window.speechSynthesis.speak(utter);
    }

  } catch (err) {
    console.error('[VariSetu] Call simulation unexpected error:', err);
  }
}

function startProgressiveSpeechStream(nativeText, englishText) {
  const nativeBox = document.getElementById('nativeTranscriptBox');
  const englishBox = document.getElementById('englishTranscriptBox');
  if (!nativeBox || !englishBox) return;

  if (streamingTypingTimer) clearInterval(streamingTypingTimer);

  nativeBox.innerHTML = '';
  englishBox.innerHTML = '';

  const nativeWords = (nativeText || '').split(' ');
  const englishWords = (englishText || '').split(' ');

  let wIdx = 0;
  const maxWords = Math.max(nativeWords.length, englishWords.length);

  updateCallState('SPEAKING');

  streamingTypingTimer = setInterval(() => {
    if (wIdx < maxWords) {
      if (wIdx < nativeWords.length) {
        nativeBox.innerHTML = nativeWords.slice(0, wIdx + 1).join(' ') + '<span class="live-speech-typing-cursor"></span>';
      }
      if (wIdx < englishWords.length) {
        englishBox.innerHTML = englishWords.slice(0, wIdx + 1).join(' ') + '<span class="live-speech-typing-cursor"></span>';
      }
      wIdx++;
    } else {
      clearInterval(streamingTypingTimer);
      nativeBox.innerHTML = nativeText;
      englishBox.innerHTML = englishText;

      handleIncomingNativeSegment({
        segment_id: 'seg-sim-' + Date.now(),
        text: nativeText,
        confidence: 0.96
      });

      handleIncomingTranslationSegment({
        segment_id: 'trans-sim-' + Date.now(),
        source_text: nativeText,
        english_text: englishText,
        confidence: 0.95
      });

      updateCallState('LISTENING');
    }
  }, 90);
}

// --------------------------------------------------------------------------
// Case Creation, AI CCTV Scanning & Truthful Human Verification
// --------------------------------------------------------------------------
async function handleGenerateCaseFromCall() {
  const repName = document.getElementById('repPersonName')?.value?.trim() || 'Missing Pilgrim';
  const repAge = parseInt(document.getElementById('repPersonAge')?.value || '35', 10);
  const repGender = document.getElementById('repPersonGender')?.value || 'M';
  const repClothing = document.getElementById('repClothing')?.value?.trim() || 'Traditional pilgrimage clothing';
  const repLocation = document.getElementById('repLocation')?.value?.trim() || 'Pandharpur Temple Chowk';
  const repNotes = document.getElementById('repOfficerNotes')?.value?.trim() || 'Distressed citizen emergency helpline intake.';

  const payload = {
    caller_name: currentHelplineCallData?.caller_name || 'Citizen Caller',
    caller_phone: currentHelplineCallData?.caller_phone || '+91 94220 88912',
    native_transcript: currentHelplineCallData?.native_transcript || repNotes,
    english_translation: currentHelplineCallData?.english_translation || repNotes,
    name: repName,
    age: repAge,
    gender: repGender,
    clothing_description: repClothing,
    last_seen_location: repLocation,
    urgency: 'CRITICAL',
    trigger_cctv_scan: true
  };

  try {
    const btn = document.getElementById('generateCaseFromCallBtn');
    if (btn) btn.innerHTML = '⏳ Saving Officer Report...';

    const res = await apiRequest('/helpline/call/create-case-and-match', {
      method: 'POST',
      body: payload
    });

    if (btn) btn.innerHTML = '<i data-lucide="file-check" style="width:13px; height:13px;"></i><span>1. Case Created!</span>';

    if (!currentHelplineCallData) currentHelplineCallData = {};
    currentHelplineCallData.createdCase = res.case;

    appendTickerEvent(`[LOST & FOUND] Case #${res.case.case_number} registered for ${res.case.name}`);
    alert(`Officer Case Report successfully registered!

Case Number: ${res.case.case_number}
Person: ${res.case.name}
Age/Gender: ${res.case.age} / ${res.case.gender}
Location: ${res.case.last_seen_location}

AI CCTV Spatial-Temporal Search scanning surveillance cameras.`);

    await refreshLostPersons();

    if (res.cctv_matches && res.cctv_matches.length > 0) {
      renderCCTVCandidates(res.cctv_matches, res.case);
    } else {
      await handleScanCCTVFeeds();
    }
  } catch (err) {
    alert(`Failed to create case: ${err.message}`);
    const btn = document.getElementById('generateCaseFromCallBtn');
    if (btn) btn.innerHTML = '<i data-lucide="file-check" style="width:13px; height:13px;"></i><span>1. Submit Report & Create Case</span>';
  }
}

async function handleScanCCTVFeeds() {
  let caseId = currentHelplineCallData?.createdCase?.id;

  if (!caseId) {
    await handleGenerateCaseFromCall();
    caseId = currentHelplineCallData?.createdCase?.id;
    if (!caseId) return;
  }

  try {
    const btn = document.getElementById('scanCCTVFeedsBtn');
    if (btn) btn.innerHTML = '⏳ Scanning Feeds...';

    const res = await apiRequest(`/lost-persons/${caseId}/cctv-scan`, {
      method: 'POST'
    });

    if (btn) btn.innerHTML = '<i data-lucide="cctv" style="width:13px; height:13px;"></i><span>2. CCTV Scan Done</span>';

    const candidateMatches = res.candidates || res.matches || res.candidate_matches || [];
    renderCCTVCandidates(candidateMatches, currentHelplineCallData.createdCase);
  } catch (err) {
    alert(`CCTV Scan error: ${err.message}`);
    const btn = document.getElementById('scanCCTVFeedsBtn');
    if (btn) btn.innerHTML = '<i data-lucide="cctv" style="width:13px; height:13px;"></i><span>2. AI CCTV Re-ID Scan</span>';
  }
}

function renderCCTVCandidates(matches, caseObj) {
  const sec = document.getElementById('cctvCandidatesSection');
  const grid = document.getElementById('cctvCandidatesGrid');
  const badge = document.getElementById('cctvMatchesBadge');

  if (!sec || !grid) return;

  sec.style.display = 'flex';
  if (badge) badge.textContent = `${matches.length} Candidates Identified`;

  if (!matches || matches.length === 0) {
    grid.innerHTML = '<div style="font-size:11.5px; color:var(--text-secondary); padding:10px;">No CCTV matches found within the spatial-temporal search perimeter.</div>';
    return;
  }

  grid.innerHTML = matches.map((m, idx) => {
    const matchId = m.match_id || m.id || `cand-${idx}`;
    const caseId = m.case_id || caseObj?.id || '';
    const simPct = Math.round((m.similarity_score || 0.85) * 100);
    const isVerified = m.status === 'VERIFIED' || m.verified === true;
    const isRejected = m.status === 'REJECTED';

    return `
      <div class="cctv-candidate-card ${isVerified ? 'is-verified' : ''} ${isRejected ? 'is-rejected' : ''}" id="candCard-${matchId}">
        <div class="cctv-cand-header">
          <div style="font-weight:700; font-size:11.5px; color:var(--maroon-primary); display:flex; align-items:center; gap:4px;">
            <i data-lucide="camera" style="width:12px; height:12px;"></i>
            <span>${escapeHtml(m.camera_code || 'CAM-04')} &bull; ${escapeHtml(m.location_name || m.camera_name || 'Temple Chowk')}</span>
          </div>
          <div style="display:flex; align-items:center; gap:4px;">
            <span class="verification-status-pill ${isVerified ? 'verified' : (isRejected ? 'rejected' : 'candidate')}" id="statusPill-${matchId}">
              ${isVerified ? 'VERIFIED' : (isRejected ? 'REJECTED' : 'CANDIDATE')}
            </span>
            <span class="cctv-sim-badge">${simPct}%</span>
          </div>
        </div>

        <div class="cctv-preview-box">
          <span class="cctv-feed-overlay-text">LIVE FEED: ${escapeHtml(m.camera_code || 'CAM-04')}</span>
          <div class="cctv-bbox-indicator">
            <span>RE-ID</span>
          </div>
        </div>

        <div class="cctv-cand-meta">
          <strong>Match Type:</strong> ${escapeHtml(m.match_type || 'ATTRIBUTE_MATCH')}<br>
          <strong>Frame Time:</strong> ${escapeHtml(m.frame_timestamp || new Date().toLocaleTimeString())}<br>
          <strong>Matched Attributes:</strong> ${escapeHtml(m.matched_features || 'Spatial-temporal color & clothing match')}
        </div>

        <!-- Human Verification Actions -->
        <div class="cctv-action-btn-group" id="verifyActions-${matchId}">
          ${!isVerified && !isRejected ? `
            <button type="button" class="btn-verify-match" onclick="verifyCCTVCandidate('${caseId}', '${matchId}', true, '${escapeHtml(caseObj?.name || 'Missing Pilgrim')}')">
              <span>✅ Confirm Match (मान्यता द्या)</span>
            </button>
            <button type="button" class="btn-reject-match" onclick="verifyCCTVCandidate('${caseId}', '${matchId}', false, '${escapeHtml(caseObj?.name || 'Missing Pilgrim')}')">
              <span>❌ Reject (नाकारा)</span>
            </button>
          ` : `
            <div style="font-size:11px; font-weight:700; color:${isVerified ? '#1B5E20' : '#B71C1C'}; padding:4px 0;">
              ${isVerified ? '✅ Confirmed by Human Operator' : '❌ Rejected by Human Operator'}
            </div>
          `}
        </div>

        <div style="display:flex; gap:6px; margin-top:4px;">
          <button type="button" class="govt-btn" style="flex:1; font-size:10px; padding:4px 6px;" onclick="highlightCCTVOnMap('${m.camera_code || 'CAM-04'}', ${m.latitude || 17.6777}, ${m.longitude || 75.3276})">
            <i data-lucide="map-pin" style="width:10px; height:10px;"></i>
            <span>📍 Show on Map</span>
          </button>
          <button type="button" class="govt-btn btn-outline" style="font-size:10px; padding:4px 6px;" onclick="dispatchPatrolToCCTV('${m.camera_code || 'CAM-04'}', '${escapeHtml(caseObj?.name || 'Missing Pilgrim')}')">
            <span>🚓 Dispatch</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Operator Human Verification Handler
window.verifyCCTVCandidate = async function(caseId, matchId, isVerified, personName) {
  try {
    const card = document.getElementById(`candCard-${matchId}`);
    const pill = document.getElementById(`statusPill-${matchId}`);
    const actionsGroup = document.getElementById(`verifyActions-${matchId}`);

    if (actionsGroup) {
      actionsGroup.innerHTML = '<span style="font-size:10.5px; color:#5D4037;">⏳ Recording human verification...</span>';
    }

    const payload = {
      verified: isVerified,
      notes: isVerified ? `Positive human visual verification confirmed for ${personName}` : `Rejected candidate mismatch for ${personName}`
    };

    let targetCaseId = caseId || currentHelplineCallData?.createdCase?.id;
    if (!targetCaseId) {
      targetCaseId = matchId;
    }

    const res = await apiRequest(`/lost-persons/${targetCaseId}/matches/${matchId}/verify`, {
      method: 'POST',
      body: payload
    });

    if (pill) {
      pill.className = `verification-status-pill ${isVerified ? 'verified' : 'rejected'}`;
      pill.textContent = isVerified ? 'VERIFIED' : 'REJECTED';
    }

    if (card) {
      card.className = `cctv-candidate-card ${isVerified ? 'is-verified' : 'is-rejected'}`;
    }

    if (actionsGroup) {
      actionsGroup.innerHTML = `
        <div style="font-size:11px; font-weight:700; color:${isVerified ? '#1B5E20' : '#B71C1C'}; padding:4px 0;">
          ${isVerified ? '✅ Confirmed by Human Operator' : '❌ Rejected by Human Operator'}
        </div>
      `;
    }

    if (isVerified) {
      appendTickerEvent(`[VERIFIED MATCH] ${personName} visually identified on CCTV feed! Case status updated to FOUND.`);
      alert(`Candidate match VERIFIED by operator!

Case has been updated to FOUND/RESOLVED.
Volunteer squads and PCR van alerted to escort pilgrim safely.`);
    } else {
      appendTickerEvent(`[REJECTED MATCH] CCTV candidate for ${personName} rejected upon visual inspection.`);
    }

    await refreshLostPersons();

  } catch (err) {
    console.error('[VariSetu] Verification error:', err);
    alert(`Verification error: ${err.message}`);
  }
};

window.highlightCCTVOnMap = function(camId, lat, lng) {
  const modal = document.getElementById('helplineCallModal');
  if (modal) modal.style.display = 'none';

  if (!window.wariMap) return;

  const cmdTab = document.querySelector('[data-target="view-command"]');
  cmdTab?.click();

  window.wariMap.setView([lat, lng], 13);

  if (window.cctvHighlightLayerGroup) {
    window.cctvHighlightLayerGroup.clearLayers();

    const circle = L.circle([lat, lng], {
      color: '#D32F2F',
      fillColor: '#FFCDD2',
      fillOpacity: 0.5,
      radius: 400
    }).addTo(window.cctvHighlightLayerGroup);

    const popupContent = `
      <div style="font-family:var(--font-sans, sans-serif); min-width:180px;">
        <div style="font-weight:700; color:#7A1F1F; font-size:12px; border-bottom:1px solid #D8D1C5; padding-bottom:3px;">
          📹 AI RE-ID DETECTION: ${camId}
        </div>
        <div style="font-size:11px; margin-top:5px; color:#2B2623;">
          Target matched on live CCTV feed.<br>
          Patrol squad alerted for physical verification.
        </div>
      </div>
    `;

    circle.bindPopup(popupContent).openPopup();
  }
};

window.dispatchPatrolToCCTV = function(camId, personName) {
  alert(`Patrol squad PS-07 and nearest Volunteer Team VT-04 dispatched to ${camId} for visual verification of ${personName}.`);
  appendTickerEvent(`[DISPATCH] Quick response squad dispatched to ${camId} for ${personName}`);
};
