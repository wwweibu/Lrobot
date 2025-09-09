"""订阅查询相关"""

import asyncio
import datetime

from message.handler.msg import Msg
from .file import sparkle_record_deal
from config import database_update, database_query, scheduler_add, future

up = []


async def subscribe_up(user, mid):
    """订阅 b 站 up"""
    query = """
            INSERT INTO user_subscribe (user, sub)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE sub = sub
        """
    await database_update(query, (user, f"up_{mid}"))
    if mid not in up:
        await subscribe_up_query(mid)
        asyncio.create_task(scheduler_add(subscribe_up_query, mid, interval=600))
        up.append(mid)


async def subscribe_up_query(mid):
    """定期查询 up 视频"""
    msg = Msg(
        platform="BILI",
        kind="私聊用户视频",
        event="发送",
        user=mid,
    )
    try:
        _future = future.get(msg.num)
        response = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
        raise Exception(f"用户{mid}视频获取超时")
    bv = response[0].get("bvid")
    title = response[0].get("title")
    rows = await database_query(
        "SELECT id, user, info FROM user_subscribe WHERE sub = %s",
        (f"up_{mid}",)
    )

    msg = Msg(
        platform="BILI",
        kind="私聊昵称",
        event="发送",
        user=mid,
    )
    try:
        _future = future.get(msg.num)
        mid = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
        mid = mid

    for row in rows:
        id = row["id"]
        user = row["user"]
        bv_id = row["info"]

        if bv != bv_id:
            content = f"{mid}发布视频啦！\n[{title}]"
            Msg(
                platform="LR5921",
                kind="私聊发送",
                event="发送",
                user=user,
                content=content
            )
            await database_update(
                "UPDATE user_subscribe SET info = %s WHERE id = %s",
                (bv, id)
            )


async def subscribe_up_init():
    """加载所有 up 订阅"""
    # 早上好
    asyncio.create_task(scheduler_add(subscribe_sparkle_query, interval=600))

    # 其他
    rows = await database_query("SELECT DISTINCT sub FROM user_subscribe")

    for row in rows:
        sub = row["sub"]
        if sub.startswith("up_"):
            mid = sub[4:]
            asyncio.create_task(scheduler_add(subscribe_up_query, mid, interval=600))


async def subscribe_sparkle(user):
    """订阅花火每日问好"""
    query = """
                INSERT INTO user_subscribe (user, sub)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE sub = sub
            """
    await database_update(query, (user, f"sparkle"))


async def subscribe_sparkle_query():
    """定期查询早上好视频"""
    msg = Msg(
        platform="BILI",
        kind="私聊用户视频",
        event="发送",
        user="4729816",
    )
    try:
        _future = future.get(msg.num)
        response = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
        raise Exception("花火视频获取超时")

    bv = response[0].get("bvid")
    today = datetime.datetime.now().strftime("%Y%m%d")

    rows = await database_query(
        "SELECT id, user,info FROM user_subscribe WHERE sub = %s",
        ("sparkle",)
    )

    for row in rows:
        id = row["id"]
        user = row["user"]
        last_info = row["info"]

        if last_info != today:
            await database_update(
                "UPDATE user_subscribe SET info = %s WHERE id = %s",
                (today, id)
            )
            record = await sparkle_record_deal(bv, today)
            Msg(
                platform="LR5921",
                kind="私聊发送",
                event="发送",
                user=user,
                content=f"[语音:{record}]"
            )
