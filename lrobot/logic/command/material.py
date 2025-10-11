"""更新物资"""

import re

from logic import data
from config import monitor_adapter
from message.handler.msg import Msg


@monitor_adapter("/物资_更新")
async def material_add(msg: Msg):
    """更新物资"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        await data.material_add(parts[1].strip(), parts[2].strip())
        content = "更新成功"
    else:
        content = "更新失败，请使用'/物资,物资,备注'类似格式"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return f"{parts[1].strip()}|{parts[2].strip()}"


@monitor_adapter("/物资_查询")
async def material_get(msg: Msg):
    """查询物资"""
    content = await data.material_get()
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content
