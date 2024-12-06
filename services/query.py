from fastapi import HTTPException

async def get_user_achievements_by_id(db, user_id, limit):
    user_achievements_q = """
        SELECT name
        FROM user_achievements JOIN achievements USING (achievement_id)
        WHERE user_id = :user_id
        LIMIT :limit
    """

    user_achievements = await db.fetch_all(user_achievements_q, {"user_id": user_id,
                                                                 "limit": limit})
    achievements = []
    if achievements is not None:
        achievements = [achievement['name'] for achievement in user_achievements]

    return achievements


async def get_user_activities_by_id(db, user_id, limit):
    user_activities_q = """
        SELECT type, start_time, end_time, burned_calories
        FROM user_activities JOIN activities USING (activity_id)
        WHERE user_id = :user_id
        LIMIT :limit
    """

    user_activities = await db.fetch_all(user_activities_q, {"user_id": user_id,
                                                             "limit": limit})
    # activities = []
    # if user_activities is not None:
    #     activities = [activity['type'] + '\t\t' + str(activity['start_time']) for activity in user_activities]

    return user_activities


async def get_user_friends_by_id(db, user_id, limit):
    get_friends_q = """
        WITH get_deleted AS (
            SELECT friendships.friend_id
            FROM friendships
            WHERE (friendships.user_id = :user_id OR friendships.friend_id = :user_id) AND status = 'deleted'
        ), get_id AS (
            SELECT friendships.friend_id
            FROM friendships
            WHERE (friendships.user_id = :user_id OR friendships.friend_id = :user_id) AND
            friend_id NOT IN (SELECT friend_id FROM get_deleted) AND
            status = 'confirmed'
        )
        
        SELECT username, points_amount FROM users JOIN user_points USING(user_id) 
        WHERE user_id IN (SELECT friend_id FROM get_id)
        LIMIT :limit
    """

    q = """
        WITH subq AS (
            SELECT user_id, friend_id
            FROM friendships
            WHERE status = 'confirmed' AND (user_id = :user_id OR friend_id = :user_id)
        ), subq_1 AS (
            SELECT user_id FROM subq
            WHERE user_id != :user_id
            UNION
            SELECT friend_id AS user_id FROM subq
            WHERE friend_id != :user_id
            LIMIT :limit
        )

        SELECT users.username, user_points.points_amount  FROM users JOIN subq_1 USING(user_id) JOIN user_points USING(user_id)
    """

    user_friends = await db.fetch_all(q, {"user_id": user_id,
                                                      "limit": limit})
    friends = []
    if user_friends is not None:
        friends = [(friend['username'], friend['points_amount']) for friend in user_friends]

    return friends


async def get_user_bonuses_by_id(db, user_id) -> int:
    get_bonuses_q = """
        SELECT points_amount FROM user_points
        WHERE user_id = :user_id AND last_update = (SELECT MAX(last_update) FROM user_points
                                                    WHERE user_id = :user_id)       
    """

    user_bonuses = await db.fetch_one(get_bonuses_q, {"user_id": user_id,})

    if user_bonuses is not None:
        return user_bonuses['points_amount']

    return 0


async def get_username_by_id(db, user_id) -> str:
    get_username_q = """
        SELECT username FROM users WHERE user_id = :user_id
    """

    username = await db.fetch_one(get_username_q, {"user_id": user_id})
    return username['username']


async def get_activity_by_type(db, activity_type):
    get_activity_q = """
        SELECT activity_id FROM activities WHERE type = :activity_type
    """

    activity = await db.fetch_one(get_activity_q, {"activity_type": activity_type})
    if activity is not None:
        return activity['activity_id']

    else:
        raise HTTPException(status_code=404, detail="Activity not found")


async def save_user_activity(db, user_id, activity_id):
    save_activity_q = """
        INSERT INTO user_activities(user_id, activity_id, start_time, end_time, burned_calories)
        VALUES (:user_id, :activity_id, NOW(),NULL, NULL)
        RETURNING start_time
    """

    time = await db.fetch_one(save_activity_q, {"user_id": user_id,
                                           "activity_id": activity_id,})
    return time['start_time']


