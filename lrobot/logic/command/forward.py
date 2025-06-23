from message.handler.msg import Msg

async def forward_all(msg: Msg):
    kind = msg.kind[:2]
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content="无效的指令，请使用 /帮助",
        group=msg.group,
    )
    Msg(
        robot="LR5921",
        kind="私聊发送文字",
        event="发送",
        source="663748426",
        seq=msg.seq,
        content="来自" + msg.source + "的消息" + msg.content,
        group=msg.group,
    )