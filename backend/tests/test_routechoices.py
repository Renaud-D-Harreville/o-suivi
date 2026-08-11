import pytest

from app.schemas.events import EventDetail
from app.schemas.routechoices import RoutechoicesEventDataRaw
from app.services.routechoices_service import (
    RoutechoicesResolutionError,
    RoutechoicesService,
    RoutechoicesUpstreamError,
)


def _event(routechoices_url: str | None = None, routechoices_event_id: str | None = None) -> EventDetail:
    return EventDetail(
        id="evt_1",
        name="Event",
        routechoices_url=routechoices_url,
        routechoices_event_id=routechoices_event_id,
    )


def test_resolve_event_id_prefers_persisted_value() -> None:
    service = RoutechoicesService()
    event = _event(routechoices_url="https://arvik.routechoices.com/API-test/", routechoices_event_id="KNOWN")
    assert service.resolve_event_id(event) == "KNOWN"


def test_resolve_event_id_from_api_url() -> None:
    service = RoutechoicesService()
    event = _event(routechoices_url="https://api.routechoices.com/events/AAXESzM45fQ/")
    assert service.resolve_event_id(event) == "AAXESzM45fQ"


def test_resolve_event_id_from_html_content() -> None:
    html = '<div data-api-url="https://api.routechoices.com/events/AAXESzM45fQ/"></div>'
    service = RoutechoicesService(fetch_text=lambda _url: html)
    event = _event(routechoices_url="https://arvik.routechoices.com/API-test/")
    assert service.resolve_event_id(event) == "AAXESzM45fQ"


def test_resolve_event_id_raises_without_url() -> None:
    service = RoutechoicesService()
    event = _event()
    with pytest.raises(RoutechoicesResolutionError):
        service.resolve_event_id(event)


def test_resolve_event_id_raises_when_not_found() -> None:
    service = RoutechoicesService(fetch_text=lambda _url: "<html>No event id here</html>")
    event = _event(routechoices_url="https://arvik.routechoices.com/API-test/")
    with pytest.raises(RoutechoicesResolutionError):
        service.resolve_event_id(event)


def test_fetch_event_payload_raises_when_data_url_missing() -> None:
    service = RoutechoicesService(fetch_json=lambda _url: {"event": {"id": "AAXESzM45fQ"}})
    with pytest.raises(RoutechoicesUpstreamError):
        service.fetch_event_payload("AAXESzM45fQ")


def test_fetch_event_payload_returns_typed_payload() -> None:
    calls: list[str] = []

    def fetch_json(url: str):
        calls.append(url)
        if url.endswith("/events/AAXESzM45fQ/"):
            return {"data_url": "https://api.routechoices.com/events/AAXESzM45fQ/data/"}
        return {
            "competitors": [
                {
                    "id": "comp_1",
                    "encoded_data": "abc",
                    "name": "Runner",
                    "short_name": "RUN",
                    "battery_level": 90,
                }
            ],
            "next": None,
        }

    service = RoutechoicesService(fetch_json=fetch_json)
    payload = service.fetch_event_payload("AAXESzM45fQ")

    assert isinstance(payload, RoutechoicesEventDataRaw)
    assert len(calls) == 2
    assert payload.competitors[0].id == "comp_1"
    assert payload.competitors[0].encoded_data == "abc"


def test_fetch_event_payload_prefers_data_url_payload() -> None:
    calls: list[str] = []

    def fetch_json(url: str):
        calls.append(url)
        if url.endswith("/events/AAXESzM45fQ/"):
            return {"data_url": "https://api.routechoices.com/events/AAXESzM45fQ/data/"}
        return {"competitors": [{"id": "x", "encoded_data": "abc"}], "next": None}

    service = RoutechoicesService(fetch_json=fetch_json)
    payload = service.fetch_event_payload("AAXESzM45fQ")

    assert len(calls) == 2
    assert calls[0].endswith("/events/AAXESzM45fQ/")
    assert calls[1].endswith("/events/AAXESzM45fQ/data/")
    assert payload.competitors[0].id == "x"


