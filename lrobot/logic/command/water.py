"""水群"""

import time
import datetime

from config import config, path
from message.handler.msg import Msg

count = 0
last_send_time = 0.0


async def water_send(msg: Msg):
    """水群"""
    global count, last_send_time
    if msg.kind != "群聊接收":
        return
    if msg.group != config["public"]["水群"][0]:
        return
    count += 1
    now = time.time()

    if count >= 120 and now - last_send_time >= 3600:
        fixed_time = datetime.datetime(2025, 11, 1, 16, 0, 0)
        now_time = datetime.datetime.now()
        time_diff = fixed_time - now_time
        total_hours = time_diff.total_seconds() / 3600
        Msg(
            platform=msg.platform,
            kind=f"群聊发送",
            event="发送",
            content=f"欢迎找小推[at:1326016706]或小推·人机版(me)入会。可以不用加好友直接私聊我，发送'/入会'\n对协会活动有疑问也可以找我发送'/常见问题'\n内阁招新还有{total_hours:.2f}h就结束了，关注群置顶公告，走过路过不要错过。\n注：本推仅支持固定指令，智能问答请找另一个推[图片:{path / 'storage/file/command/water.jpg'}]",
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
