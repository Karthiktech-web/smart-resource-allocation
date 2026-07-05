from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.auth import require_auth, require_role
from app.database import get_db
from app.services import event_report, events

router = APIRouter(prefix="/api/events", tags=["events"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(db, event_id: str) -> dict:
    snap = db.collection("events").document(event_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Event not found")
    return {**snap.to_dict(), "id": event_id}


@router.get("")
async def list_events(user: dict = Depends(require_auth)):
    db = get_db()
    return {"events": [{**e.to_dict(), "id": e.id} for e in db.collection("events").stream()]}


@router.post("")
async def create_event(payload: dict, admin: dict = Depends(require_role("admin"))):
    """Create an event (venue center + radius + time window)."""
    required = {"name", "venue_lat", "venue_lng"}
    if not required.issubset(payload):
        raise HTTPException(status_code=400, detail=f"missing fields: {required - set(payload)}")
    db = get_db()
    ref = db.collection("events").document()
    doc = {**payload, "active": bool(payload.get("active", True)), "created_at": _now()}
    ref.set(doc)
    return {"id": ref.id, **doc}


@router.post("/{event_id}/toggle")
async def toggle_event(event_id: str, admin: dict = Depends(require_role("admin"))):
    """Flip Event Mode on/off (venue-centric focus)."""
    db = get_db()
    event = _load(db, event_id)
    new_active = not bool(event.get("active", False))
    db.collection("events").document(event_id).set({"active": new_active}, merge=True)
    return {"id": event_id, "active": new_active}


@router.get("/{event_id}/live")
async def event_live(event_id: str, user: dict = Depends(require_auth)):
    """Live-tracker aggregation for tasks/proofs inside the venue perimeter + window."""
    db = get_db()
    event = _load(db, event_id)
    tasks = [t.to_dict() for t in db.collection("tasks").stream()]
    proofs = [p.to_dict() for p in db.collection("proofs").stream()]
    return events.aggregate_event(event, tasks, proofs)


@router.get("/{event_id}/report")
async def event_report_pdf(event_id: str, admin: dict = Depends(require_role("admin"))):
    """Generate + return the post-event PDF summary."""
    db = get_db()
    event = _load(db, event_id)
    tasks = [t.to_dict() for t in db.collection("tasks").stream()]
    proofs = [p.to_dict() for p in db.collection("proofs").stream()]
    stories = [s.to_dict() for s in db.collection("impact_stories").stream()]

    data = event_report.build_report_data(event, tasks, proofs, stories)
    pdf = event_report.render_pdf(data)
    filename = f"event_{event_id}_report.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )