"""待办与提醒创建"""

from datetime import datetime

from message.handler.msg import Msg
from config import chunk_sleep, create_background_task, database_query, database_update


async def remind_send(id, target_time, content, user):
    """待办提醒"""
    now = datetime.now()
    diff = (target_time - now).total_seconds()
    await chunk_sleep(diff)
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        content=f"小推提醒您，{content}",
        user=user,
    )
    sql = "DELETE FROM system_remind WHERE id = %s"
    await database_update(sql, (id,))



async def remind_load():
    """系统重启时重新加载未过期的提醒"""
    sql = "SELECT id, time, content, user FROM system_remind"
    reminders = await database_query(sql)

    for r in reminders:
        create_background_task(
            remind_send(r["id"], r["time"], r["content"], r["user"]),
            name=f"reminder:{r['id']}",
        )
