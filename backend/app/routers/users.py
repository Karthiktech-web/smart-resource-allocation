from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_auth, require_role
from app.database import get_db
from app.models import UserRegister, UserResponse, UserRole

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register(payload: UserRegister, user: dict = Depends(require_auth)):
    """Create or update the caller's profile. Existing role is preserved."""
    db = get_db()
    ref = db.collection("users").document(user["uid"])
    existing = ref.get()
    role = (
        (existing.to_dict() or {}).get("role", UserRole.volunteer.value)
        if existing.exists
        else UserRole.volunteer.value
    )
    record = {
        **payload.dict(),
        "uid": user["uid"],
        "role": role,
        "created_at": (existing.to_dict() or {}).get("created_at")
        if existing.exists
        else datetime.now(timezone.utc).isoformat(),
    }
    ref.set(record, merge=True)
    return UserResponse(**record)


@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(require_auth)):
    snap = get_db().collection("users").document(user["uid"]).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="User profile not found")
    return UserResponse(**snap.to_dict())


@router.patch("/{uid}/role", response_model=UserResponse)
async def set_role(
    uid: str, role: UserRole, admin: dict = Depends(require_role("admin"))
):
    db = get_db()
    ref = db.collection("users").document(uid)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="User not found")
    ref.set({"role": role.value}, merge=True)
    return UserResponse(**{**snap.to_dict(), "role": role.value})