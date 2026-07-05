from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_auth, require_role
from app.database import get_db
from app.services import anomaly, heatmap, storyteller, synergy

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/anomaly-scan")
async def anomaly_scan(admin: dict = Depends(require_role("admin"))):
    """Scan proof submissions and flag statistically/physically implausible entries."""
    db = get_db()
    submissions = [{**proof.to_dict(), "id": proof.id} for proof in db.collection("proofs").stream()]
    results = anomaly.scan_batch(submissions)
    flagged = [result for result in results if result.get("flagged")]
    now = _now()

    for result in flagged:
        db.collection("proofs").document(result["id"]).set(
            {"anomaly_flagged": True, "anomaly_reasons": result["reasons"], "scanned_at": now},
            merge=True,
        )

    return {"scanned": len(results), "flagged": len(flagged), "items": flagged}


@router.get("/heatmap/forecast")
async def heatmap_forecast(month: int, category: str = "water", user: dict = Depends(require_auth)):
    """Forecast predicted high-need zones for a target month from historical needs."""
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="month must be 1..12")

    db = get_db()
    needs = [need.to_dict() for need in db.collection("needs").stream()]
    return {"month": month, "category": category, "zones": heatmap.forecast(needs, month, category)}


@router.post("/synergy-scan")
async def synergy_scan(admin: dict = Depends(require_role("admin"))):
    """Suggest transport sharing between NGOs with nearby, time-aligned trips."""
    db = get_db()
    trips = [{**trip.to_dict(), "id": trip.id} for trip in db.collection("trips").stream()]
    return {"suggestions": synergy.find_synergies(trips)}


@router.post("/story/{task_id}")
async def generate_story(task_id: str, admin: dict = Depends(require_role("admin"))):
    """Generate a donor-ready impact story for a completed task."""
    db = get_db()
    task_snap = db.collection("tasks").document(task_id).get()
    if not task_snap.exists:
        raise HTTPException(status_code=404, detail="Task not found")

    task = {**task_snap.to_dict(), "id": task_id}
    proofs = [proof.to_dict() for proof in db.collection("proofs").where("task_id", "==", task_id).stream()]
    feedback = [item.to_dict() for item in db.collection("feedback").where("task_id", "==", task_id).stream()]

    story = storyteller.generate_story(task, proofs, feedback)
    now = _now()
    ref = db.collection("impact_stories").document()
    ref.set({"task_id": task_id, **story, "created_at": now})
    return {"id": ref.id, **story}
