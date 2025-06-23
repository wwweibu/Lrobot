from message.handler.msg import Msg


async def welcome_user(msg: Msg):
    kind = msg.kind[:2]
    Msg(
        robot="LR232",
        kind=f"{kind}回复推送",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content="这里是 LRobot，武大推协开发的多平台聊天工具，使用'/帮助'获取更多功能",
        group=msg.group,
    )
