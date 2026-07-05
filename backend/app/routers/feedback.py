from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import require_auth, require_role
from app.database import get_db
from app.services import reliability

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    task_id: str
    ngo_id: str
    rating: float
    comment: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("")
async def submit_feedback(payload: FeedbackCreate, user: dict = Depends(require_auth)):
    """Record feedback for a completed task and update the NGO reliability score."""
    db = get_db()
    now = _now()
    record = {
        "task_id": payload.task_id,
        "ngo_id": payload.ngo_id,
        "rating": payload.rating,
        "comment": payload.comment,
        "author_uid": user.get("uid"),
        "created_at": now,
    }
    db.collection("feedback").document().set(record)

    new_score = None
    ngo_ref = db.collection("ngos").document(payload.ngo_id)
    ngo_snap = ngo_ref.get()
    if ngo_snap.exists:
        ngo = ngo_snap.to_dict() or {}
        new_score = reliability.update_score(
            float(ngo.get("reliability_score", 0.0)),
            payload.rating,
            int(ngo.get("tasks_completed", 0)),
        )
        ngo_ref.set({"reliability_score": new_score, "updated_at": now}, merge=True)
    return {"status": "recorded", "reliability_score": new_score}


@router.post("/verify/{task_id}")
async def verify_task(task_id: str, ngo_id: str, admin: dict = Depends(require_role("admin"))):
    """Mark a task verified, archive its room, and credit the NGO."""
    db = get_db()
    task_ref = db.collection("tasks").document(task_id)
    if not task_ref.get().exists:
        raise HTTPException(status_code=404, detail="Task not found")

    now = _now()
    task_ref.set({"status": "verified", "verified_at": now, "updated_at": now}, merge=True)
    db.collection("task_rooms").document(task_id).set(
        {"status": "archived", "archived_at": now},
        merge=True,
    )

    ngo_ref = db.collection("ngos").document(ngo_id)
    ngo_snap = ngo_ref.get()
    if ngo_snap.exists:
        ngo = ngo_snap.to_dict() or {}
        ngo_ref.set(
            {
                "tasks_completed": int(ngo.get("tasks_completed", 0)) + 1,
                "active_assignments": max(0, int(ngo.get("active_assignments", 0)) - 1),
                "updated_at": now,
            },
            merge=True,
        )
    return {"status": "verified", "task_id": task_id, "room": "archived"}
