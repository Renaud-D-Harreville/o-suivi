from pydantic import BaseModel


class BeaconResult(BaseModel):
    sequence: int
    beacon_number: int
    tag: str
    is_ph: bool = False
    expected_code: str | None = None
    entered_code: str | None = None
    valid: bool | None = None  # None = not reached
    split_time: int | None = None  # seconds since previous beacon
    cumulated_section_time: int | None = None  # seconds since section start


class SectionResult(BaseModel):
    gate: str  # "PH1", "PH2", etc.
    valid: bool | None = None  # True/False/None (not reached)
    codes_valid: bool | None = None  # True = all codes correct, False = at least one incorrect, None = not reached
    delay: int | None = None  # minutes (negative = too early, positive = too late, None = on time or not reached)
    section_time: int | None = None  # official section time in seconds (PH to PH validation)
    running_time: int | None = None  # running time in seconds (excl. pause)
    pause_time: int | None = None  # pause time at PH in seconds


class CompetitorResult(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    sex: str | None = None
    course_number: int | None = None
    valid_global: bool | None = None  # True=validated, False=not validated, None=not finished/dns
    dns: bool = False
    abandoned: bool = False
    finished: bool = False  # True if race is over (last PH reached, or DNS, or abandoned)
    has_tracker: bool = False  # True if a tracker was assigned to this competitor
    tracker_returned: bool = False  # True if the assigned tracker has been returned
    bag_weight_start: float | None = None
    bag_weight_end: float | None = None
    departure_time: str | None = None
    arrival_time: str | None = None  # timestamp of last PH checkpoint
    total_time: int | None = None  # seconds (arrival - departure)
    total_running_time: int | None = None  # sum of section running times
    sections: list[SectionResult] = []
    beacons: list[BeaconResult] = []


class ResultsResponse(BaseModel):
    routechoices_url: str | None = None
    public_routechoices_time: str | None = None
    event_date: str | None = None
    competitors: list[CompetitorResult] = []

