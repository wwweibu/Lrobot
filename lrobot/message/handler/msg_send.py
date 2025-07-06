import re
from config import config,loggers
from message.handler.msg import Msg
from message.adapter import *

msg_logger = loggers["message"]


async def msg_send(msg: Msg):
    msg_logger.info(
        f"⌈{msg.robot}⌋{msg.event}:{msg.kind}->{msg.content}",
        extra={"event": "消息发送"},
    )
    # TODO BILI 中私聊发送图文改为发送两条消息
    # if msg.robot == "BILIBILI":
    #     if msg.kind == "私聊发送文本":
    #         await bili_dispatch(msg.source, msg.content)
    if msg.robot == "LR232":
        match = re.search(r"发送\*(\d+)", msg.event)
        msg_seq = int(match.group(1)) if match else 1
        if msg.kind in [
            "私聊发送文字",
            "群聊发送文字",
            "私聊发送文件",
            "群聊发送文件",
            "私聊发送图文",
            "群聊发送图文",
        ]:
            await lr232_dispatch(
                msg.kind,
                msg.source,
                msg.group,
                msg.content,
                msg_id=msg.seq,
                msg_seq=msg_seq,
                files=msg.files,
            )
        elif msg.kind in ["私聊发送推送", "群聊发送推送"]:
            await lr232_dispatch(msg.kind, msg.source, msg.content, event_id=msg.seq)
        elif msg.kind in ["私聊撤回消息", "群聊撤回消息"]:
            await lr232_withdraw(msg.kind, msg.source, msg.group,msg.seq)
    elif msg.robot == "LR5921":
        if msg.kind in ["私聊发送文字","私聊发送文件","私聊发送图文"]:
            await lr5921_dispatch(msg.kind, msg.source, msg.content, msg.files)
        elif msg.kind in ["群聊发送文字","群聊发送文件","群聊发送图文"]:
            await lr5921_dispatch(msg.kind, msg.group, msg.content, msg.files)
        elif msg.kind == "私聊发送语音":
            await lr5921_dispatch_record(msg.kind, msg.source, msg.files)
        elif msg.kind == "群聊发送语音":
            await lr5921_dispatch_record(msg.kind, msg.group, msg.files)
        elif msg.kind == "私聊分享名片":
            await lr5921_get_share(user=msg.source, phone=msg.content)
        elif msg.kind == "群聊分享名片":
            await lr5921_get_share(group=msg.group)
        elif msg.kind == "私聊设置状态":
            status = msg.content.split("|")
            state = config["online_status"].get(status[0]).split("|")
            if not state:
                raise Exception(f"状态不存在|状态:{msg.content}")
            await lr5921_set_status(state[0], state[1], status[1])
        elif msg.kind == "私聊获取状态":
            await lr5921_get_status(msg.content)
        elif msg.kind == "私聊设置信息":
            info = msg.content.split("|")
            await lr5921_set_info(info[0], info[1], info[2])
        elif msg.kind == "私聊获取信息":
            await lr5921_get_info(msg.content,msg.seq)
        elif msg.kind == "群聊获取信息":
            await lr5921_get_group(msg.content,msg.seq)
        elif msg.kind in ["私聊撤回消息", "群聊撤回消息"]:
            await lr5921_withdraw(msg.seq)
        elif msg.kind in ["群聊转发消息"]:
            await lr5921_forward()
    elif msg.robot == "WECHAT":
        if msg.kind == "私聊发送文字":
            await wechat_dispatch(msg.source, msg.seq, msg.content)
