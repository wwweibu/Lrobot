"""订阅相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import future, monitor_adapter


@monitor_adapter("/订阅_活动")
async def subscribe_activity(msg: Msg):
    """订阅活动提醒"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        await data.subscribe_data(user, "activity", "活动提醒")
        content = "订阅成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_早上好")
async def subscribe_morning(msg: Msg):
    """订阅早上好"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        await data.subscribe_data(user, "morning", "枣尚耗~")
        content = "订阅成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_晚安")
async def subscribe_evening(msg: Msg):
    """订阅晚安"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        await data.subscribe_data(user, "evening", "晚安啦~")
        content = "订阅成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_up")
async def subscribe_up(msg: Msg):
    """订阅 up"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
        if len(parts) == 2:
            msg1 = Msg(
                platform="BILI",
                event="发送",
                kind=f"私聊搜索",
                content=f"{parts[1].strip()}|bili_user"
            )
            response = await future.wait(msg1.num, "[消息]用户搜索超时")
            if not response:
                content = "无搜索结果"
            else:
                id = response[0].get("mid")
                name = response[0].get("uname")
                sign = response[0].get("usign")
                fans = response[0].get("fans")
                video = response[0].get("videos")
                content = (f"请确认信息，回复'确认'或者'取消':\n"
                           f"id:{id}\n"
                           f"名字:{name}\n"
                           f"签名:{sign}\n"
                           f"粉丝数:{fans}\n"
                           f"视频数:{video}")
                await data.status_add(msg.user, "up", f"{user}|{id}|{name}")
        else:
            content = "格式错误,请使用'/订阅,赵小爽729'类似格式"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_up_确认")
async def subscribe_up_check(msg: Msg):
    """订阅 up 确认"""
    info = await data.status_check(msg.user, "up")
    user, id, name = info.split("|")
    await data.status_delete(msg.user, "up")
    if Msg.content_join(msg.content) == "确认":
        await data.subscribe_up(user, id, name)
        content = "订阅成功"
    else:
        content = "取消成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_删除")
async def subscribe_delete(msg: Msg):
    """删除订阅"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
        if len(id) == 2:
            id = id[1].strip()
            try:
                id = int(id)
                content = await data.subscribe_delete(user, id)
            except ValueError:
                content = "格式错误，请输入'/订阅删除,1'类似格式"
        else:
            content = "您已订阅以下内容，请输入'/订阅删除,[序号]'以取消订阅\n"
            content += await data.subscribe_check(user)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
