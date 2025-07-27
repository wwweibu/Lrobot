"""B 站消息获取"""

import re
import json
import time

from message.handler.msg import Msg
from .bili_dispatch import request_deal
from config import config, loggers, monitor_adapter

adapter_logger = loggers["adapter"]


async def bili_receive(interval=None):
    """私聊接收"""
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions"
    params = {
        **(
            {"begin_ts": int((time.time() - interval) * 1_000_000)}
            if interval is not None
            else {}
        ),
    }  # 指定开始时间
    response = await request_deal(url, "get", params, "私聊接收")

    msg_list = response["data"]["session_list"]
    if not isinstance(msg_list, list):  # 无消息
        return
    for msg in msg_list:
        if msg["unread_count"] == 0:
            pass
        elif msg["unread_count"] == 1:
            await bili_msg_read(msg["talker_id"])
            await bili_msg_deal(msg["last_msg"])
        else:
            await bili_msg_read(msg["talker_id"])
            msg_get_list = await bili_msg_get(msg["ack_seqno"], user=msg["talker_id"])
            for msg_get in msg_get_list:
                await bili_msg_deal(msg_get)


async def bili_msg_get(seq, num=None, user=None):
    """私聊消息获取"""
    url = "https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs"
    params = {
        "talker_id": user,
        "session_type": 1,
        "size": 20,
        "begin_seqno": seq,  # 指定开始序号
    }
    response = await request_deal(url, "get", params, "私聊消息获取")
    return response["data"]["messages"]


async def bili_msg_read(user):
    """私聊已读"""
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack"
    params = {
        "talker_id": user,
        "session_type": 1,
        "csrf_token": config["BILI_JCT"],
        "csrf": config["BILI_JCT"],
    }
    await request_deal(url, "post", params, "私聊已读")


@monitor_adapter("BILI")
async def bili_msg_deal(msg):
    """消息处理，对应私信主体对象"""
    content = json.loads(msg["content"])
    kind = "私聊接收"
    if msg["msg_type"] == 1:
        content = content["content"]
        parts = re.split(r"(\[[^\[\]]+])", content)
        result = []
        for part in parts:
            if not part:
                continue
            if re.fullmatch(r"\[[^\[\]]+]", part):
                result.append({"type": "image", "data": {"summary": part}})
            else:
                result.append({"type": "text", "data": {"text": part}})
        content = result

    elif msg["msg_type"] == 2 or msg["msg_type"] == 6:

        file = f"{msg['msg_key']}.{content['imageType']}"
        content = [
            {
                "type": "image",
                "data": {
                    "file": file,
                    "url": content["url"],
                    "original": content["original"],
                    "size": content["size"],
                    "width": content["width"],
                    "height": content["height"],
                },
            }
        ]

    elif msg["msg_type"] == 5:
        kind = "私聊撤回"
        content = Msg.content_disjoin(
            f"{msg['sender_uid']} 撤回了 {msg['sender_uid']} 的消息 - "
        )
        content += Msg.content_disjoin(content)

    elif msg["msg_type"] == 7:
        source_type_map = {
            2: "相簿",
            3: "纯文字",
            5: "视频",
            6: "专栏",
            7: "番剧",
            8: "音乐",
            9: "国产动画",
            10: "图片",
            11: "动态",
            16: "番剧",
            17: "番剧",
        }
        type = source_type_map.get(content["source"], "未知类型")
        content_value = content.pop("title", "")
        new_content = {"prompt": content_value, "type": type, **content}
        content = [{"type": "json", "data": {"data": new_content}}]

    elif msg["msg_type"] == 10:
        content_value = content.pop("text", "")
        new_content = {"prompt": content_value, "type": "系统通知", **content}
        content = [{"type": "json", "data": {"data": new_content}}]

    elif msg["msg_type"] == 13:
        content_value = content.pop("title", "")
        new_content = {"prompt": content_value, "type": "图片分享", **content}
        content = [{"type": "json", "data": {"data": new_content}}]

    elif msg["msg_type"] == 14:
        content_value = content.pop("title", "")
        new_content = {"prompt": content_value, "type": "视频分享", **content}
        content = [{"type": "json", "data": {"data": new_content}}]
    else:
        adapter_logger.error(
            f"[BILI] 未定义的消息类型 -> {msg}", extra={"event": "消息接收"}
        )
        return
    Msg(
        platform="BILI",
        kind=kind,
        event="处理",
        seq=msg["msg_key"],
        content=content,
        user=msg["sender_uid"]
    )
