"""LR232 接收消息"""

import re
import time
import nacl.signing
import nacl.encoding
from fastapi import APIRouter

from message.handler.msg import Msg
from config import config, monitor_adapter, loggers

_msg_cache = {}
router = APIRouter()
adapter_logger = loggers["adapter"]


def generate_signature(bot_secret, event_ts, plain_token):
    """生成 ed25519 签名"""
    while len(bot_secret) < 32:
        bot_secret *= 2
    bot_secret = bot_secret[:32].encode()
    private_key = nacl.signing.SigningKey(bot_secret)  # 生成私钥
    message = event_ts + plain_token
    signature = private_key.sign(
        message.encode(), encoder=nacl.encoding.HexEncoder
    ).signature.decode()  # 计算签名
    return signature


@router.post("/")
async def lr232_receive(data: dict):
    """LR232 接收消息"""
    op = data.get("op")
    if op == 13:  # 回调地址配置
        data = data.get("d", {})
        plain_token = data.get("plain_token")
        event_ts = data.get("event_ts")
        if not plain_token or not event_ts:
            raise Exception(f"回调配置错误 -> 数据不完整: {data}")
        signature = generate_signature(config["LR232_SECRET"], event_ts, plain_token)
        adapter_logger.debug(f"⌈LR232⌋ 回调配置成功", extra={"event": "消息接收"})
        return {"plain_token": plain_token, "signature": signature}
    elif op == 0:  # qqbot 消息
        adapter_logger.debug(f"⌈LR232⌋ {data}", extra={"event": "消息接收"})
        await lr232_msg_deal(data)
        return {"op": 12}, 200
    else:
        raise Exception(f" 不存在 op 码 | 数据: {data}")


@monitor_adapter("LR232")
async def lr232_msg_deal(data):
    """消息处理"""
    now = time.time()
    event_id = data.get("id")  # 事件id
    if event_id in _msg_cache and (now - _msg_cache[event_id] < 5):
        adapter_logger.info(
            f"⌈LR232⌋ 跳过 5 秒内重复消息 -> {data}", extra={"event": "消息接收"}
        )
        return  # 消息去重
    _msg_cache[event_id] = now

    t = data.get("t")
    d = data.get("d", {})
    if not event_id or not t or not d:
        raise Exception(f"参数不完整 | 数据:{data}")
    kind_map = {
        "C2C_MESSAGE_CREATE": "私聊接收",
        "FRIEND_ADD": "私聊添加",
        "FRIEND_DEL": "私聊删除",
        "GROUP_AT_MESSAGE_CREATE": "群聊接收",
        "GROUP_ADD_ROBOT": "群聊添加",
        "GROUP_DEL_ROBOT": "群聊删除",
    }
    if t not in kind_map:
        raise Exception(f"未定义的消息类型 | 类型: {t} |消息: {data}")
    kind = kind_map.get(t, "未知消息类型")
    if kind.endswith("删除"):
        return  # 不处理
    if kind not in ["私聊接收", "群聊接收"]:
        if kind.startswith("私聊"):
            user_id = d.get("openid")
            group_id = None
        else:
            user_id = d.get("op_member_openid")
            group_id = d.get("group_openid")
        Msg(
            platform="LR232",
            kind=kind,
            event="处理",
            seq=event_id,
            user=user_id,
            group=group_id,
        )
    else:
        id = d.get("id")  # 消息id
        raw_content = d.get("content")
        author = d.get("author", {})
        user_id = author.get("id")
        group_id = d.get("group_id")
        attachments = d.get("attachments", {})
        pattern = re.compile(r'<faceType=(\d+),\s*faceId="(.*?)",\s*ext="(.*?)">')
        content = []
        last_index = 0

        for match in pattern.finditer(raw_content):
            start, end = match.span()
            face_type, face_id, ext = match.groups()

            if start > last_index:
                text_part = raw_content[last_index:start]
                if text_part:
                    content.append({
                        "type": "text",
                        "data": {"text": text_part}
                    })
            if face_type in ["1", "3"]:
                if face_id == "358":
                    content.append({"type": "dice", "data": {"result": ''}})
                elif face_id == "359":
                    content.append({"type": "rps", "data": {"result": ''}})
                else:
                    content.append({
                        "type": "face",
                        "data": {
                            "id": face_id,
                            "type": face_type,
                            "ext": ext
                        }
                    })
            elif face_type == "4":
                content.append({
                    "type": "image",
                    "data": {
                        "summary": "[动画表情]",
                        "file": ext
                    }
                })
            else:
                content.append({
                    "type": "text",
                    "data": {"text": match.group(0)}
                })
            last_index = end

        if last_index < len(raw_content):
            text_part = raw_content[last_index:]
            if text_part:
                content.append({
                    "type": "text",
                    "data": {"text": text_part}
                })
        if attachments:
            for attachment in attachments:
                url = attachment.get("url")
                filename = attachment.get("filename")
                size = attachment.get("size")
                width = attachment.get("width", 0)
                height = attachment.get("height", 0)
                content_type = attachment.get("content_type", "")

                if content_type in ("image/jpeg", "image/png", "image/gif"):
                    type = "image"
                elif content_type == "video/mp4":
                    type = "video"
                elif content_type == "voice":
                    type = "record"
                else:
                    type = "file"

                segment = {
                    "type": type,
                    "data": {
                        "file": filename,
                        "url": url,
                        "file_size": size,
                        "width": width,
                        "height": height,
                    }
                }
                content.append(segment)

        Msg(
            platform="LR232",
            kind=kind,
            event="处理",
            user=user_id,
            seq=id,
            content=content,
            group=group_id,
        )
