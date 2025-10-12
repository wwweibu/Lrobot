"""待办与提醒创建"""

import asyncio
from datetime import datetime

from message.handler.msg import Msg
from config import database_update, database_query


async def remind_send(id, target_time, content, user):
    """待办提醒"""
    while True:
        now = datetime.now()
        diff = (target_time - now).total_seconds()
        if diff <= 0:
            Msg(
                platform="LR5921",
                event="发送",
                kind="私聊发送",
                content=f"小推提醒您，{content}",
                user=user,
            )
            sql = "DELETE FROM system_remind WHERE id = %s"
            await database_update(sql, (id,))
            break
        await asyncio.sleep(min(diff, 3600))


async def remind_load():
    """系统重启时重新加载未过期的提醒"""
    sql = "SELECT id, time, content, user FROM system_remind"
    reminders = await database_query(sql)

    for r in reminders:
        asyncio.create_task(remind_send(r["id"], r["time"], r["content"], r["user"]))
