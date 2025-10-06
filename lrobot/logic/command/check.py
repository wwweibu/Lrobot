"""定期检测连接"""

import httpx
import docker

from config import loggers
from message.handler.msg import Msg

COMMAND_CONTAINER = "command"


async def check_net():
    """测试网络"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("https://whumystery.cn/test")
            if resp.status_code == 200 and resp.text.strip() == "Hello World!":
                loggers["message"].debug("[网络检查]连接成功", extra={"event": "容器处理"})
                return
            else:
                content = f"检测失败-> {resp.status_code}: {resp.text[:50]}"
                loggers["message"].error(f"[网络检查]连接失败-> {resp.status_code}: {resp.text[:50]}",
                                         extra={"event": "容器处理"})
    except Exception as e:
        content = f"检测失败-> {e}"
        loggers["message"].error(f"[网络检查]连接失败-> {e}",
                                 extra={"event": "容器处理"})
    if content:
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            content=content,
            user="663748426",
        )


async def check_restart(msg: Msg):
    """重启容器"""
    client = docker.from_env()
    container = client.containers.get("command")
    container.restart()
    loggers["message"].debug(f"[容器重启]重启成功",
                             extra={"event": "容器处理"})
    content = "重启成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content
