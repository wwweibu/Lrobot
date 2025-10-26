"""水群"""

import time
import datetime

from config import config, path
from message.handler.msg import Msg

count = 0
last_send_time = 0

async def water_send(msg: Msg):
    """水群"""
    global count, last_send_time
    if msg.group != config["public"]["水群"][0]:
        return
    count += 1
    now = time.time()

    if count >= 100 and now - last_send_time >= 1800:
        Msg(
            platform=msg.platform,
            kind=f"群聊发送",
            event="发送",
            content=f"欢迎找小推[at:1326016706]或小推·人机版(me)入会。可以不用加好友直接私聊我，发送\n\n/入会\n\n对协会活动有疑问也可以找我发送'/常见问题'\n注意去掉引号，保留/\n注：仅支持固定指令，智能问答请找另一个推[图片:{path / 'storage/file/command/water.jpg'}]",
            seq=msg.seq,
            group=config["public"]["水群"][0]
        )
        count = 0
        last_send_time = now


async def water_send_evening():
    """每天0点发送语音"""
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    storage_path = path / "storage/file/command"
    record = storage_path / f"evening_{yesterday}.wav"
    if not record.exists():
        return

    Msg(
        platform="LR5921",
        kind="群聊发送",
        event="发送",
        group=config["public"]["水群"][0],
        content=f"[语音:{record}]"
    )
