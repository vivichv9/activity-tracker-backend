from datetime import timedelta
from typing import Any

from pydantic import BaseModel

class DashboardResponse(BaseModel):
    username: str
    email: str
    bonuses: int
    last_activities: Any
    achievements: Any
    friends: Any
    active_train: str


class StartActivityRequest(BaseModel):
    activity_type: str


class StartActivityResponse(BaseModel):
    start_time: str


class EndActivityResponse(BaseModel):
    burned: float
    minutes: float