"""订阅相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import future, monitor_adapter


@monitor_adapter("/订阅_订阅")
async def subscribe_subscribe(msg: Msg):
    """订阅选择"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        await data.status_add(msg.user, msg.platform, "订阅")
        content = ("阁下，请选择您希望订阅的服务：\n"
                   "活动:回复'活动'，当有新活动时，我将第一时间提醒您\n"
                   "早上好:回复'早上好'，订阅每日晨间问候语音\n"
                   "晚安:回复'晚安'，订阅每晚睡前安眠语音\n"
                   "UP主:回复UP主昵称，订阅对应B站UP的更新提醒。")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_订阅_回答")
async def subscribe_subscribe_answer(msg: Msg):
    """订阅选择"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    sub = Msg.content_join(msg.content).strip()
    if sub == "活动":
        await data.subscribe_data(user, "activity", "活动提醒")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
        await data.status_delete(msg.user, msg.platform, "订阅")
    elif sub == "早上好":
        await data.subscribe_data(user, "morning", "枣尚耗~")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
        await data.status_delete(msg.user, msg.platform, "订阅")
    elif sub == "晚安":
        await data.subscribe_data(user, "evening", "晚安啦~")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
        await data.status_delete(msg.user, msg.platform, "订阅")
    else:
        msg1 = Msg(
            platform="BILI",
            event="发送",
            kind=f"私聊搜索",
            content=f"{sub}|bili_user"
        )
        response = await future.wait(msg1.num, "[消息]用户搜索超时")
        if not response:
            content = "经过一番侦察，未能找到与此昵称匹配的UP主。或许您可以尝试换个昵称再次查询？"
        else:
            id = response[0].get("mid")
            name = response[0].get("uname")
            sign = response[0].get("usign")
            fans = response[0].get("fans")
            video = response[0].get("videos")
            content = (f"阁下，请确认以下信息无误，回复'确认'以完成订阅，或回复'取消'以中止：\n"
                       f"ID:{id}\n"
                       f"昵称:{name}\n"
                       f"签名:{sign}\n"
                       f"粉丝数:{fans}\n"
                       f"视频数:{video}")
            await data.status_add(msg.user, msg.platform, "up", f"{user}|{id}|{name}")
            await data.status_delete(msg.user, msg.platform, "订阅")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

@monitor_adapter("/订阅_活动")
async def subscribe_activity(msg: Msg):
    """订阅活动提醒"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        await data.subscribe_data(user, "activity", "活动提醒")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
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
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        await data.subscribe_data(user, "morning", "枣尚耗~")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
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
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        await data.subscribe_data(user, "evening", "晚安啦~")
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
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
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
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
                content = "经过一番侦察，未能找到与此昵称匹配的UP主。或许您可以尝试换个昵称再次查询？"
            else:
                id = response[0].get("mid")
                name = response[0].get("uname")
                sign = response[0].get("usign")
                fans = response[0].get("fans")
                video = response[0].get("videos")
                content = (f"阁下，请确认以下信息无误，回复'确认'以完成订阅，或回复'取消'以中止：\n"
                           f"ID:{id}\n"
                           f"昵称:{name}\n"
                           f"签名:{sign}\n"
                           f"粉丝数:{fans}\n"
                           f"视频数:{video}")
                await data.status_add(msg.user, msg.platform, "up", f"{user}|{id}|{name}")
        else:
            content = "格式似乎有误，阁下。正确的形式应为'/订阅,赵小爽729'类似格式"
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
    info = await data.status_check(msg.user, msg.platform, "up")
    user, id, name = info.split("|")
    await data.status_delete(msg.user, msg.platform, "up")
    if Msg.content_join(msg.content) == "确认":
        await data.subscribe_up(user, id, name)
        content = "订阅已生效，阁下。我会在适当的时候为您呈上最新情报。"
    else:
        content = "订阅已取消，期待您的下次使用。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/订阅_列表")
async def subscribe_list(msg: Msg):
    """订阅列表"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        content = "阁下，这是您当前的订阅清单，请输入对应序号以取消订阅\n"
        content += await data.subscribe_check(user)
        await data.status_add(msg.user, msg.platform, "订阅取消")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def subscribe_list_judge(msg: Msg):
    """订阅清单序号判断"""
    try:
        user = await data.status_lr5921_get(msg.user, msg.platform)
        id = int(Msg.content_join(msg.content))
        content = await data.subscribe_delete(user, id)
        if content.startwith("已取消"):
            return True
        return False
    except ValueError:
        return False


@monitor_adapter("/订阅_列表_取消")
async def subscribe_list_delete(msg: Msg):
    """订阅列表"""
    content = "订阅已取消，期待您的下次使用。"
    await data.status_delete(msg.user, msg.platform, "订阅取消")
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
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
        if len(id) == 2:
            id = id[1].strip()
            try:
                id = int(id)
                content = await data.subscribe_delete(user, id)
            except ValueError:
                content = "格式似乎有误，阁下。正确的形式应为 /订阅删除,1 这样的格式，请您再试一次。"
        else:
            content = "格式似乎有误，阁下。正确的形式应为 /订阅删除,1 这样的格式，请您再试一次。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
