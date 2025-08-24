"""测试群相关"""

import re

from logic import data
from message.handler.msg import Msg


async def firefly_in(msg: Msg):
    """入群更新 user_test 表"""
    await data.firefly_update()


async def firefly_set(msg: Msg):
    """设置测试员密码"""
    user = next((item["data"]["qq"] for item in msg.content if item["type"] == "at"), None)
    content = msg.content[1]["data"]["text"]
    parts = re.split(r"[，,]", content)
    name = parts[1].strip()
    password = await data.firefly_password_update(user, name)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"群聊发送",
        content=f"[at:{user}]你的账号为{name},密码为{password},请登录 whumystery.cn/cmd,并进入 whumystery.cn/firefly 提交你的每日任务",
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
