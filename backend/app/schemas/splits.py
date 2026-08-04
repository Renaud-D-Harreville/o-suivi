from pydantic import BaseModel

from app.schemas.events import EventBeacon


class CompetitorSummary(BaseModel):
    """Lightweight competitor info for split times display."""

    user_id: str
    first_name: str
    last_name: str
    sex: str | None = None
    course_number: int | None = None


class SplitEntry(BaseModel):
    """One competitor's split time for a beacon pair."""

    user_id: str
    split_seconds: int


class BeaconPairSplits(BaseModel):
    """Split times for one pair of consecutive beacons."""

    from_beacon_id: int | None = None  # None = Départ
    to_beacon_id: int
    splits: list[SplitEntry] = []


class SplitsResponse(BaseModel):
    """Full response for the split times endpoint."""

    event_name: str
    beacons: list[EventBeacon] = []
    competitors: list[CompetitorSummary] = []
    pairs: list[BeaconPairSplits] = []

