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

