import time
import random
import asyncio
from message.handler.msg import Msg
from config import query_database,update_database,future
async def judge_user_test_group(source):
    """判断是否在测试群"""
    query = "SELECT EXISTS(SELECT 1 FROM user_test WHERE source = %s) AS exists_flag"
    result = await query_database(query, (source,))
    return result[0]["exists_flag"] == 1


async def update_user_test_group():
    """更新测试群列表"""
    seq = f"test_{int(time.time() * 1000)}"
    Msg(
        robot="LR5921",
        kind="群聊获取信息",
        event="发送",
        source="663748426",
        seq=seq,
        content="786159347",
        group=""
    )
    try:
        _future = future.get(seq)
        response = await asyncio.wait_for(_future, timeout=20)
        data = response.json().get("data", {})
        user_dict = {item["user_id"]: item.get("nickname") for item in data}
    except asyncio.TimeoutError:
        raise Exception(f"测试群列表获取超时")

    new_sources = set(user_dict.keys())

    # 获取数据库中所有已有 source
    query = "SELECT source FROM user_test"
    existing_rows = await query_database(query)
    existing_sources = {row["source"] for row in existing_rows}

    # 计算需要新增和删除的 source
    to_add = new_sources - existing_sources
    to_delete = existing_sources - new_sources
    to_update = new_sources & existing_sources

    # 删除多余的 source
    if to_delete:
        delete_query = f"DELETE FROM user_test WHERE source IN ({','.join(['%s'] * len(to_delete))})"
        await update_database(delete_query, tuple(to_delete))

    # 插入新增的 source + codename
    insert_query = "INSERT INTO user_test (source, nickname) VALUES (%s, %s)"
    for source in to_add:
        codename = user_dict[source]
        await update_database(insert_query, (source, codename))

    # 更新已存在的 nickname
    update_query = "UPDATE user_test SET nickname = %s WHERE source = %s"
    for source in to_update:
        codename = user_dict[source]
        await update_database(update_query, (codename, source))


async def update_user_test_group_password(source,name):
    """分配管理员账号密码"""
    password = random.randint(100000, 999999)
    query = """
           INSERT INTO user_test (source, name, password)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE
               name = VALUES(name),
               password = VALUES(password)
       """
    await update_database(query, (source, name, password))
    return password


async def get_user_test_group_password(name):
    """根据管理员名称 name 获取对应的密码"""
    query = "SELECT password FROM user_test WHERE name = %s LIMIT 1"
    result = await query_database(query, (name,))

    if result:
        return result[0]["password"]
    else:
        return None
