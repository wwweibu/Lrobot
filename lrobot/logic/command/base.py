"""基础功能"""

import re

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter, config


@monitor_adapter("/基础_活动")
async def base_activity(msg: Msg):
    """活动"""
    content = await data.system_get("activity")
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


@monitor_adapter("/基础_活动_修改")
async def base_activity_change(msg: Msg):
    """修改活动"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 1:
        await data.status_add(msg.user, msg.platform, "活动修改")
        content = "请输入活动"
    else:
        await data.system_edit("activity", parts[1].strip())
        await data.subscribe_activity()
        content = "已记录"
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


@monitor_adapter("/基础_活动_修改_回答")
async def base_activity_change_answer(msg: Msg):
    """修改活动输入"""
    content = Msg.content_join(msg.content)
    await data.system_edit("activity", content)
    await data.subscribe_activity()
    await data.status_delete(msg.user, msg.platform, "活动修改")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="已记录",
        user=msg.user,
        group=msg.group,
    )
    return content

@monitor_adapter("/基础_书单")
async def base_book(msg: Msg):
    """推荐书单"""
    content = await data.system_get("book")
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


@monitor_adapter("/基础_书单_修改")
async def base_book_change(msg: Msg):
    """修改当前书单"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 1:
        await data.status_add(msg.user, msg.platform, "书单修改")
        content = "请输入书单"
    else:
        await data.system_edit("book", parts[1].strip())
        content = "已记录"
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


@monitor_adapter("/基础_书单_修改_回答")
async def base_book_change_answer(msg: Msg):
    """修改书单输入"""
    content = Msg.content_join(msg.content)
    await data.system_edit("book", content)
    await data.status_delete(msg.user, msg.platform, "书单修改")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="已记录",
        user=msg.user,
        group=msg.group,
    )
    return content

@monitor_adapter("/基础_留言")
async def base_word(msg: Msg):
    """留言"""
    name = await data.user_name(msg.user, msg.platform)
    content = ("来自" + name + "的留言--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        content=content,
        user=config["private"]["微部"][0],
    )
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="阁下，您的讯息已记录在案。它将如信鸽般迅速抵达协会总部。",
        user=msg.user,
        group=msg.group,
    )
    return content



@monitor_adapter("/基础_转发")
async def base_unknown(msg: Msg):
    """兜底指令"""
    content = ""
    if Msg.content_join(msg.content).startswith("/"):
        Msg(
            platform=msg.platform,
            kind=f"{msg.kind[:2]}发送",
            event="发送",
            user=msg.user,
            seq=msg.seq,
            content="阁下，此指令不在当前行动清单内。建议使用 /帮助 进行核查。",
            group=msg.group,
        )
    if msg.platform in ["LR232", "WECHAT", "BILI"]:
        content = ("来自" + msg.user + "的消息--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            user=config["private"]["微部"][0],
            content=content
        )
    return content
