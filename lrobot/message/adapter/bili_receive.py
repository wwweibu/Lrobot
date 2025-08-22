"""BILI 消息接收"""
import re
import json
import time

from message.handler.msg import Msg
from .bili_dispatch import request_deal
from config import config, loggers, monitor_adapter
from logic import status_add, status_delete, status_check

adapter_logger = loggers["adapter"]


def sort_messages(msg_list):
    """重新排序消息列表"""
    non_withdraw, withdraw = [], []
    for m in reversed(msg_list):
        (withdraw if m["msg_type"] == 5 else non_withdraw).append(m)
    # 将非撤回消息放在前面，撤回消息放在后面
    return non_withdraw + withdraw

async def bili_receive(interval=None):
    """私聊接收"""
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions"
    params = {}
    if interval:
        params["begin_ts"] = int((time.time() - interval) * 1_000_000)
    response = await request_deal(url, "get", params, "私聊接收")

    msg_list = response.get("data", {}).get("session_list", [])
    if not isinstance(msg_list, list):  # 无消息
        return
    for msg in msg_list:
        if msg["unread_count"] == 0 and not interval:
            continue
        # 不直接提取消息，因为撤回消息不算数量（unread_count）
        await _bili_msg_read(msg["talker_id"])
        if not msg.get("ack_seqno"):
            continue
        msg_get_list = await bili_msg_get(msg["ack_seqno"], user=msg["talker_id"])
        for msg_get in sort_messages(msg_get_list):
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
    return response.get("data", {}).get("messages", [])


async def _bili_msg_read(user):
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
    mtype = msg.get("msg_type")
    if mtype == 1:
        content = content["content"]
        parts = re.split(r"(\[[^\[\]]+])", content)
        content = [
            {"type": "image", "data": {"summary": part}} if re.fullmatch(r"\[[^\[\]]+]", part)
            else {"type": "text", "data": {"text": part}}
            for part in parts if part
        ]

    elif mtype in (2, 6):
        content = [
            {
                "type": "image",
                "data": {
                    "file": f"{msg['msg_key']}.{content['imageType']}",
                    "url": content["url"],
                    "original": content["original"],
                    "size": content["size"],
                    "width": content["width"],
                    "height": content["height"],
                },
            }
        ]

    elif mtype == 5:
        kind = "私聊撤回"
        raw_content = Msg.content_disjoin(f"{msg['sender_uid']} 撤回了 {msg['sender_uid']} 的消息 - ")
        from message.handler.msg_pool import MsgPool
        withdraw_msg = MsgPool.seq_get(str(content))
        if withdraw_msg:  # 如果不存在，则为消息序号
            content = raw_content + withdraw_msg.get("content")

    elif mtype == 7:
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

    elif mtype == 10:
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


async def bili_fan_get():
    """私聊粉丝获取"""
    url = "https://api.bilibili.com/x/relation/fans"

    params = {
        "vmid": config["BILI_UID"],
    }
    response = await request_deal(url, "get", params, "私聊粉丝获取")
    fan_list = response["data"]["list"]
    fan_users = await status_check(status="fan")
    old_fan = fan_users[0] if fan_users else None  # 上次最新粉丝
    old_fan_index = None
    if old_fan:
        for idx, item in enumerate(fan_list):
            if str(item["mid"]) == str(old_fan):
                old_fan_index = idx
                break
        if old_fan_index is not None and old_fan_index > 0:
            for i in range(old_fan_index):
                Msg(
                    platform="BILI",
                    kind="私聊添加",
                    event="处理",
                    user=fan_list[i]["mid"]
                )
        await status_delete(old_fan, "fan")
    new_fan = fan_list[0]["mid"]
    await status_add(new_fan, "fan")
