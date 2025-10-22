"""更新物资"""

import re

from logic import data
from config import monitor_adapter
from message.handler.msg import Msg


@monitor_adapter("/工具_物资")
async def material_add(msg: Msg):
    """更新物资"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        await data.material_add(parts[1].strip(), parts[2].strip())
        content = "更新成功"
    elif len(parts) == 1:
        content = "请输入物资"
        await data.status_add(msg.user, msg.platform, "物资1")
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
    return content


@monitor_adapter("/工具_物资_物资")
async def material_add_1(msg: Msg):
    """物资更新输入物资"""
    material = Msg.content_join(msg.content).strip()
    await data.status_delete(msg.user, msg.platform, "物资1")
    await data.status_add(msg.user, msg.platform, "物资2", material)
    content = "请输入物资备注，若无则发送空格"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/工具_物资_备注")
async def material_add_2(msg: Msg):
    """物资更新输入备注"""
    remark = Msg.content_join(msg.content).strip()
    material = await data.status_check(msg.user, msg.platform, "物资2")
    await data.material_add(material, remark)
    content = "更新成功"
    await data.status_delete(msg.user, msg.platform, "物资2")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content

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