async def check_activity_exists(db, user_id):
    check_q = """
        SELECT activity_id FROM user_activities
        WHERE user_id = :user_id AND end_time is NULL
    """

    activity = await db.fetch_one(check_q, {"user_id": user_id})
    if activity is None:
        return

    raise HTTPException(status_code=400, detail="You have active activity xD")


async def end_user_activity(db, user_id):
    get_activity_q = """
        SELECT activity_id, EXTRACT(EPOCH FROM NOW() - start_time) / 60 AS duration FROM user_activities
        WHERE user_id = :user_id AND end_time is NULL
    """

    log_activity_q = """
        UPDATE user_activities 
        SET end_time = NOW(),
            burned_calories = :cals
        WHERE user_id = :user_id AND end_time is NULL
    """

    get_activity_cost_q = """
        SELECT cals_per_min, points_per_min FROM activities
        WHERE  activity_id = :activity_id
    """

    get_user_points = """
        SELECT points_amount FROM user_points
        WHERE user_id = :user_id
    """

    set_user_points = """
        UPDATE user_points 
        SET user_id = :user_id,
            last_update = NOW(),
            points_amount = :current,
            prev_amount = :prev
        WHERE user_id = :user_id
    """

    select_prev_stat = """
        SELECT total_duration_minutes, total_cals_burned, activities_count FROM user_stats
        WHERE user_id = :user_id AND activity_id = :activity_id
    """

    update_stat_q = """
        UPDATE user_stats
        SET total_duration_minutes = :new_minutes,
            total_cals_burned = :new_cals_burned,
            activities_count = :new_count,
            updated_at = NOW()
        WHERE user_id = :user_id AND activity_id = :activity_id
    """

    create_new_stat_q = """
        INSERT INTO user_stats(user_id, activity_id, total_duration_minutes, total_cals_burned, activities_count, updated_at)
        VALUES (:user_id, :activity_id, :duration, :burned, 1, NOW())
    """


    async with db.transaction():
        q_activity = await db.fetch_one(get_activity_q, {"user_id": user_id,})

        if q_activity is None:
            raise HTTPException(status_code=400, detail="You dont have activity yet")

        duration = q_activity['duration']
        activity_id = q_activity['activity_id']

        q_costs = await db.fetch_one(get_activity_cost_q, {"activity_id": activity_id,})

        cals_per_min = q_costs['cals_per_min']
        points_per_min = q_costs['points_per_min']

        cals_burned = float(cals_per_min) * float(duration)
        points_collected = float(points_per_min) * float(duration)

        await db.execute(log_activity_q, {"user_id": user_id, "cals": float(cals_burned)})

        q_points = await db.fetch_one(get_user_points, {"user_id": user_id,})

        if q_points is None:
            await db.execute(set_user_points, {"user_id": user_id, "current": int(points_collected), "prev": 0})

        else:
            prev_points = q_points['points_amount']
            await db.execute(set_user_points, {"user_id": user_id, "current": int(points_collected) + int(prev_points), "prev": int(prev_points)})


        q_stat = await db.fetch_one(select_prev_stat, {"user_id": user_id, "activity_id": activity_id})

        if q_stat is None:
            await db.execute(create_new_stat_q, {"user_id": user_id,
                                                 "activity_id": activity_id,
                                                 "duration": float(duration),
                                                 "burned": float(cals_burned),})
        else:
            await db.execute(update_stat_q, {"user_id": user_id,
                                         "activity_id": activity_id,
                                         "new_minutes": float(duration) + float(q_stat['total_duration_minutes']),
                                         "new_cals_burned": float(cals_burned) + float(q_stat['total_cals_burned']),
                                         "new_count": int(q_stat['activities_count']) + 1})

        return cals_burned, duration


async def get_current_train(db, user_id):
    get_train_q = """
        WITH suubq AS (
            SELECT activity_id
            FROM user_activities
            WHERE user_id = :user_id AND end_time IS NULL
        )
        SELECT type FROM activities
        where activity_id = (SELECT activity_id FROM suubq)
    """

    active_train = await db.fetch_one(get_train_q, {"user_id": user_id})

    if active_train is None:
        return "Нет активности"

    return active_train['type']
