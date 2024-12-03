from databases import Database
from fastapi import HTTPException

async def check_friend_already_exist(db: Database, friend_id: int, user_id: int) -> bool:
    get_friendship_id_q = """
        SELECT friendship_id
        FROM friendships
        WHERE user_id = :user_id AND friend_id = :friend_id
    """

    friendship_id = await db.fetch_one(get_friendship_id_q, {"user_id": user_id, "friend_id": friend_id})

    if friendship_id is None:
        return False

    return True


async def check_exist_username(db: Database, username: str) -> int:
    get_id_by_username_q = """
        SELECT user_id
        FROM users
        WHERE username = :username
    """

    friend_id = await db.fetch_one(get_id_by_username_q, {'username': username})

    if friend_id is None:
        raise HTTPException(status_code=400, detail=f"User with username: {username} not found!")

    return friend_id['user_id']


async def add_friend(db: Database, friend_id: int, user_id: int) -> None:
    is_exist = await check_friend_already_exist(db, friend_id, user_id)

    if is_exist:
        raise HTTPException(status_code=400, detail=f"Friendships with user already exist!")

    add_friend_request_q = """
        INSERT INTO friendships (user_id, friend_id, status, created_at, updated_at)
        VALUES (:user_id, :friend_id, 'pending', NOW(), NOW())
    """

    await db.execute(add_friend_request_q, {"user_id": user_id, "friend_id": friend_id})


async def update_friend_request(db: Database, friend_id: int, user_id: int, status: str) -> None:
    get_friendship_id_q = """
        SELECT status 
        FROM friendships
        WHERE user_id = :user_id AND
        friend_id = :friend_id 
        AND updated_at = (SELECT MAX(updated_at) FROM friendships WHERE user_id = :user_id)
    """

    friendship_id = await db.fetch_one(get_friendship_id_q, {'user_id': user_id, 'friend_id': friend_id})

    if friendship_id is None:
        raise HTTPException(status_code=400, detail=f"Friendships not found!")

    update_status_q = """
        INSERT INTO friendships (user_id, friend_id, status, created_at, updated_at)
        VALUES (:user_id, :friend_id, :status, (SELECT created_at
                                                FROM friendships
                                                WHERE user_id = :user_id AND
                                                friend_id = :friend_id 
                                                AND updated_at = (SELECT MIN(updated_at)
                                                                  FROM friendships
                                                                  WHERE user_id = :user_id)), NOW())
    """

    await db.execute(update_status_q, {"user_id": user_id,"status": status, 'friendship_id': friendship_id})