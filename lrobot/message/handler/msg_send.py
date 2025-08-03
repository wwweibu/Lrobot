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
                msg.content, kind=msg.kind, user=msg.user, group=msg.group
            )
        elif msg.platform == "WECHAT":
            await wechat_dispatch(msg.content, user=msg.user, seq=msg.seq)
        elif msg.platform == "BILI":
            await bili_dispatch(msg.content, user=msg.user, num=msg.num)
        elif msg.platform == "LR232":
            match = re.search(r"发送\*(\d+)", msg.event)
            msg_seq = int(match.group(1)) if match else 1
            await lr232_dispatch(msg.content, msg.kind, msg.user, msg.group, msg.num, msg.seq, msg_seq)
    elif msg.kind.endswith("撤回"):
        if msg.platform == "LR5921":
            await lr5921_withdraw(msg.seq)
        elif msg.platform == "BILI":
            await bili_withdraw(msg.seq, user=msg.user)
        elif msg.platform == "LR232":
            if msg.kind.startswith("私聊"):
                await lr232_withdraw(msg.seq, msg.user, msg.seq)
            else:
                await lr232_withdraw(msg.seq, msg.group, msg.seq)
    elif msg.kind.endswith("签到"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("群聊"):
                await lr5921_sign_in(msg.group)
    elif msg.kind.endswith("戳戳"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                await lr5921_poke(msg.user)
            else:
                await lr5921_poke(msg.user, msg.group)
    elif msg.kind.endswith("分享"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                await lr5921_share(msg.num, user=msg.user)
            else:
                await lr5921_share(msg.num, group=msg.group)
    elif msg.kind.endswith("状态设置"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                status = Msg.content_join(msg.content).split("|")
                status += [""] * (4 - len(status))
                id = None
                if status[0] == "自定义":
                    id = [k for k, v in config["emojis"].items() if v == status[2]]
                state = config["online_status"][status[0]].split("|")
                if not state:
                    raise Exception(f"状态不存在 | 状态: {msg.content}")
                await lr5921_status_set(state[0], state[1], status[1], id, status[3])
    elif msg.kind.endswith("回应"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("群聊"):
                await lr5921_echo(msg.seq, msg.content)
    elif msg.kind.endswith("签名"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                await lr5921_signature(Msg.content_join(msg.content))
    elif msg.kind.endswith("消息获取"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                await lr5921_msg_get(msg.num, msg.seq)
    elif msg.kind.endswith("收藏"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                content_list = Msg.content_join(msg.content).split("|")
                await lr5921_favor(content_list[0], content_list[1])
    elif msg.kind.endswith("状态获取"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("私聊"):
                await lr5921_status_get(msg.num, msg.user)
    elif msg.kind.endswith("精华"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("群聊"):
                await lr5921_essence(msg.seq, Msg.content_join(msg.content))
    elif msg.kind.endswith("头衔"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("群聊"):
                await lr5921_title(msg.user, msg.group, Msg.content_join(msg.content))
    elif msg.kind.endswith("列表"):
        if msg.platform == "LR5921":
            if msg.kind.startswith("群聊"):
                await lr5921_list(msg.num, msg.group)
    elif msg.kind.endswith("卡片"):
        if msg.platform == "LR5921":
            content_list = Msg.content_join(msg.content).split("|")
            await lr5921_card(msg.num, content_list[0], content_list[1], content_list[2], content_list[3],
                              content_list[4])
    elif msg.kind.endswith("测试"):
        await bili_test(Msg.content_join(msg.content))
