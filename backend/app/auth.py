from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import logging
from app.database import get_db

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict | None:
    if credentials is None:
        return None
    token = credentials.credentials
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.warning(f"Invalid Firebase token: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = credentials.credentials
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.warning(f"Auth required but token invalid: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    

def get_user_role(uid: str) -> str:
    """Load a user's role from the `users` collection, defaulting to volunteer."""
    snap = get_db().collection("users").document(uid).get()
    if not snap.exists:
        return "volunteer"
    return (snap.to_dict() or {}).get("role", "volunteer")


def require_role(*allowed: str):
    """Dependency factory enforcing the caller has one of the allowed roles."""

    async def _dep(user: dict = Depends(require_auth)) -> dict:
        role = get_user_role(user["uid"])
        if allowed and role not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return {**user, "role": role}

    return _dep
    