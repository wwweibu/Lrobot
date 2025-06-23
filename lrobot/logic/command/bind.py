import time
from message.handler.msg import Msg
# TODO 绑定回复
async def bind_platform(msg: Msg):
    kind = msg.kind[:2]
    timestamp = int(time.time() * 1000)
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=f"请在对应平台输入验证码{timestamp}",
        group=msg.group,
    )