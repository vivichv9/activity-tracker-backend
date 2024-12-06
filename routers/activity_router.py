from databases import Database
from fastapi import APIRouter, Depends
from sqlalchemy.sql.functions import current_user

from db.db import get_db
from models.activity import ActivityListResponse
from models.personal import StartActivityRequest, StartActivityResponse, EndActivityResponse
from services.auth import get_current_user, get_user_by_email
from services.query import get_activity_by_type, save_user_activity, check_activity_exists, end_user_activity, \
    get_user_activities_by_id

router = APIRouter()


@router.post("/start")
async def start_activity(req: StartActivityRequest, current_user: dict = Depends(get_current_user),
                         db: Database = Depends(get_db)) -> StartActivityResponse:
    user_id = await get_user_by_email(db, current_user['sub'])
    activity_id = await get_activity_by_type(db, req.activity_type)

    await check_activity_exists(db, user_id)

    time = await save_user_activity(db, user_id, activity_id)

    time = 1

    

    return StartActivityResponse(start_time=str(time))


@router.post("/end")
async def end_activity(current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)) -> EndActivityResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    cals, time = await end_user_activity(db, user_id)

    return EndActivityResponse(burned=float(cals), minutes=float(time))


@router.get("/list")
async def get_activities(current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)) -> ActivityListResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    user_activities = await get_user_activities_by_id(db, user_id, limit=1000)

    activities = []
    if user_activities is not None:
        activities = [(el['type'], el['start_time'], el['end_time'], el['burned_calories']) for el in user_activities]

    return ActivityListResponse(activities=activities)

