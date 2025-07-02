import re
from logic import data
from message.handler.msg import Msg


async def firefly_in(msg: Msg):
    """入群更新 user_test 表"""
    await data.update_user_test_group()


async def firefly_set(msg:Msg):
    """设置测试员密码"""
    match = re.match(r"\[at:(\d+)\](.+)", msg.content)
    source = match.group(1)
    content_list = [p.strip() for p in re.split(r"[，,]", match.group(2).strip()) if p.strip()]
    name = content_list[1]
    print(source,name)
    password = await data.update_user_test_group_password(source,name)
    print(12345)
    Msg(
        robot=msg.robot,
        kind=f"群聊发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=f"[at:{source}]你的账号为{name},密码为{password},请登录 whumystery.cn/cmd,并进入 whumystery.cn/firefly 提交你的每日任务",
        group=msg.group,
    )



