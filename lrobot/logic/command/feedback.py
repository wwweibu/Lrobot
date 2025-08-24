"""留言及反馈"""

from message.handler.msg import Msg


async def feedback_text(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="反馈成功！",
        user=msg.user,
        group=msg.group,
    )
