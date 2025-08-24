"工具"

from logic import data
from message.handler.msg import Msg


async def tool_list(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="当前工具：待办存储，输入'/待办'获取待办",
        user=msg.user,
        group=msg.group,
    )


async def tool_schedule(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="当前待办:完成侦探扮演任务1",
        user=msg.user,
        group=msg.group,
    )
