"""订阅相关"""

from logic import data
from message.handler.msg import Msg


async def subscribe_list(msg: Msg):
    """查询当前订阅"""
    content = ("可订阅项目:\n"
               "/订阅花火:获取每日定时原音早上好项目\n"
               "注:未绑定LR5921无法使用")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def subscribe_sparkle(msg: Msg):
    """订阅花火"""
    user = await data.user_qq_transform(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        await data.subscribe_sparkle(user)
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
