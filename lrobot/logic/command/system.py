from message.handler.msg import Msg

async def system_remind(msg:Msg):
    kind = msg.kind[:2]
    # content = "小推提醒你，找小推了解更多协会咨询和玩法"
    # Msg(
    #     robot=msg.robot,
    #     kind=f"{kind}发送文字",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content=content,
    #     group=msg.group,
    # )

async def system_get_nickname():
    pass