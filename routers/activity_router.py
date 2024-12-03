from databases import Database
from fastapi import APIRouter, Depends

from db.db import get_db
from models.personal import StartActivityRequest, StartActivityResponse, EndActivityResponse
from services.auth import get_current_user, get_user_by_email
from services.query import get_activity_by_type, save_user_activity, check_activity_exists, end_user_activity

router = APIRouter()


@router.post("/start")
async def start_activity(req: StartActivityRequest, current_user: dict = Depends(get_current_user),
                         db: Database = Depends(get_db)) -> StartActivityResponse:
    user_id = await get_user_by_email(db, current_user['sub'])
    activity_id = await get_activity_by_type(db, req.activity_type)

    await check_activity_exists(db, user_id)

    time = await save_user_activity(db, user_id, activity_id)
    return StartActivityResponse(start_time=str(time))


@router.post("/end")
async def end_activity(current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)) -> EndActivityResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    cals, time = await end_user_activity(db, user_id)

    return EndActivityResponse(burned=float(cals), minutes=float(time))