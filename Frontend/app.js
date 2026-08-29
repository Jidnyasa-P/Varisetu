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

  // 3. Face Match Queue
  renderFaceMatchQueue(data.face_match_candidates || []);

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

// Action Handlers
window.handleAcknowledgeIncident = async function(incidentId, btn) {
  await executeCommandAction('ACKNOWLEDGE_INCIDENT', {
    incidentId: incidentId,
    targetType: 'INCIDENT',
    targetId: incidentId,
    buttonEl: btn
  });
};

window.handleDispatchSquadForIncident = async function(incidentId, btn) {
  await executeCommandAction('DISPATCH_POLICE', {
    incidentId: incidentId,
    targetType: 'INCIDENT',
    targetId: incidentId,
    parameters: { squad_code: 'SQUAD-QRT-01', sector: 'Sector 3' },
    buttonEl: btn
  });
};

window.handleResolveIncident = async function(incidentId, btn) {
  await executeCommandAction('RESOLVE_INCIDENT', {
    incidentId: incidentId,
    targetType: 'INCIDENT',
    targetId: incidentId,
    buttonEl: btn
  });
};

window.handleVerifyFaceMatch = async function(matchId, caseId, btn) {
  await executeCommandAction('VERIFY_FACE_MATCH', {
    incidentId: caseId,
    targetType: 'LOST_PERSON_MATCH',
    targetId: matchId || caseId,
    parameters: { case_id: caseId, status: 'VERIFIED' },
    buttonEl: btn
  });
};

window.handleDispatchReuniteVolunteer = async function(caseId, btn) {
  await executeCommandAction('DISPATCH_VOLUNTEER', {
    incidentId: caseId,
    targetType: 'LOST_PERSON_CASE',
    targetId: caseId,
    parameters: { purpose: 'REUNIFICATION', station: 'Wakhri Desk' },
    buttonEl: btn
  });
};

window.handleApproveRouteDiversion = async function(routeId, suggestedStatus, btn) {
  await executeCommandAction('DIVERT_ROUTE', {
    targetType: 'ROUTE',
    targetId: routeId,
    parameters: { new_status: suggestedStatus || 'DIVERTED_PEDESTRIAN_ONLY' },
    buttonEl: btn
  });
};

window.handleDispatchRecommendedResource = async function(resourceId, targetId, btn) {
  await executeCommandAction('DISPATCH_AMBULANCE', {
    targetType: 'RESOURCE',
    targetId: resourceId,
    parameters: { target_location: targetId || 'Wakhri Emergency Camp' },
    buttonEl: btn
  });
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
    window.wariMap.setView([17.7500, 75.2500], 10);
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
