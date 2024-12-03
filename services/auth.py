from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from config import SECRET_KEY, JWT_ALGORITHM
from models.auth import RegisterResponse, RegisterRequest
from utils.jwt_utils import decode_token
from utils.password import hash_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_user_by_email(db, email: str) -> Optional[int]:
    get_user_id = "SELECT user_id FROM user_credentials WHERE email = :email"
    row = await db.fetch_one(get_user_id, {"email": email})

    if row:
        return row['user_id']

    return None


async def get_password_by_id(db, user_id) -> Optional[str]:
    query = "SELECT password FROM user_credentials WHERE user_id = :user_id"
    row = await db.fetch_one(query, {"user_id": user_id})

    if row:
        return row['password']

    return None


async def save_user(db, user: RegisterRequest) -> RegisterResponse:
    save_user_data = """
        INSERT INTO users(username, birth_date) VALUES(:username, :birth_date)
        RETURNING user_id
    """

    save_user_creds = """
        INSERT INTO user_credentials(user_id, email, password) VALUES(:user_id, :email, :hashed_pw)
        RETURNING email
    """

    user_values = {
        "username": user.username,
        "birth_date": user.birth_date,
    }

    add_bonus_balance_q = """
        INSERT INTO user_points(user_id, last_update, points_amount, prev_amount) 
        VALUES(:user_id, NOW(), 0, 0)
    """

    async with db.transaction():
        user_id = await db.fetch_one(save_user_data, user_values)

        hashed_pw = hash_password(user.password)

        cred_values = {
            "user_id": int(user_id['user_id']),
            "email": user.email,
            "hashed_pw": hashed_pw,
        }
        await  db.execute(add_bonus_balance_q, {"user_id": int(user_id['user_id'])})
        email = await db.fetch_one(save_user_creds, cred_values)

    return RegisterResponse(email=str(email['email']))


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token, secret_key=SECRET_KEY, algorith=JWT_ALGORITHM)
    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user info",
        )
    return payload

