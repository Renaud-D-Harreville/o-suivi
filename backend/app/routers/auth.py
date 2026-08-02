from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from jose import jwt

from app.config import JWT_ALGORITHM, JWT_EXPIRATION_HOURS, JWT_SECRET
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    repo = UserRepository()
    user = repo.find_by_credentials(body.username, body.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return LoginResponse(token=token, role=user.role)

