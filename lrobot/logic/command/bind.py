import time
from message.handler.msg import Msg
from logic import data

bind_list = {}
async def bind_platform(msg: Msg):
    """平台绑定 qq"""
    kind = msg.kind[:2]
    info = await data.check_status(msg.source,"qq")
    if info:
        content = f"当前平台已绑定 QQ: {info}"
    else:
        timestamp = msg.seq + int(time.time() * 1000)
        content = f"请将整条消息复制至 LR5921(QQ) 处 {timestamp},五分钟有效"
        bind_list[msg.source] = (timestamp,time.time() + 300,msg.robot)
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


async def bind_check(msg:Msg):
    """平台绑定确认"""
    content = "绑定失败，请确认完整复制了验证消息且在有效期内"
    kind = msg.kind[:2]
    for source, (ts, expire_time,platform) in list(bind_list.items()):
        if str(ts) in msg.content and time.time() < expire_time:
            del bind_list[source]
            await data.add_status(source,"qq",msg.source)
            await data.add_status(msg.source,platform,source)
            content = "绑定成功"
            break
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
