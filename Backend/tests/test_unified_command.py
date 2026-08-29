import pytest


async def get_admin_headers(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def get_police_headers(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.police@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_command_picture_aggregation(client):
    """Test GET /api/dashboard/command-picture returns the complete Common Operating Picture."""
    headers = await get_admin_headers(client)

    res = await client.get("/api/dashboard/command-picture", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Validate high-level contract
    assert "system_health" in data
    assert "summary" in data
    assert "freshness" in data
    assert "yatra" in data
    assert "critical_incidents" in data
    assert "active_incidents" in data
    assert "active_medical_alerts" in data
    assert "active_lost_cases" in data
    assert "face_match_candidates" in data
    assert "deployed_resources" in data
    assert "available_resources" in data
    assert "routes" in data
    assert "corridor_segments" in data
    assert "route_recommendations" in data
    assert "resource_recommendations" in data
    assert "recent_actions" in data
    assert "incident_timeline" in data
    assert "heatmap_points" in data

    # Validate freshness metrics
    assert data["freshness"]["gis_provider"] == "GOOGLE_MAPS"
    assert data["freshness"]["data_age_seconds"] >= 0

    # Validate Yatra live object
    assert data["yatra"]["name"] == "Sant Tukaram Maharaj Palkhi"
    assert data["yatra"]["latitude"] > 0
    assert data["yatra"]["longitude"] > 0


@pytest.mark.asyncio
async def test_action_execution_and_idempotency(client):
    """Test POST /api/actions executes transactionally and prevents duplicate execution via idempotency_key."""
    headers = await get_admin_headers(client)

    # 1. Dispatch an ambulance
    action_payload = {
        "action_type": "DISPATCH_AMBULANCE",
        "target_type": "RESOURCE",
        "target_id": "r-res-amb-01",
        "priority": "CRITICAL",
        "parameters": {"destination": "Wakhri Phata Sector 4"},
        "idempotency_key": "idem-test-ambulance-001"
    }

    res1 = await client.post("/api/actions", json=action_payload, headers=headers)
    assert res1.status_code == 201
    action_data1 = res1.json()
    assert action_data1["status"] == "SUCCEEDED"
    assert action_data1["action_type"] == "DISPATCH_AMBULANCE"

    # 2. Resend exact same action with same idempotency key (must return existing action without duplicate error)
    res2 = await client.post("/api/actions", json=action_payload, headers=headers)
    assert res2.status_code == 201
    action_data2 = res2.json()
    assert action_data2["id"] == action_data1["id"]

    # 3. List actions
    list_res = await client.get("/api/actions", headers=headers)
    assert list_res.status_code == 200
    actions = list_res.json()
    assert len(actions) >= 1
    assert any(a["idempotency_key"] == "idem-test-ambulance-001" for a in actions)


@pytest.mark.asyncio
async def test_action_rbac_authorization(client):
    """Test RBAC enforcement on high-impact actions (e.g. Police role cannot change route or broadcast public alert)."""
    police_headers = await get_police_headers(client)

    forbidden_action = {
        "action_type": "CHANGE_ROUTE",
        "target_type": "ROUTE",
        "target_id": "r-solapur-01",
        "parameters": {"status": "DIVERTED"},
        "idempotency_key": "idem-police-forbidden-01"
    }

    res = await client.post("/api/actions", json=forbidden_action, headers=police_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_yatra_gps_ingestion_and_anomaly_rejection(client):
    """Test POST /api/yatra/track accepts valid Maharashtra GPS points and rejects out-of-boundary anomaly coordinates."""
    headers = await get_admin_headers(client)

    # 1. Valid telemetry point
    valid_point = {
        "tracker_id": "PALKHI-TUKARAM-01",
        "latitude": 17.7295,
        "longitude": 75.2965,
        "speed_kmph": 2.9,
        "heading": 148.0,
        "accuracy_meters": 4.5,
        "source": "GPS_DEVICE"
    }
    res_valid = await client.post("/api/yatra/track", json=valid_point, headers=headers)
    assert res_valid.status_code == 200
    live_out = res_valid.json()
    assert live_out["latitude"] == 17.7295
    assert live_out["longitude"] == 75.2965

    # 2. Anomaly coordinate outside Maharashtra (e.g. North Pole 88.0, 0.0) -> must fail 400
    invalid_point = {
        "tracker_id": "PALKHI-TUKARAM-01",
        "latitude": 88.0,
        "longitude": 0.0,
        "speed_kmph": 50.0
    }
    res_invalid = await client.post("/api/yatra/track", json=invalid_point, headers=headers)
    assert res_invalid.status_code == 400


@pytest.mark.asyncio
async def test_crowd_heatmap_and_corridor_density(client):
    """Test GET /api/crowd/heatmap returns normalized 0.0 - 1.0 weights for GPU rendering."""
    headers = await get_admin_headers(client)

    res = await client.get("/api/crowd/heatmap", headers=headers)
    assert res.status_code == 200
    points = res.json()
    assert len(points) >= 4
    for pt in points:
        assert 0.0 <= pt["weight"] <= 1.0
        assert "latitude" in pt
        assert "longitude" in pt
        assert "risk_level" in pt


@pytest.mark.asyncio
async def test_route_diversion_recommendations(client):
    """Test GET /api/routes/recommendations returns alternatives and impact estimates."""
    headers = await get_admin_headers(client)

    res = await client.get("/api/routes/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) >= 1
    rec = recs[0]
    assert "affected_route_name" in rec
    assert "alternative_route_name" in rec
    assert rec["distance_increase_km"] > 0
    assert rec["estimated_time_increase_minutes"] > 0


@pytest.mark.asyncio
async def test_public_announcements_workflow(client):
    """Test Public Announcements: Queue -> List -> Approve/Broadcast."""
    admin_headers = await get_admin_headers(client)

    # 1. Queue an announcement
    create_payload = {
        "message_mr": "कृपया वाखरी फाटा येथे पाणी वाटप केंद्राचा लाभ घ्यावा.",
        "message_en": "Please avail the water distribution facilities at Wakhri Phata.",
        "priority": "HIGH",
        "category": "PUBLIC_SAFETY"
    }
    create_res = await client.post("/api/announcements", json=create_payload, headers=admin_headers)
    assert create_res.status_code == 201
    ann = create_res.json()
    assert ann["status"] == "PENDING_APPROVAL"
    ann_id = ann["id"]

    # 2. List announcements
    list_res = await client.get("/api/announcements", headers=admin_headers)
    assert list_res.status_code == 200
    assert any(a["id"] == ann_id for a in list_res.json())

    # 3. Approve and broadcast
    broadcast_res = await client.post(f"/api/announcements/{ann_id}/broadcast", headers=admin_headers)
    assert broadcast_res.status_code == 200
    assert broadcast_res.json()["status"] == "BROADCAST"


@pytest.mark.asyncio
async def test_public_sanitized_yatra_endpoint(client):
    """Test GET /api/public/yatra/live is accessible unauthenticated and returns privacy-sanitized telemetry."""
    res = await client.get("/api/public/yatra/live")
    assert res.status_code == 200
    data = res.json()
    assert "name" in data
    assert "approximate_latitude" in data
    assert "approximate_longitude" in data
    assert "public_advisory" in data
    # Ensure sensitive private fields (e.g. tracker internal IDs) are not exposed
    assert "tracker_id" not in data
