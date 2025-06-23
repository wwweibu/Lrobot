from message.handler.msg import Msg

# TODO 积分相关
async def point_query(msg: Msg):
    kind = msg.kind[:2]
    content = "当前积分:3\n\n积分排行\n1.令狐二中\n2.微步"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


async def point_award_query(msg: Msg):
    kind = msg.kind[:2]
    content = "当前奖品:\n1.社刊 数量:10 积分:100\n2.桌游 数量:20 积分:50"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
