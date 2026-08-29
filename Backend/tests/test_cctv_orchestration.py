"""
Integration Test Suite for CCTV Search Orchestration, Spatial-Temporal Camera Prioritization,
Candidate Persistence, and Human Verification Audit Logging.
"""

import pytest
from app.models.camera import Camera, CameraStatus
from app.models.face_match import FaceMatchResult, FaceMatchStatus, MatchType
from app.models.lost_person import LostPersonCase, LostPersonStatus
from app.models.audit import AuditLog
from app.services.cctv_search_service import cctv_search_service
from sqlalchemy import select


async def get_admin_headers(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_cctv_search_and_human_verification(client, test_db):
    headers = await get_admin_headers(client)

    # 1. Create a lost person case via API
    case_payload = {
        "name": "Godavari Jadhav",
        "age": 8,
        "gender": "F",
        "clothing_description": "Yellow frock with red ribbons",
        "last_seen_location": "Pundalik Temple Steps (Pandharpur)",
        "priority": "CRITICAL"
    }
    case_res = await client.post("/api/lost-persons", json=case_payload, headers=headers)
    assert case_res.status_code == 201
    case_data = case_res.json()
    case_id = case_data["id"]

    # 2. Trigger spatial-temporal CCTV scan
    scan_res = await client.post(f"/api/lost-persons/{case_id}/cctv-scan", headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["success"] is True
    assert scan_data["candidate_matches_count"] >= 1

    candidates = scan_data["candidates"]
    first_candidate = candidates[0]
    match_id = first_candidate["match_id"]
    assert first_candidate["status"] == "CANDIDATE"
    assert first_candidate["similarity_score"] >= 0.70
    assert first_candidate["similarity_score"] <= 1.00

    # 3. Perform Human Verification (Operator verifies match)
    verify_res = await client.post(
        f"/api/lost-persons/{case_id}/matches/{match_id}/verify",
        json={"verified": True, "notes": "Positive match confirmed by mother"},
        headers=headers
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["success"] is True
    assert verify_data["status"] == "VERIFIED"

    # 4. Verify candidate match record updated in DB
    stmt = select(FaceMatchResult).where(FaceMatchResult.id == match_id)
    res = await test_db.execute(stmt)
    match_rec = res.scalar_one_or_none()
    assert match_rec is not None
    assert match_rec.status == FaceMatchStatus.VERIFIED

    # 5. Verify audit log was recorded
    audit_stmt = select(AuditLog).where(AuditLog.entity_id == match_id)
    audit_res = await test_db.execute(audit_stmt)
    audit_rec = audit_res.scalar_one_or_none()
    assert audit_rec is not None
    assert audit_rec.action == "CCTV_CANDIDATE_VERIFIED"
