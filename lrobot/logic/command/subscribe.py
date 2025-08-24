"""订阅相关"""

from logic import data
from message.handler.msg import Msg


async def subscribe_list(msg: Msg):
    """查询当前订阅"""
    status = await data.status_check(msg.user)
    if "订阅" in status:
        content = "当前订阅：天气。\n可订阅：无。"
    else:
        content = "当前订阅：无。\n可订阅：天气。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def subscribe_weather(msg: Msg):
    """订阅天气"""
    status = await data.status_check(msg.user)
    if "订阅" in status:
        content = "已订阅天气。"
    else:
        await data.status_add(msg.user, "订阅")
        content = "订阅成功。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def subscribe_test(msg: Msg):
    """订阅测试"""
    status = await data.status_check(msg.user)
    if "订阅" in status:
        content = "早上好啊，今天也是一个大晴天呢，愿你度过美好的一天"
    else:
        content = "早上好啊，愿你度过美好的一天"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
