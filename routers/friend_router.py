from databases import Database
from fastapi import APIRouter, Depends

from db.db import get_db
from models.friends import FriendRequest, FriendResponse, FriendListResponse
from services.auth import get_current_user, get_user_by_email
from services.friend import check_exist_username, add_friend, update_friend_request
from services.query import get_user_friends_by_id

router = APIRouter()

@router.get('/list')
async def get_friends(current_user: dict = Depends(get_current_user),
                      db: Database = Depends(get_db)) -> FriendListResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    friends = await get_user_friends_by_id(db, user_id, limit=1000)

    return FriendListResponse(friends=friends)


@router.post('/add')
async def add_friend_router(req: FriendRequest,
                            current_user: dict = Depends(get_current_user),
                            db: Database = Depends(get_db)) -> FriendResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    friend_id = await check_exist_username(db, req.username)

    await add_friend(db, friend_id, user_id)

    return FriendResponse(username=req.username)


@router.post('/confirm')
async def confirm_friend(req: FriendRequest,
                         current_user: dict = Depends(get_current_user),
                         db: Database = Depends(get_db)) -> FriendResponse:
    user_id = await get_user_by_email(db, current_user['sub'])
    friend_id = await check_exist_username(db, req.username)

    await update_friend_request(db, friend_id, user_id, 'confirmed')

    return FriendResponse(username=req.username)


@router.post('/reject')
async def confirm_friend(req: FriendRequest,
                         current_user: dict = Depends(get_current_user),
                         db: Database = Depends(get_db)) -> FriendResponse:
    user_id = await get_user_by_email(db, current_user['sub'])
    friend_id = await check_exist_username(db, req.username)

    await update_friend_request(db, friend_id, user_id, 'rejected')

    return FriendResponse(username=req.username)


@router.post('/delete')
async def confirm_friend(req: FriendRequest,
                         current_user: dict = Depends(get_current_user),
                         db: Database = Depends(get_db)) -> FriendResponse:
    user_id = await get_user_by_email(db, current_user['sub'])
    friend_id = await check_exist_username(db, req.username)

    await update_friend_request(db, friend_id, user_id, 'deleted')

    return FriendResponse(username=req.username)