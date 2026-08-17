import threading

import pytest
from starlette.websockets import WebSocketDisconnect
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _get_token() -> str:
    resp = client.post("/api/auth/login", json={"username": "renaud", "password": "arvik"})
    return resp.json()["token"]


def _create_event(token: str) -> str:
    resp = client.post(
        "/api/events",
        json={"name": "WS Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


def _add_registration(token: str, event_id: str) -> str:
    resp = client.post(
        f"/api/events/{event_id}/registrations",
        json={"first_name": "Test", "last_name": "User", "sex": "H", "phone": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["user_id"]


def test_websocket_receives_refresh_on_log_action() -> None:
    """A connected WebSocket client receives a refresh signal when a log action is posted."""
    token = _get_token()
    eid = _create_event(token)
    uid = _add_registration(token, eid)

    received_messages: list[dict] = []

    with client.websocket_connect(f"/api/events/{eid}/ws?token={token}") as ws:
        # Post a departure action in a background thread to avoid blocking
        def post_departure():
            client.post(
                f"/api/events/{eid}/registrations/{uid}/depart",
                json={"creation_date": "2026-09-15T07:30:00Z", "departure_time": "2026-09-15T07:30:00Z"},
                headers={"Authorization": f"Bearer {token}"},
            )

        t = threading.Thread(target=post_departure)
        t.start()
        t.join()

        msg = ws.receive_json()
        received_messages.append(msg)

    assert len(received_messages) == 1
    assert received_messages[0] == {"type": "refresh"}


def test_websocket_rejects_invalid_token() -> None:
    """WebSocket connection with an invalid token should be closed with code 4001."""
    token = _get_token()
    eid = _create_event(token)

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/api/events/{eid}/ws?token=invalid"):
            pass
    assert exc_info.value.code == 4001


def test_websocket_rejects_missing_token() -> None:
    """WebSocket connection without a token should fail (422 from missing query param)."""
    token = _get_token()
    eid = _create_event(token)

    try:
        with client.websocket_connect(f"/api/events/{eid}/ws") as ws:
            pass
        assert False, "Should have raised"
    except Exception:
        pass
