from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Decoded JWT payload — returned by auth dependencies."""

    user_id: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str

