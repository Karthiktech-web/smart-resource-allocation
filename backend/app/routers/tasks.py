import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_auth, require_role
from app.database import get_db
from app.services import matching, requeue, task_splitter

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

SLA_MINUTES = int(os.getenv("TASK_SLA_MINUTES", "120"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_ngos(db) -> list[dict]:
    return [{**d.to_dict(), "id": d.id} for d in db.collection("ngos").stream()]


def _load_task(db, task_id: str) -> dict:
    snap = db.collection("tasks").document(task_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Task not found")
    return {**snap.to_dict(), "id": snap.id}


@router.get("")
async def list_tasks(status: str | None = None):
    db = get_db()
    query = db.collection("tasks")
    if status:
        query = query.where("status", "==", status)
    return [{**d.to_dict(), "id": d.id} for d in query.stream()]


@router.post("/{task_id}/match")
async def match_task(task_id: str, admin: dict = Depends(require_role("admin"))):
    db = get_db()
    task = _load_task(db, task_id)
    ranked = matching.rank(_load_ngos(db), task)
    return {"task_id": task_id, "candidates": ranked}


@router.post("/{task_id}/broadcast")
async def broadcast_task(task_id: str, top_n: int = 3, admin: dict = Depends(require_role("admin"))):
    """Match, and if the quantity exceeds one NGO, split into subtasks and broadcast."""
    db = get_db()
    task = _load_task(db, task_id)
    ranked = matching.rank(_load_ngos(db), task)[:top_n]
    subtasks = task_splitter.build_subtasks(task, ranked)

    now = _now()
    created_ids = []
    if len(subtasks) > 1:
        for st in subtasks:
            ref = db.collection("tasks").document()
            ref.set({**st, "created_at": now, "updated_at": now})
            created_ids.append(ref.id)
        db.collection("tasks").document(task_id).set(
            {"status": "broadcast", "updated_at": now}, merge=True
        )
    else:
        db.collection("tasks").document(task_id).set(
            {"status": "broadcast", "updated_at": now}, merge=True
        )
    return {
        "task_id": task_id,
        "split": len(subtasks) > 1,
        "subtask_ids": created_ids,
        "candidates": ranked,
    }


@router.post("/{task_id}/accept")
async def accept_task(task_id: str, ngo_id: str, user: dict = Depends(require_auth)):
    db = get_db()
    task = _load_task(db, task_id)
    now = _now()
    assignment = {
        "task_id": task_id,
        "ngo_id": ngo_id,
        "status": "accepted",
        "accepted_at": now,
        "acted_at": None,
        "created_by": user.get("uid"),
    }
    ref = db.collection("assignments").document()
    ref.set(assignment)
    db.collection("tasks").document(task_id).set(
        {"status": "accepted", "updated_at": now}, merge=True
    )
    db.collection("task_rooms").document(task_id).set(
        {"task_id": task_id, "participants": [user.get("uid")], "status": "active", "created_at": now},
        merge=True,
    )
    return {"assignment_id": ref.id, "status": "accepted"}


@router.post("/{task_id}/act")
async def act_task(task_id: str, user: dict = Depends(require_auth)):
    db = get_db()
    now = _now()
    for a in db.collection("assignments").where("task_id", "==", task_id).stream():
        db.collection("assignments").document(a.id).set({"acted_at": now}, merge=True)
    db.collection("tasks").document(task_id).set(
        {"status": "acted", "updated_at": now}, merge=True
    )
    return {"task_id": task_id, "status": "acted"}


@router.post("/requeue-scan")
async def requeue_scan(admin: dict = Depends(require_role("admin"))):
    """Find accepted-but-idle assignments past SLA and reopen their tasks."""
    db = get_db()
    assignments = [{**a.to_dict(), "id": a.id} for a in db.collection("assignments").stream()]
    stagnant = requeue.find_stagnant(assignments, SLA_MINUTES)
    now = _now()
    requeued = []
    for a in stagnant:
        db.collection("assignments").document(a["id"]).set(
            {"status": "revoked", "revoked_at": now}, merge=True
        )
        db.collection("tasks").document(a["task_id"]).set(
            {"status": "requeued", "updated_at": now}, merge=True
        )
        requeued.append(a["task_id"])
    return {"requeued_task_ids": requeued, "count": len(requeued)}
