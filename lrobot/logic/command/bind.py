"""绑定平台"""

import time
import hashlib

from logic import data
from message.handler.msg import Msg
from config import storage, monitor_adapter


bind_list = storage.setdefault("bind_list", {})


@monitor_adapter("/系统_绑定")
async def bind_platform(msg: Msg):
    """平台绑定 qq"""
    info = await data.status_check(msg.user, "qq")
    if info:
        content = f"当前平台已绑定 QQ: {info}"
    else:
        timestamp = time.time()
        code = hashlib.sha256(msg.seq.encode() + str(int(timestamp * 1000)).encode()).hexdigest()[:6]

        content = f"请将整条消息复制至 LR5921(QQ) 处 {code},五分钟有效"
        bind_list[msg.user] = (code, timestamp + 300, msg.platform)
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


@monitor_adapter("/系统_绑定_验证")
async def bind_qq(msg: Msg):
    """平台绑定确认"""
    content = "绑定失败，请确认完整复制了验证消息且在有效期内"

    for user, (code, expire_time, platform) in list(bind_list.items()):
        if Msg.content_pattern_contains(msg.content, str(code)) and time.time() < expire_time:
            del bind_list[user]
            info = await data.status_check(msg.user, platform)
            if info:
                content = f"当前 QQ 已绑定平台: {info}"
            else:
                await data.status_add(user, "qq", msg.user)
                await data.status_add(msg.user, platform, user)
                content = "绑定成功"
            break
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
