"""海龟汤数据处理"""

import json
import random

from config import database_query, database_update


async def soup_random_get(exclude_id=None):
    """随机抽取一条海龟汤，exclude_id 指定时尽量不重复；
    若题库只有一条则直接返回该条"""
    if exclude_id:
        rows = await database_query(
            "SELECT id, title, author, surface, bottom FROM system_soup WHERE id != %s",
            (exclude_id,),
        )
        if not rows:
            rows = await database_query(
                "SELECT id, title, author, surface, bottom FROM system_soup"
            )
    else:
        rows = await database_query(
            "SELECT id, title, author, surface, bottom FROM system_soup"
        )
    if not rows:
        return None
    return random.choice(rows)


async def soup_get(soup_id):
    """根据 id 获取海龟汤"""
    rows = await database_query(
        "SELECT id, title, author, surface, bottom FROM system_soup WHERE id = %s",
        (soup_id,),
    )
    return rows[0] if rows else None


async def soup_state_get(group):
    """读取某个群的海龟汤对局状态，返回 dict 或 None"""
    name = f"turtle_soup_{group}"
    rows = await database_query(
        "SELECT text FROM system_data WHERE name = %s", (name,)
    )
    if not rows or not rows[0]["text"]:
        return None
    try:
        return json.loads(rows[0]["text"])
    except (json.JSONDecodeError, TypeError):
        return None


async def soup_state_set(group, state):
    """写入某个群的海龟汤对局状态"""
    name = f"turtle_soup_{group}"
    text = json.dumps(state, ensure_ascii=False)
    await database_update(
        "INSERT INTO system_data (name, text) VALUES (%s, %s) "
        "AS new ON DUPLICATE KEY UPDATE text = new.text",
        (name, text),
    )


async def soup_state_clear(group):
    """清除某个群的海龟汤对局状态"""
    name = f"turtle_soup_{group}"
    await database_update("DELETE FROM system_data WHERE name = %s", (name,))


async def soup_search(keyword):
    """按名称或作者模糊查询，返回列表"""
    like = f"%{keyword}%"
    rows = await database_query(
        "SELECT id, title, author, surface, bottom FROM system_soup "
        "WHERE title LIKE %s OR author LIKE %s ORDER BY id DESC",
        (like, like),
    )
    return rows or []


async def soup_delete_by_id(soup_id):
    """根据 id 删除一条海龟汤"""
    await database_update("DELETE FROM system_soup WHERE id = %s", (soup_id,))


async def soup_find_by_title(title):
    """根据 title 精确查找（title 默认可为空）"""
    if title == "":
        rows = await database_query(
            "SELECT id, title, author, surface, bottom FROM system_soup "
            "WHERE title = '' OR title IS NULL ORDER BY id DESC"
        )
    else:
        rows = await database_query(
            "SELECT id, title, author, surface, bottom FROM system_soup "
            "WHERE title = %s ORDER BY id DESC",
            (title,),
        )
    return rows or []


async def soup_add(title, author, surface, bottom):
    """新增一条海龟汤，返回新 id"""
    return await database_update(
        "INSERT INTO system_soup (title, author, surface, bottom) VALUES (%s, %s, %s, %s)",
        (title, author, surface, bottom),
    )

