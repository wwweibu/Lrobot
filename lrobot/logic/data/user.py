# 用户相关
import time
import asyncio
from .status import check_status
from message.handler.msg import Msg
from .user_test import judge_user_test_group
from config import config,query_database,future

async def identify_user(source,platform):
    """确认用户身份，未认证/社员/用户组"""
    if platform != "LR5921":
        information = await check_status(source,"qq")
        if not information:
            return []
        source = information

    result = []
    for identity, numbers in config["私聊"].items():
        if source in numbers:
            result.append(identity)
    # 如果匹配到任意一个身份，则添加 "内阁"
    if result:
        result.append("内阁")
    test_member = await judge_user_test_group(source)
    if test_member:
        result.append("测试员")
    member = await judge_user_member(source)
    if member:
        result.append("社员")
    return result


async def judge_user_member(source):
    """判断用户是否为社员"""
    query = "SELECT 1 FROM user_information WHERE qq = %s LIMIT 1"
    result = await query_database(query, (source,))
    return 1 if result else 0


async def get_user_nickname(source):
    """获取用户昵称"""
    seq = f"{source}_{int(time.time() * 1000)}"
    Msg(
        robot="LR5921",
        kind="私聊获取信息",
        event="发送",
        source="663748426",
        seq=seq,
        content=source,
    )
    try:
        _future = future.get(seq)
        response = await asyncio.wait_for(_future, timeout=20)
        data = response.json().get("data", {})
        return data.get("nickname",{})
    except asyncio.TimeoutError:
        raise Exception(f"昵称获取超时 | 用户: {source}")


async def change_codename_to_user(codename):
    """根据代号获取 QQ"""
    query = "SELECT qq FROM user_information WHERE codename = %s LIMIT 1"
    result = await query_database(query, (codename,))
    if result:
        return result[0]["qq"]
    return None
