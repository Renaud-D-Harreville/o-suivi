from typing import Literal

from pydantic import BaseModel, Field


class RegistrationCreate(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    sex: Literal["H", "F"]
    phone: str = ""
    routechoices_id: str | None = None
    routechoices_short_name: str | None = None


class RegistrationDetail(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    sex: str
    phone: str
    routechoices_id: str | None = None
    routechoices_short_name: str | None = None
    course_number: int | None = None
    start_order: int | None = None
    start_time_planned: str | None = None
    tracker_number: str | None = None


class RegistrationUpdate(BaseModel):
    course_number: int | None = None
    start_time_planned: str | None = None
    tracker_number: str | None = None
