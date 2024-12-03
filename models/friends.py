from typing import List

from pydantic import BaseModel


class FriendListResponse(BaseModel):
    friends: List[str]


class FriendRequest(BaseModel):
    username: str


class FriendResponse(BaseModel):
    username: str
