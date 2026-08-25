import pytest


@pytest.mark.asyncio
async def test_health_endpoints(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_dashboard_summary(client):
    res = await client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "active_incidents" in data
    assert "palkhi_location" in data
    assert "estimated_pilgrim_count" in data


@pytest.mark.asyncio
async def test_dashboard_heat_risk(client):
    res = await client.get("/api/dashboard/heat-risk")
    assert res.status_code == 200
    data = res.json()
    assert "ambient_temperature" in data
    assert "computed_risk_index" in data


@pytest.mark.asyncio
async def test_create_and_acknowledge_incident(client):
    # Create incident
    create_payload = {
        "title": "Pedestrian bottleneck test",
        "type": "CROWD",
        "severity": "HIGH",
        "description": "Dense crowd surge at sector 2",
        "source": "OPERATOR"
    }
    create_res = await client.post("/api/incidents", json=create_payload)
    assert create_res.status_code == 201
    inc_data = create_res.json()
    assert inc_data["status"] == "OPEN"
    inc_id = inc_data["id"]

    # Acknowledge incident
    ack_res = await client.post(f"/api/incidents/{inc_id}/acknowledge", json={"notes": "Controller dispatched patrol squad"})
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve incident
    res_res = await client.post(f"/api/incidents/{inc_id}/resolve", json={"resolution_notes": "Queue cleared"})
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_lost_person_workflow(client):
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
    case_res = await client.post("/api/lost-persons", json=case_payload)
    assert case_res.status_code == 201
    case_data = case_res.json()
    assert case_data["name"] == "Maruti Kisan Shinde"
    case_id = case_data["id"]

    # Dispatch volunteer
    disp_res = await client.post(f"/api/lost-persons/{case_id}/dispatch")
    assert disp_res.status_code == 200
    assert disp_res.json()["status"] == "DISPATCHED"

    # Reunite case
    reunite_res = await client.post(f"/api/lost-persons/{case_id}/reunite")
    assert reunite_res.status_code == 200
    assert reunite_res.json()["status"] == "REUNITED"

    # Purge sensitive biometric data (Privacy check)
    purge_res = await client.post(f"/api/lost-persons/{case_id}/purge-sensitive-data")
    assert purge_res.status_code == 200
    assert purge_res.json()["success"] is True


@pytest.mark.asyncio
async def test_medical_alert_workflow(client):
    # Create alert
    alert_payload = {
        "type": "FALL",
        "severity": "HIGH",
        "latitude": 17.7280,
        "longitude": 75.2950,
        "description": "Pilgrim fall detected at Wakhri junction"
    }
    alert_res = await client.post("/api/medical-alerts", json=alert_payload)
    assert alert_res.status_code == 201
    alert_data = alert_res.json()
    alert_id = alert_data["id"]
    assert alert_data["status"] == "ACTIVE"

    # Acknowledge alert
    ack_res = await client.post(f"/api/medical-alerts/{alert_id}/acknowledge", json={"assigned_volunteer_name": "Team Alpha"})
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve alert
    resolve_res = await client.post(f"/api/medical-alerts/{alert_id}/resolve", json={"resolution_notes": "First aid administered"})
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"


@pytest.mark.asyncio
async def test_routes_status_change(client):
    # Create route
    route_res = await client.post("/api/routes", json={
        "name": "NH-9 Solapur Corridor",
        "status": "OPEN",
        "priority": "PRIMARY"
    })
    assert route_res.status_code == 201
    route_id = route_res.json()["id"]

    # Divert route
    divert_res = await client.post(f"/api/routes/{route_id}/divert", json={"reason": "Pedestrian safety"})
    assert divert_res.status_code == 200
    assert divert_res.json()["status"] == "DIVERTED"
