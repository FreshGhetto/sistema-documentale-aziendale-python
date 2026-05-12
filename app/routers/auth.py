from fastapi import APIRouter, HTTPException, status

from app.database import mongo_manager
from app.schemas import TokenResponse, UserLoginRequest
from app.security import create_access_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest) -> TokenResponse:
    user = mongo_manager.users.find_one({"username": payload.username})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenziali non valide.")
    token = create_access_token(payload.username)
    return TokenResponse(access_token=token)
