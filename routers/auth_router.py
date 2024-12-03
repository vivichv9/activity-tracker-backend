from databases import Database
from fastapi import APIRouter, HTTPException, Depends

from db.db import get_db
from models.auth import RegisterResponse, RegisterRequest, LoginResponse, LoginRequest
from services.auth import save_user, get_user_by_email, get_password_by_id, get_current_user
from utils.email import validate_email_address
from utils.jwt_utils import create_access_token, create_refresh_token
from utils.password import verify_password
from config import SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_REFRESH_TOKEN_EXPIRE_DAYS
from datetime import timedelta

router = APIRouter()

@router.post("/reg/", response_model=RegisterResponse)
async def register(req: RegisterRequest, db: Database = Depends(get_db)):
    if len(req.password) < 8 or len(req.password) > 32:
        raise HTTPException(status_code=400, detail="Uncorrect Password")

    if len(req.username) < 4 or len(req.username) > 24:
        raise HTTPException(status_code=400, detail="Uncorrect username")

    if not validate_email_address(req.email):
        raise HTTPException(status_code=400, detail="Uncorrect email address")

    existing_user = await get_user_by_email(db, req.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    response = await save_user(db, req)

    return response


@router.post("/login/", response_model=LoginResponse)
async def login(req: LoginRequest, db: Database = Depends(get_db)):
    user_id = await get_user_by_email(db, req.email)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid email")

    password = await get_password_by_id(db, user_id)

    if not verify_password(req.password, password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": req.email},
                                       secret_key=str(SECRET_KEY),
                                       expires_delta=timedelta(minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)),
                                       algorithm=JWT_ALGORITHM)

    refresh_token = create_refresh_token(data={"sub": req.email},
                                         secret_key=str(SECRET_KEY),
                                         expires_delta=timedelta(days=int(JWT_REFRESH_TOKEN_EXPIRE_DAYS)),
                                         algorithm=JWT_ALGORITHM)

    return LoginResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


