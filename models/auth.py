import datetime

from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str
    password: str
    email: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    birth_date: datetime.date


class RegisterResponse(BaseModel):
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str