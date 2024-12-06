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
        WHERE (user_id = :user_id AND friend_id = :friend_id) OR (friend_id = :user_id AND user_id = :friend_id)
    """

    friendship_id = await db.fetch_one(get_friendship_id_q, {'user_id': user_id, 'friend_id': friend_id})
    print('4')
    if friendship_id is None:
        raise HTTPException(status_code=400, detail=f"Friendships not found!")

    # update_status_q = """
    #     INSERT INTO friendships (user_id, friend_id, status, created_at, updated_at)
    #     VALUES (:user_id, :friend_id, :status, (SELECT created_at
    #                                             FROM friendships
    #                                             WHERE user_id = :user_id AND
    #                                             friend_id = :friend_id
    #                                             AND updated_at = (SELECT MIN(updated_at)
    #                                                               FROM friendships
    #                                                               WHERE user_id = :user_id)), NOW())
    # """

    update_q = """
        UPDATE friendships 
        SET status = :status,
            updated_at = NOW()
        WHERE (user_id = :user_id AND friend_id = :friend_id) OR (friend_id = :user_id AND user_id = :friend_id)
    """

    await db.execute(update_q, {"user_id": user_id,"status": status, "friend_id": friend_id})


async def get_orders(db: Database, user_id: int):
    orders_q = """
        WITH get_senders AS (
            SELECT user_id 
            FROM friendships
            WHERE friend_id = :user_id AND status = 'pending'
        )

        SELECT username FROM users
        WHERE user_id IN (SELECT user_id FROM get_senders)
    """

    orders_res = await db.fetch_all(orders_q, {'user_id': user_id})

    return [el['username'] for el in orders_res]
