import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException
from starlette import status


def create_access_token(data: dict, expires_delta: timedelta, secret_key: str, algorithm) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta, secret_key, algorithm) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorith) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorith])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
