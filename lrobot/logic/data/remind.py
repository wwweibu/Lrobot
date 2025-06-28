from message.handler.msg import Msg
async def remind_send():
    Msg(
        robot="LR5921",
        kind="私聊文字消息",
        event="处理",
        source="663748426",
        seq="12342",
        content="/消息提醒"
    )