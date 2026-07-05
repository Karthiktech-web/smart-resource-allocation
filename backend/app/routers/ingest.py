from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import require_role
from app.database import get_db
from app.services import ingestion

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/upload")
async def upload_preview(
    file: UploadFile = File(...), admin: dict = Depends(require_role("admin"))
):
    """Parse an uploaded Excel/CSV/PDF into a preview of need records (not saved)."""
    content = await file.read()
    try:
        needs = ingestion.parse_file(file.filename or "", content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {e}")
    return {"count": len(needs), "needs": needs}


@router.post("/commit")
async def commit_needs(needs: list[dict], admin: dict = Depends(require_role("admin"))):
    """Persist reviewed needs and create an open task for each."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    created = []
    for need in needs:
        need_ref = db.collection("needs").document()
        need_record = {**need, "status": "open", "created_at": now, "updated_at": now}
        need_ref.set(need_record)

        task_ref = db.collection("tasks").document()
        task_record = {
            "need_id": need_ref.id,
            "title": need.get("title", "Untitled"),
            "category": need.get("category", "general"),
            "quantity": float(need.get("quantity", 0) or 0),
            "unit": need.get("unit", ""),
            "area_id": need.get("area_id"),
            "lat": float(need.get("lat", 0) or 0),
            "lng": float(need.get("lng", 0) or 0),
            "status": "open",
            "parent_task_id": None,
            "created_at": now,
            "updated_at": now,
        }
        task_ref.set(task_record)
        created.append({"need_id": need_ref.id, "task_id": task_ref.id})
    return {"created": created, "count": len(created)}
