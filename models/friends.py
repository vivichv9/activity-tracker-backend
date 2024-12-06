from typing import List, Any

from pydantic import BaseModel


class FriendListResponse(BaseModel):
    friends: Any


class FriendRequest(BaseModel):
    username: str


class FriendResponse(BaseModel):
    username: str


class FriendOrdersRepsonse(BaseModel):
    orders: List