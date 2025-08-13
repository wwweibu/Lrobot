"""LR5921 消息接收"""

import asyncio
import json
from typing import Dict
from fastapi import APIRouter
from message.handler.msg import Msg
from config import config, monitor_adapter, loggers, future


router = APIRouter()
adapter_logger = loggers["adapter"]
_msg_cache = {}


@router.post("/")
async def lr5921_receive(data: Dict):
    """LR5921 消息接收"""
    adapter_logger.debug(f"⌈LR5921⌋ {data}", extra={"event": "消息接收"})
    if data.get("post_type") in ["meta_event", "message_sent", "request"]:
        return {"status": "ok"}
    else:
        await lr5921_msg_deal(data)
        return {"status": "ok"}


@monitor_adapter("LR5921")
async def lr5921_msg_deal(data):
    """消息处理"""
    post_type = data.get("post_type")
    seq = data.get("message_id", "")
    group = data.get("group_id", "")
    kind = "群聊" if data.get("message_type") == "group" else "私聊"
    content = data.get("message", "")
    user = data.get("user_id", "")

    if post_type == "message":
        if not content:
            return  # 对方已接收文件等为空消息
        if user in config["private"]["LR232"]:
            kind = "系统消息"
        else:
            if content[0].get("type", "") == "forward":
                msg = Msg(
                    platform="LR5921",
                    kind=f"私聊消息获取",
                    user=0,
                    event="发送",
                    seq=seq,
                )
                try:
                    _future = future.get(msg.num)
                    response = await asyncio.wait_for(_future, timeout=20)
                except asyncio.TimeoutError:
                    raise Exception(f"转发消息获取失败 | 消息: {seq} {content}")
                content = response
            elif content[0].get("type", "") == "json":
                if isinstance(content[0]["data"]["data"], str):
                    try:
                        content[0]["data"]["data"] = json.loads(content[0]["data"]["data"])
                    except json.JSONDecodeError:
                        pass
            elif content[0].get("type", "") == "reply":
                reply_id = content[0]["data"].get("id")
                if reply_id:
                    msg = Msg(
                        platform="LR5921",
                        kind="私聊消息获取",
                        user=0,
                        event="发送",
                        seq=reply_id,
                    )
                    try:
                        _future = future.get(msg.num)
                        response = await asyncio.wait_for(_future, timeout=20)
                        content[0]["data"].pop("id", None)  # 删除 id
                        content[0]["data"]["content"] = response  # 添加 content
                    except asyncio.TimeoutError:
                        content[0]["data"]["content"] = None
            kind += "接收"
    elif post_type == "notice":
        notice_type = data.get("notice_type")
        kind_map = {
            "group_upload": "群聊文件",
            "friend_add": "私聊添加",
            "group_increase": "群聊添加",
            "group_decrease": "群聊删除",
            "friend_recall": "私聊撤回",
            "group_recall": "群聊撤回",
            "group_admin": "群聊管理",
            "group_ban": "群聊禁言",
            "group_msg_emoji_like": "群聊回应",
            "essence": "群聊设精",
            "notify": "消息提醒",
            "group_card": "群名片更改"
        }
        kind = kind_map.get(notice_type, "未知消息类型")
        if kind == "群聊文件":
            return  # 会在群聊消息中处理(两边一样)
        elif kind == "群聊添加":
            if data.get("sub_type") == "invite":
                content = f"{data.get('operator_id')} 邀请 {user} 加入群 {data.get('group_id')}"
            else:
                content = f"{data.get('operator_id')} 同意 {user} 加入群 {data.get('group_id')}"
            return
        elif kind.endswith("删除"):
            if data.get("sub_type").startswith("kick"):  # kick or kick_me
                content = f"{data.get('operator_id')} 将 {data.get('user_id')} 踢出群 {data.get('group_id')}"
            else:
                content = f"{data.get('user_id')} 退出群 {data.get('group_id')}"
            return
        elif kind.endswith("撤回"):
            operator = data.get("operator_id") if data.get("operator_id") else user
            content = Msg.content_disjoin(f"{operator} 撤回了 {user} 的消息")
            from message.handler.msg_pool import MsgPool
            withdraw_msg = MsgPool.seq_get(str(seq))
            if withdraw_msg:  # 接收过原消息才能显示撤回
                content += withdraw_msg.get("content") or []  # 返回的是 list;撤回自己消息时会是 None（仅有撤回事件）
        elif kind.endswith("管理"):
            if data.get("sub_type") == "set":
                content = f"{data.get('group_id')} 增加管理 {data.get('user_id')}"
            else:
                content = f"{data.get('group_id')} 减少管理 {data.get('user_id')}"
            return
        elif kind.endswith("禁言"):
            content = "开启" if data.get("sub_type") == "lift_ban" else "关闭"
            return
        elif kind.endswith("回应"):
            # count 字段都为一,不会累加且列表只有一项
            like_list = data.get("likes", [])
            emoji_id = like_list[0].get("emoji_id")
            content = [{"type": "face", "data": {"id": emoji_id}}]
        elif kind.endswith("设精"):
            sender_id = data.get("sender_id")
            if str(sender_id) == "0":  # 自己设置自己
                sender_id = "3502644244"
            content = f"{data.get('operator_id')} 给 {sender_id} 的消息设置了精华"
        elif kind == "消息提醒":
            sub_type = data.get("sub_type")
            if sub_type == "input_status":  # 输入状态
                return
            elif sub_type == "poke":
                if group:
                    kind = "群聊戳戳"
                else:
                    kind = "私聊戳戳"
                text = data.get("raw_info")
                targets = [
                    item["txt"]
                    for item in text
                    if item.get("type") == "nor" and "txt" in item
                ]
                while len(targets) < 2:
                    targets.append("")
                content = f"{user} {targets[0]} {data.get('target_id')} {targets[1]}"
            elif sub_type == "title":
                kind = "群聊头衔"
                content = f"{user} 被设置头衔为 {data.get('title')}"
                return
            elif sub_type == "profile_like":
                kind = "私聊点赞"
                source = data.get("operator_id")
                content = f"{data.get('operator_nick')} 给你点赞了"
                return
            elif sub_type == "group_name":  # 群名称修改
                return
    else:
        raise Exception(f" 未定义的消息类型 | 消息: {data}")

    Msg(
        platform="LR5921",
        kind=kind,
        event="处理",
        user=user,
        seq=seq,
        content=content,
        group=group,
    )
