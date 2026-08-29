import pytest


async def get_admin_headers(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_helpline_scenarios(client):
    headers = await get_admin_headers(client)
    res = await client.get("/api/helpline/scenarios", headers=headers)
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 3
    assert any(s["language"] == "mr" for s in scenarios)


@pytest.mark.asyncio
async def test_helpline_call_simulation(client):
    headers = await get_admin_headers(client)
    payload = {"scenario_id": "marathi_senior_wakhri"}
    res = await client.post("/api/helpline/call/simulate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "मारुती शिंदे" in data["native_transcript"]
    assert "Maruti Shinde" in data["english_translation"]
    assert len(data["waveform"]) == 32
    assert "extracted_attributes" in data
    assert data["extracted_attributes"]["age"] == 68


@pytest.mark.asyncio
async def test_create_case_from_call_and_cctv_scan(client):
    headers = await get_admin_headers(client)

    # 1. Create case from call
    payload = {
        "caller_name": "Sunita Jadhav",
        "caller_phone": "+91 94220 88912",
        "native_transcript": "माझी लहान मुलगी गोदावरी जाधव हरवली आहे.",
        "english_translation": "My young daughter Godavari Jadhav is lost.",
        "name": "Godavari Jadhav",
        "age": 8,
        "gender": "F",
        "clothing_description": "Yellow frock with floral print and red ribbons",
        "last_seen_location": "Pundalik Temple Steps",
        "urgency": "CRITICAL",
        "trigger_cctv_scan": True
    }
    res = await client.post("/api/helpline/call/create-case-and-match", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    case = data["case"]
    assert case["name"] == "Godavari Jadhav"

    # 2. Test explicit CCTV scan endpoint on the created case
    case_id = case["id"]
    scan_res = await client.post(f"/api/lost-persons/{case_id}/cctv-scan", headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["success"] is True
    assert scan_data["case_id"] == case_id
