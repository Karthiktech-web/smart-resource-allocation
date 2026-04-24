from fastapi import Request, HTTPException
from firebase_admin import auth as firebase_auth
import firebase_admin
from app.config import get_settings

settings = get_settings()

async def verify_firebase_token(request: Request):
    # 1. Skip security for the documentation and health checks
    # Otherwise, you won't be able to see your own API docs!
    allowed_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    if request.url.path in allowed_paths:
        return None

    # 2. Check for the Authorization Header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Please log in to perform this action."
        )

    # 3. Extract and Verify the Token
    token = auth_header.split("Bearer ")[1]
    try:
        # This checks the token against Google's servers
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except firebase_admin.auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid security token.")