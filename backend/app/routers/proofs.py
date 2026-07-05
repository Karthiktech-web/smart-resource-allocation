from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import require_auth
from app.database import get_db
from app.services import exif

router = APIRouter(prefix="/api/proofs", tags=["proofs"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/upload")
async def upload_proof(
    task_id: str = Form(...),
    media_url: str = Form(""),
    file: UploadFile = File(...),
    user: dict = Depends(require_auth),
):
    """Upload a proof-of-work photo and validate EXIF GPS/timestamp against the task."""
    db = get_db()
    task_snap = db.collection("tasks").document(task_id).get()
    if not task_snap.exists:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_snap.to_dict() or {}

    image_bytes = await file.read()
    try:
        meta = exif.extract_from_bytes(image_bytes)
    except Exception:
        meta = {"gps": None, "taken_at": None}

    validation = exif.validate(
        meta["gps"],
        meta["taken_at"],
        float(task.get("lat", 0) or 0),
        float(task.get("lng", 0) or 0),
        None,
    )

    now = _now()
    record = {
        "task_id": task_id,
        "uploaded_by": user.get("uid"),
        "media_url": media_url,
        "filename": file.filename,
        "gps": list(meta["gps"]) if meta["gps"] else None,
        "taken_at": meta["taken_at"].isoformat() if meta["taken_at"] else None,
        "validation": validation,
        "flagged": not validation["valid"],
        "created_at": now,
    }
    ref = db.collection("proofs").document()
    ref.set(record)
    return {**record, "id": ref.id}


@router.get("/{task_id}")
async def list_proofs(task_id: str, user: dict = Depends(require_auth)):
    db = get_db()
    proofs = db.collection("proofs").where("task_id", "==", task_id).stream()
    return [{**p.to_dict(), "id": p.id} for p in proofs]
