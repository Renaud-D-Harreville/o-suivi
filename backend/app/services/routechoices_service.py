import json
import re
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import ValidationError

from app.schemas.events import EventDetail
from app.schemas.routechoices import RoutechoicesEventDataRaw, RoutechoicesEventMetaRaw


class RoutechoicesResolutionError(Exception):
    """Raised when Routechoices event id cannot be resolved from event data."""


class RoutechoicesUpstreamError(Exception):
    """Raised when a Routechoices upstream request fails."""


class RoutechoicesService:
    _API_EVENT_URL_TEMPLATE = "https://api.routechoices.com/events/{event_id}/"
    _API_EVENT_ID_RE = re.compile(r"routechoices\.com/events/([A-Za-z0-9_-]+)")
    _HTML_EVENT_ID_RE = re.compile(r"event_id\s*[:=]\s*[\"']([A-Za-z0-9_-]+)[\"']")
    _HTML_API_URL_RE = re.compile(r"api\.routechoices\.com/events/([A-Za-z0-9_-]+)/")

    def __init__(
        self,
        fetch_text: Callable[[str], str] | None = None,
        fetch_json: Callable[[str], object] | None = None,
    ) -> None:
        self._fetch_text = fetch_text or self._default_fetch_text
        self._fetch_json = fetch_json or self._default_fetch_json

    def resolve_event_id(self, event: EventDetail) -> str:
        if event.routechoices_event_id:
            return event.routechoices_event_id

        if not event.routechoices_url:
            raise RoutechoicesResolutionError("routechoices_url is not configured for this event")

        event_id = self._extract_event_id_from_url(event.routechoices_url)
        if event_id:
            return event_id

        html = self._fetch_text(event.routechoices_url)
        event_id = self._extract_event_id_from_html(html)
        if event_id:
            return event_id

        raise RoutechoicesResolutionError("Unable to resolve Routechoices event id from routechoices_url")

    def fetch_event_payload(self, routechoices_event_id: str) -> RoutechoicesEventDataRaw:
        url = self._API_EVENT_URL_TEMPLATE.format(event_id=routechoices_event_id)
        event_meta = self._parse_event_meta(self._fetch_json(url))
        if not event_meta.data_url:
            raise RoutechoicesUpstreamError("Routechoices event metadata has no data_url")
        return self._parse_event_data(self._fetch_json(event_meta.data_url))

    def _parse_event_meta(self, payload: object) -> RoutechoicesEventMetaRaw:
        try:
            return RoutechoicesEventMetaRaw.model_validate(payload)
        except ValidationError as exc:
            raise RoutechoicesUpstreamError("Unexpected Routechoices metadata response format") from exc

    def _parse_event_data(self, payload: object) -> RoutechoicesEventDataRaw:
        try:
            return RoutechoicesEventDataRaw.model_validate(payload)
        except ValidationError as exc:
            raise RoutechoicesUpstreamError("Unexpected Routechoices data response format") from exc

    def _extract_event_id_from_url(self, url: str) -> str | None:
        match = self._API_EVENT_ID_RE.search(url)
        return match.group(1) if match else None

    def _extract_event_id_from_html(self, html: str) -> str | None:
        for regex in (self._HTML_EVENT_ID_RE, self._HTML_API_URL_RE):
            match = regex.search(html)
            if match:
                return match.group(1)
        return None

    def _default_fetch_text(self, url: str) -> str:
        try:
            request = Request(url, headers={"User-Agent": "o-suivi/0.1"})
            with urlopen(request, timeout=15) as response:  # noqa: S310
                return response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RoutechoicesUpstreamError(f"Failed to fetch Routechoices page: {exc}") from exc

    def _default_fetch_json(self, url: str) -> object:
        try:
            request = Request(url, headers={"Accept": "application/json", "User-Agent": "o-suivi/0.1"})
            with urlopen(request, timeout=15) as response:  # noqa: S310
                body = response.read().decode("utf-8", errors="strict")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RoutechoicesUpstreamError(f"Failed to fetch Routechoices API: {exc}") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RoutechoicesUpstreamError("Invalid JSON returned by Routechoices API") from exc


