"""消息发送"""

import re

from message.adapter import *
from message.handler.msg import Msg

msg_logger = loggers["message"]


async def msg_send(msg: Msg):
    """消息发送分配器"""
    msg_logger.info(
        f"⌈{msg.platform}⌋: {msg.kind} -> {Msg.content_join(msg.content) if Msg.content_join(msg.content) else msg.kind}",
        extra={"event": "消息发送"},
    )
    if msg.kind.endswith("发送"):
        if msg.platform == "LR5921":
            await lr5921_dispatch(
                msg.content, kind=msg.kind, user=msg.user, group=msg.group, num=msg.num
            )
        elif msg.platform == "LR232":
            match = re.search(r"发送\*(\d+)", msg.event)
            order = int(match.group(1)) if match else 1
            await lr232_dispatch(msg.content, msg.kind, msg.user, msg.group, msg.num, msg.seq, order)
        elif msg.platform == "BILI":
            await bili_dispatch(msg.content, user=msg.user, num=msg.num)
        elif msg.platform == "WECHAT":
            await wechat_dispatch(msg.content, user=msg.user, seq=msg.seq)
    elif msg.kind.endswith("消息获取"):
        if msg.platform == "LR5921":
            await lr5921_msg_get(msg.seq, num=msg.num)
        elif msg.platform == "BILI":
            await bili_msg_get(msg.seq, user=msg.user)
    elif msg.kind.endswith("文件上传"):
        if msg.platform == "LR232":
            if msg.kind.startswith("私聊"):
                url = f"https://api.sgroup.qq.com/v2/users/{msg.user}/files"
            else:
                url = f"https://api.sgroup.qq.com/v2/groups/{msg.group}/files"
            file = msg.content[0].get("data", "").get("file")
            await lr232_file_upload(file, url=url)
        elif msg.platform == "BILI":
            await bili_file_upload(msg.content[0].get("data", "").get("file"))
        elif msg.platform == "WECHAT":
            msg_type = msg.content[0].get("type")
            if msg_type == "record":
                msg_type = "voice"
            await wechat_file_upload(msg.content[0].get("data", "").get("file"), msg_type)
    elif msg.kind.endswith("文件下载"):
        if msg.platform == "LR5921":
            file = msg.content[0]["data"].get("file")
            file_path = msg.content[0]["data"].get("file_path")
            await lr5921_file_download(file, file_path)
        elif msg.platform == "WECHAT":
            file = msg.content[0]["data"].get("file")
            file_path = msg.content[0]["data"].get("file_path")
            await wechat_file_download(file, file_path)
    elif msg.kind.endswith("撤回"):
        if msg.platform == "LR5921":
            await lr5921_withdraw(msg.seq, kind=msg.kind)
        elif msg.platform == "LR232":
            user = msg.user if msg.kind.startswith("私聊") else msg.group
            await lr232_withdraw(msg.seq, user, msg.kind)
        elif msg.platform == "BILI":
            await bili_withdraw(msg.seq, user=msg.user)
    elif msg.kind.endswith("签名"):
        if msg.platform == "LR5921":
            await lr5921_signature(Msg.content_join(msg.content))
        elif msg.platform == "BILI":
            await bili_signature(Msg.content_join(msg.content))
    elif msg.platform == "BILI":
        if msg.kind.endswith("直播开启"):
            await bili_live_start(msg.num)
        elif msg.kind.endswith("直播标题"):
            info = Msg.content_join(msg.content)
            if "|" in info:
                title, file = info.split("|", 2)
            else:
                title, file = info, None
            await bili_live_title(title, file)
        elif msg.kind.endswith("直播公告"):
            await bili_live_notice(Msg.content_join(msg.content))
        elif msg.kind.endswith("直播关闭"):
            await bili_live_stop()
        elif msg.kind.endswith("粉丝获取"):
            await bili_fan_get()
    elif msg.platform == "LR5921":
        if msg.kind.endswith("状态"):
            status = Msg.content_join(msg.content).split("|")
            if status[0] == "自定义":
                await lr5921_status(emoji=status[1], word=status[2])
            else:
                await lr5921_status(status[0], status[1])
        elif msg.kind.endswith("成员"):
            await lr5921_member(msg.num, msg.group)
        elif msg.kind.endswith("签到"):
            if msg.group:
                await lr5921_sign_in(msg.group)
        elif msg.kind.endswith("回应"):
            await lr5921_echo(msg.seq, Msg.content_join(msg.content))
        elif msg.kind.endswith("精华"):
            await lr5921_essence(msg.seq, Msg.content_join(msg.content))
        elif msg.kind.endswith("头衔"):
            if msg.group:
                await lr5921_title(msg.user, msg.group, Msg.content_join(msg.content))
