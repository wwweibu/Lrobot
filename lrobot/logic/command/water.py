"""水群"""

from config import config
from message.handler.msg import Msg

count = 0


async def water_send(msg: Msg):
    """水群"""
    global count
    if msg.group == config["public"]["水群"][0]:
        count += 1
    if count == 100:
        Msg(
            platform=msg.platform,
            kind=f"群聊发送",
            event="发送",
            content="欢迎找小推[at:1326016706]或小推·人机版(me)入会。可以不用加好友直接私聊我，发送'/入会'，注意去掉引号，保留'/'哦~\n对协会活动有疑问也可以找我发送'/常见问题'。\n注：仅支持固定指令",
            seq=msg.seq,
            group=config["public"]["水群"][0]
        )
