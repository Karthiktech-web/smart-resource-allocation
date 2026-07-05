from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import require_auth
from app.database import get_db

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


class MessageCreate(BaseModel):
    text: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _room_ref(db, task_id: str):
    return db.collection("task_rooms").document(task_id)


def firestore_array_union(value):
    """Wrapper so tests can monkeypatch; uses firestore.ArrayUnion at runtime."""
    from google.cloud import firestore

    return firestore.ArrayUnion([value])


@router.get("/{task_id}")
async def get_room(task_id: str, user: dict = Depends(require_auth)):
    snap = _room_ref(get_db(), task_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Room not found")
    return {**snap.to_dict(), "task_id": task_id}


@router.get("/{task_id}/messages")
async def list_messages(task_id: str, user: dict = Depends(require_auth)):
    db = get_db()
    msgs = _room_ref(db, task_id).collection("messages").order_by("created_at").stream()
    return [{**m.to_dict(), "id": m.id} for m in msgs]


@router.post("/{task_id}/messages")
async def post_message(task_id: str, payload: MessageCreate, user: dict = Depends(require_auth)):
    db = get_db()
    room = _room_ref(db, task_id)
    snap = room.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Room not found")
    if (snap.to_dict() or {}).get("status") == "archived":
        raise HTTPException(status_code=403, detail="Room is archived")

    now = _now()
    record = {
        "text": payload.text,
        "sender_uid": user.get("uid"),
        "sender_name": user.get("name") or user.get("email") or "User",
        "created_at": now,
    }
    ref = room.collection("messages").document()
    ref.set(record)
    room.set(
        {"participants": firestore_array_union(user.get("uid")), "last_message_at": now},
        merge=True,
    )
    return {**record, "id": ref.id}
