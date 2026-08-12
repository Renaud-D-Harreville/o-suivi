from pydantic import BaseModel, ConfigDict


class RoutechoicesEventMetaRaw(BaseModel):
    """Raw metadata returned by /events/{id}/ endpoint."""

    model_config = ConfigDict(extra="ignore")

    data_url: str | None = None


class RoutechoicesCompetitorRaw(BaseModel):
    """Raw competitor payload returned by Routechoices data endpoint."""

    model_config = ConfigDict(extra="ignore")

    id: str
    encoded_data: str
    name: str | None = None
    short_name: str | None = None
    start_time: str | None = None
    battery_level: int | None = None


class RoutechoicesEventDataRaw(BaseModel):
    """Raw event data returned by Routechoices data endpoint."""

    model_config = ConfigDict(extra="ignore")

    competitors: list[RoutechoicesCompetitorRaw]
    next: str | None = None


class RoutechoicesGpsRawResponse(BaseModel):
    routechoices_event_id: str
    payload: RoutechoicesEventDataRaw


class GpsStatusEntry(BaseModel):
    last_timestamp: str | None = None


class GpsStatusResponse(BaseModel):
    statuses: dict[str, GpsStatusEntry] = {}


