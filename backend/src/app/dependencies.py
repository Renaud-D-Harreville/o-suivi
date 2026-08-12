from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import JWT_ALGORITHM, JWT_SECRET
from app.schemas.auth import TokenPayload

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> TokenPayload:
    """Decode JWT and return typed payload. Raises 401 if invalid or expired."""
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return TokenPayload(user_id=payload["user_id"], role=payload["role"])


async def require_organizer(
    user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """Require the authenticated user to have the organizer role."""
    if user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer role required",
        )
    return user


