from databases import Database
from fastapi import APIRouter, Depends

from db.db import get_db
from models.personal import DashboardResponse
from services.auth import get_current_user, get_user_by_email
from services.query import get_user_friends_by_id, get_user_achievements_by_id, get_user_activities_by_id, \
    get_username_by_id, get_user_bonuses_by_id, get_current_train

router = APIRouter()

@router.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user), db: Database = Depends(get_db)) -> DashboardResponse:
    user_id = await get_user_by_email(db, current_user['sub'])

    user_friends = await get_user_friends_by_id(db, user_id, limit=5)
    user_achievements = await get_user_achievements_by_id(db, user_id, limit=5)
    user_activities = await get_user_activities_by_id(db, user_id, limit=5)

    activities = []
    if user_activities is not None:
        activities = [activity['type'] + '\t' + str(activity['start_time']) for activity in user_activities]

    username = await get_username_by_id(db, user_id)
    bonuses = await get_user_bonuses_by_id(db, user_id)
    active_train = await get_current_train(db, user_id)
    return DashboardResponse(username=username,
                             last_activities=activities,
                             achievements=user_achievements,
                             friends=[el[0] for el in user_friends],
                             bonuses=bonuses,
                             email=current_user['sub'],
                             active_train=active_train)


