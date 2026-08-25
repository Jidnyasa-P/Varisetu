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
