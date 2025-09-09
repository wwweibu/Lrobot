"""用户相关"""

import asyncio

from .status import status_check
from .firefly import firefly_judge
from message.handler.msg import Msg
from config import config, future, database_query, loggers


async def user_identify(user, platform):
    """确认用户身份，未认证/社员/用户组"""
    if platform != "LR5921":
        information = await status_check(user, "qq")
        if not information:
            return []
        user = information

    result = []
    for identity, numbers in config["private"].items():
        if user in numbers:
            result.append(identity)
    # 如果匹配到任意一个身份，则添加 "内阁"
    if result:
        result.append("内阁")

    test_member = await firefly_judge(user)
    if test_member:
        result.append("测试员")

    member = await user_member_judge(user)
    if member:
        result.append("社员")
    return result


async def user_member_judge(qq):
    """判断用户是否为社员"""
    query = "SELECT 1 FROM user_information WHERE qq = %s LIMIT 1"
    result = await database_query(query, (qq,))
    return 1 if result else 0


async def user_nickname_get(user):
    """获取用户昵称"""
    msg = Msg(
        platform="LR5921",
        event="发送",
        kind="私聊昵称",
        user=user
    )
    try:
        _future = future.get(msg.num)
        response = await asyncio.wait_for(_future, timeout=20)
        return response
    except asyncio.TimeoutError:
        loggers["message"].error(
            f"昵称获取超时 | 用户: {user}", extra={"event": "消息处理"},
        )
        return None


async def user_codename_change(codename):
    """根据代号获取 QQ"""
    query = "SELECT qq FROM user_information WHERE codename = %s LIMIT 1"
    result = await database_query(query, (codename,))
    if result:
        return result[0]["qq"]
    return None


async def user_qq_transform(user, platform):
    """转换为 QQ 号"""
    if platform == "LR5921":
        return user
    information = await status_check(user, "qq")
    if information:
        return information
    return None
