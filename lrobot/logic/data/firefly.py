"""测试群相关"""

import random
import asyncio

from message.handler.msg import Msg
from config import database_update, database_query, future


async def firefly_judge(user):
    """判断是否在测试群"""
    query = "SELECT EXISTS(SELECT 1 FROM user_test WHERE user = %s) AS exists_flag"
    result = await database_query(query, (user,))
    return result[0]["exists_flag"] == 1


async def firefly_update():
    """更新测试群列表"""
    msg = Msg(
        platform="LR5921",
        kind="群聊成员",
        event="发送",
        group="786159347",
    )
    try:
        _future = future.get(msg.num)
        response = await asyncio.wait_for(_future, timeout=20)
        user_dict = {item["user_id"]: item.get("nickname") for item in response}
    except asyncio.TimeoutError:
        raise Exception(f"测试群列表获取超时")

    new_users = set(user_dict.keys())

    # 获取数据库中所有已有 user
    query = "SELECT user FROM user_test"
    existing_rows = await database_query(query)
    existing_users = {row["user"] for row in existing_rows}

    # 计算需要删除的 user
    to_delete = existing_users - new_users

    # 删除多余的 source
    if to_delete:
        delete_query = f"DELETE FROM user_test WHERE user IN ({','.join(['%s'] * len(to_delete))})"
        await database_update(delete_query, tuple(to_delete))

    upsert_query = """
        INSERT INTO user_test (user, nickname)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE nickname = VALUES(nickname)
    """
    for user in new_users:
        codename = user_dict[user]
        await database_update(upsert_query, (user, codename))


async def firefly_password_update(user, name):
    """分配管理员账号密码"""
    password = random.randint(100000, 999999)
    query = """
           INSERT INTO user_test (user, name, password)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE
               name = VALUES(name),
               password = VALUES(password)
       """
    await database_update(query, (user, name, password))
    return password


async def firefly_password_get(name):
    """根据管理员名称 name 获取对应的密码"""
    query = "SELECT password FROM user_test WHERE name = %s LIMIT 1"
    result = await database_query(query, (name,))

    if result:
        return result[0]["password"]
    else:
        return None
