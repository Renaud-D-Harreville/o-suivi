from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from app.config import JWT_ALGORITHM, JWT_EXPIRATION_HOURS, JWT_SECRET
from app.main import app

client = TestClient(app)


def _get_token() -> str:
    response = client.post(
        "/api/auth/login",
        json={"username": "renaud", "password": "arvik"},
    )
    return response.json()["token"]


def _make_competitor_token() -> str:
    """Create a valid JWT with role=competitor (simulates a logged-in trainee)."""
    return jwt.encode(
        {
            "user_id": "competitor_001",
            "role": "competitor",
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )




def test_list_templates_empty() -> None:
    token = _get_token()
    response = client.get("/api/templates", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_template() -> None:
    token = _get_token()
    response = client.post(
        "/api/templates",
        json={"name": "Chartreuse 2026"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chartreuse 2026"
    assert "id" in data


def test_create_template_then_list() -> None:
    token = _get_token()
    client.post(
        "/api/templates",
        json={"name": "Template A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/templates",
        json={"name": "Template B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get("/api/templates", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    names = [t["name"] for t in response.json()]
    assert "Template A" in names
    assert "Template B" in names


def test_create_template_empty_name() -> None:
    token = _get_token()
    response = client.post(
        "/api/templates",
        json={"name": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_list_templates_requires_auth() -> None:
    response = client.get("/api/templates")
    assert response.status_code == 401


def test_create_template_requires_auth() -> None:
    response = client.post("/api/templates", json={"name": "Test"})
    assert response.status_code == 401


def _create_template(token: str, name: str = "Test Template") -> str:
    """Helper: create a template and return its id."""
    response = client.post(
        "/api/templates",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


def test_get_template_detail() -> None:
    token = _get_token()
    tid = _create_template(token, "Chartreuse")
    response = client.get(
        f"/api/templates/{tid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tid
    assert data["name"] == "Chartreuse"


def test_get_template_not_found() -> None:
    token = _get_token()
    response = client.get(
        "/api/templates/nonexistent",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_update_template_name() -> None:
    token = _get_token()
    tid = _create_template(token)
    response = client.patch(
        f"/api/templates/{tid}",
        json={"name": "Nouveau nom"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nouveau nom"


def test_get_beacons_empty() -> None:
    token = _get_token()
    tid = _create_template(token)
    response = client.get(
        f"/api/templates/{tid}/beacons",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_put_beacons() -> None:
    token = _get_token()
    tid = _create_template(token)
    beacons = [
        {"id": 31, "number": 1, "tag": "unique", "is_ph": False},
        {"id": 32, "number": 2, "tag": "NO", "is_ph": False},
        {"id": 33, "number": 2, "tag": "SE", "is_ph": False},
        {"id": 34, "number": 3, "tag": "unique", "is_ph": True},
    ]
    response = client.put(
        f"/api/templates/{tid}/beacons",
        json=beacons,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[3]["is_ph"] is True
    assert data[0]["id"] == 31


def test_put_beacons_persists() -> None:
    token = _get_token()
    tid = _create_template(token)
    beacons = [{"id": 31, "number": 1, "tag": "unique", "is_ph": False}]
    client.put(
        f"/api/templates/{tid}/beacons",
        json=beacons,
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        f"/api/templates/{tid}/beacons",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 31


def test_get_courses_empty() -> None:
    token = _get_token()
    tid = _create_template(token)
    response = client.get(
        f"/api/templates/{tid}/courses",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_put_courses() -> None:
    token = _get_token()
    tid = _create_template(token)
    # First set beacons so courses can reference them
    beacons = [
        {"id": 31, "number": 1, "tag": "unique", "is_ph": False},
        {"id": 32, "number": 2, "tag": "NO", "is_ph": False},
    ]
    client.put(
        f"/api/templates/{tid}/beacons",
        json=beacons,
        headers={"Authorization": f"Bearer {token}"},
    )
    courses = [{"number": 1, "beacons": [31, 32]}]
    response = client.put(
        f"/api/templates/{tid}/courses",
        json=courses,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["number"] == 1
    # Courses are enriched in response
    assert data[0]["beacons"][0]["id"] == 31
    assert data[0]["beacons"][0]["tag"] == "unique"
    assert data[0]["beacons"][1]["id"] == 32
    assert data[0]["beacons"][1]["tag"] == "NO"


def test_get_time_gates_empty() -> None:
    token = _get_token()
    tid = _create_template(token)
    response = client.get(
        f"/api/templates/{tid}/time-gates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_put_time_gates() -> None:
    token = _get_token()
    tid = _create_template(token)
    time_gates = [
        {
            "course_number": 1,
            "gates": [
                {"gate": "PH1", "min_m": 45, "max_m": 75, "min_f": 45, "max_f": 85},
                {"gate": "PH2", "min_m": 30, "max_m": 60, "min_f": 30, "max_f": 70},
            ],
        }
    ]
    response = client.put(
        f"/api/templates/{tid}/time-gates",
        json=time_gates,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["gates"][0]["min_m"] == 45


def test_update_template_not_found() -> None:
    token = _get_token()
    response = client.patch(
        "/api/templates/nonexistent",
        json={"name": "Nope"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_get_template_requires_auth() -> None:
    response = client.get("/api/templates/some-id")
    assert response.status_code == 401


def test_update_template_requires_auth() -> None:
    response = client.patch("/api/templates/some-id", json={"name": "X"})
    assert response.status_code == 401


def test_put_beacons_requires_auth() -> None:
    response = client.put("/api/templates/some-id/beacons", json=[])
    assert response.status_code == 401


def test_put_courses_requires_auth() -> None:
    response = client.put("/api/templates/some-id/courses", json=[])
    assert response.status_code == 401


def test_put_time_gates_requires_auth() -> None:
    response = client.put("/api/templates/some-id/time-gates", json=[])
    assert response.status_code == 401


def test_competitor_token_rejected() -> None:
    token = _make_competitor_token()
    response = client.get(
        "/api/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Organizer role required"
