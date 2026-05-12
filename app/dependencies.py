from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import mongo_manager
from app.security import decode_access_token


bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:  # pragma: no cover - depends on runtime token input
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto.",
        ) from exc

    username = payload.get("sub")
    user = mongo_manager.users.find_one({"username": username}, {"password_hash": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato.",
        )
    user["id"] = str(user.pop("_id"))
    return user
