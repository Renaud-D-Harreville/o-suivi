from fastapi.testclient import TestClient
from jose import jwt

from app.config import JWT_ALGORITHM, JWT_SECRET
from app.main import app

client = TestClient(app)


def test_login_success() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "arvik"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["role"] == "organizer"


def test_login_jwt_contains_role() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "arvik"},
    )
    token = response.json()["token"]
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["role"] == "organizer"
    assert "user_id" in payload


def test_login_wrong_password() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_unknown_user() -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "nobody", "password": "arvik"},
    )

    assert response.status_code == 401

