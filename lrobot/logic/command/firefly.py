"""测试群相关"""

import re

from logic import data
from config import monitor_adapter
from message.handler.msg import Msg


@monitor_adapter("/工具_测试群入群")
async def firefly_in(msg: Msg):
    """入群更新 user_test 表"""
    await data.firefly_update()
    content = f"[at:{msg.user}]新人要什么头衔?"
    await data.status_add(msg.user, msg.platform, "头衔")
    Msg(
        platform=msg.platform,
        event="发送",
        kind="群聊发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/工具_测试群头衔")
async def firefly_title(msg: Msg):
    """入群第一句设置成头衔"""
    await data.status_delete(msg.user, msg.platform, "头衔")
    Msg(
        platform=msg.platform,
        event="发送",
        kind="群聊头衔",
        content=Msg.content_join(msg.content),
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return Msg.content_join(msg.content)

@monitor_adapter("/工具_测试群密码")
async def firefly_set(msg: Msg):
    """设置测试员密码"""
    identity_list = await data.user_identify(msg.user, msg.platform)
    if "微部" not in identity_list:
        content = "不许偷偷设置密码哦"
    else:
        user = next((item["data"]["qq"] for item in msg.content if item["type"] == "at"), None)
        content = msg.content[1]["data"]["text"]
        parts = re.split(r"[，,]", content)
        name = parts[1].strip()
        password = await data.firefly_password_update(user, name)
        content = f"[at:{user}]你的账号为{name},密码为{password},请在 whumystery.cn/cmd 登录,之后可以进入 whumystery.cn/firefly 提交你的每日任务"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"群聊发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content
