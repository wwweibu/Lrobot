"""用户相关"""

import asyncio
from datetime import datetime, timedelta

from .firefly import firefly_judge
from message.handler.msg import Msg
from config import config, future, database_query, database_update
from .status import status_lr5921_get, status_delete, status_add, status_user_check



async def user_identify(user, platform):
    """确认用户身份，未认证/社员/用户组"""
    qq = await status_lr5921_get(user, platform)
    if not qq:
        return []

    result = []
    for identity, numbers in config["private"].items():
        if qq in numbers:
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


async def user_nickname_transform(user, platform, is_send=None):
    """用户昵称转换"""
    qq = await status_lr5921_get(user, platform)
    if not qq:
        return None
    query = "SELECT nickname, created_at FROM user_nickname WHERE user = %s LIMIT 1"
    result = await database_query(query, (qq,))
    if result:
        nickname = result[0]["nickname"]
        created_at = result[0]["created_at"]
        if datetime.now() - created_at < timedelta(days=3):
            return nickname
    if is_send:  # 发送不能调用 user_nickname_get
        return None
    msg = Msg(
        platform="LR5921",
        event="发送",
        kind="私聊昵称",
        user=qq
    )
    try:
        nickname = await future.wait(msg.num)
    except asyncio.TimeoutError:
        return None
    if not nickname:
        return None
    update_sql = """
            INSERT INTO user_nickname (user, nickname, created_at)
            VALUES (%s, %s, NOW()) AS new
            ON DUPLICATE KEY UPDATE
                nickname = new.nickname,
                created_at = new.created_at
        """
    await database_update(update_sql, (qq, nickname))

    return nickname


async def user_codename_change(codename):
    """根据代号获取 QQ"""
    query = "SELECT qq FROM user_information WHERE codename = %s LIMIT 1"
    result = await database_query(query, (codename,))
    if result:
        return result[0]["qq"]
    return None


async def user_codename_qq_change(user):
    """根据 qq 获取代号"""
    query_code = "SELECT codename FROM user_information WHERE qq = %s LIMIT 1"
    result = await database_query(query_code, (user,))
    if result:
        return result[0]["codename"]
    return None


async def user_name(user, platform, is_send=None):
    """转换用户，代号>昵称>qq>原 id"""
    qq = await status_lr5921_get(user, platform)
    if not qq:
        return user
    name = await user_codename_qq_change(qq)
    if name:
        return name
    name = await user_nickname_transform(user, platform, is_send)
    if name:
        return name
    return user


async def user_register(user_data):
    """入会"""
    await database_update(
        """
        INSERT INTO user_information (
            qq, codename, name, grade, gender,
            major, student_id, phone, political_status, hometown
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        ) AS new
        ON DUPLICATE KEY UPDATE
            codename = new.codename,
            name = new.name,
            grade = new.grade,
            gender = new.gender,
            major = new.major,
            student_id = new.student_id,
            phone = new.phone,
            political_status = new.political_status,
            hometown = new.hometown
        """,
        (
            user_data["qq"],
            user_data["codename"],
            user_data["name"],
            user_data["grade"],
            user_data["gender"],
            user_data["major"],
            user_data["student_id"],
            user_data["phone"],
            user_data["political_status"],
            user_data["hometown"],
        ),
    )
