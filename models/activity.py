import dataclasses
from datetime import datetime
from typing import List

from pydantic import BaseModel

class Activity:
    type: str
    start_date: datetime
    end_date: datetime
    cals_burned: float
    points_earned: int


class ActivityListResponse(BaseModel):
    activities: List