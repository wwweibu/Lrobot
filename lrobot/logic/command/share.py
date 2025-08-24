"""分享"""

from message.handler.msg import Msg


async def share_text(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="分享成功！",
        user=msg.user,
        group=msg.group,
    )
