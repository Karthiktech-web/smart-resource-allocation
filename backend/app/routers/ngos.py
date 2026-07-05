from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_role
from app.database import get_db
from app.models import NGO, NGOCreate

router = APIRouter(prefix="/api/ngos", tags=["ngos"])


@router.get("", response_model=list[NGO])
async def list_ngos():
    """Public directory of registered NGOs."""
    db = get_db()
    return [NGO(**{**doc.to_dict(), "id": doc.id}) for doc in db.collection("ngos").stream()]


@router.get("/{ngo_id}", response_model=NGO)
async def get_ngo(ngo_id: str):
    snap = get_db().collection("ngos").document(ngo_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="NGO not found")
    return NGO(**{**snap.to_dict(), "id": snap.id})


@router.post("", response_model=NGO)
async def create_ngo(payload: NGOCreate, admin: dict = Depends(require_role("admin"))):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    record = {**payload.dict(), "created_at": now, "updated_at": now}
    ref = db.collection("ngos").document()
    ref.set(record)
    return NGO(**{**record, "id": ref.id})


@router.patch("/{ngo_id}", response_model=NGO)
async def update_ngo(
    ngo_id: str, payload: NGOCreate, admin: dict = Depends(require_role("admin"))
):
    db = get_db()
    ref = db.collection("ngos").document(ngo_id)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="NGO not found")
    updates = {**payload.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}
    ref.set(updates, merge=True)
    return NGO(**{**snap.to_dict(), **updates, "id": ngo_id})