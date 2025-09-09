"""工具"""

import re
import time
import jionlp as jio
from datetime import datetime

from logic import data
from config import database_update
from message.handler.msg import Msg


async def tool_list(msg: Msg):
    """获取工具列表"""
    content = ("当前工具:\n"
               "待办:\n"
               "/待办,[时间],[事项]:设置待办,将用LR5921私聊提醒\n"
               "其中时间可以是模糊表述,如一个月后\n"
               "不能使用9.10表示日期，或者3h/m/s表示时间\n"
               "未绑定 LR5921 无法使用")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def tool_pending(msg: Msg):
    """设置待办"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
        content = "格式错误，请使用'/待办，时间，事项'"
        if len(parts) == 3:
            try:
                pending_time = jio.parse_time(parts[1], time_base=time.time(), time_type="time_point")
                if pending_time["type"] == "time_point" or pending_time["type"] == "time_span":
                    pending_time = pending_time["time"][0]
                    target_time = datetime.strptime(pending_time, "%Y-%m-%d %H:%M:%S")
                    content = f"设置成功，将在 {pending_time} 提醒您 {parts[2]}"
                    Msg(
                        platform=msg.platform,
                        event="发送",
                        kind=f"{msg.kind[:2]}发送",
                        seq=msg.seq,
                        content=content,
                        user=msg.user,
                        group=msg.group,
                    )
                    sql = "INSERT INTO system_remind (time, content, user) VALUES (%s, %s, %s)"
                    id = await database_update(sql, (target_time, parts[2], user))
                    await data.remind_send(id, target_time, parts[2], user)
                    return
                else:
                    content = "时间格式错误，请不要用7.1表示日期，用h、m、s表示时分秒"
            except Exception:
                content = "时间格式错误，请不要用7.1表示日期，用h、m、s表示时分秒"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
