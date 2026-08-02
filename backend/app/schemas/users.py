from typing import Literal

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    username: str | None = None
    password: str | None = None
    routechoices_id: str | None = None
    role: Literal["organizer", "competitor"]
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    sex: Literal["H", "F"] | None = None
