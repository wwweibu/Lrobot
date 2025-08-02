"""绑定平台"""

import time
import hashlib

from logic import data
from config import config
from message.handler.msg import Msg

bind_list = config.load("bind_list")


async def platform_bind(msg: Msg):
    """平台绑定 qq"""
    kind = msg.kind[:2]
    info = await data.status_check(msg.user, "qq")
    if info:
        content = f"当前平台已绑定 QQ: {info}"
    else:
        seq_hash = hashlib.md5(msg.seq.encode()).hexdigest()[:6]
        timestamp = f"{seq_hash}{int(time.time() * 1000)}"
        content = f"请将整条消息复制至 LR5921(QQ) 处 {timestamp},五分钟有效"
        bind_list[msg.user] = (timestamp, time.time() + 300, msg.platform)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{kind}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def qq_bind(msg: Msg):
    """平台绑定确认"""
    content = "绑定失败，请确认完整复制了验证消息且在有效期内"
    kind = msg.kind[:2]
    for user, (ts, expire_time, platform) in list(bind_list.items()):
        if Msg.content_pattern_contains(msg.content, str(ts)) and time.time() < expire_time:
            del bind_list[user]
            await data.status_add(user, "qq", msg.user)
            await data.status_add(msg.user, platform, user)
            content = "绑定成功"
            break
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{kind}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
