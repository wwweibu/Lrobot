"""LR232 消息接收"""

import re
import nacl.signing
import nacl.encoding
from fastapi import APIRouter
from cachetools import TTLCache

from message.handler.msg import Msg
from config import config, monitor_adapter, loggers

cache_5s = TTLCache(maxsize=100_000, ttl=5)
router = APIRouter()
adapter_logger = loggers["adapter"]


def generate_signature(bot_secret, event_ts, plain_token):
    """生成 ed25519 签名"""
    bot_secret = (bot_secret * 2)[:32].encode()
    private_key = nacl.signing.SigningKey(bot_secret)  # 生成私钥n
    return private_key.sign(
        (event_ts + plain_token).encode(), encoder=nacl.encoding.HexEncoder
    ).signature.decode()  # 计算签名


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


def _append_text(content_list, text):
    """添加文本段落"""
    text = text.strip()  # 去除 @ 后面跟着的空格
    if text:
        content_list.append({"type": "text", "data": {"text": text}})


def _append_face(content_list, face_type, face_id, ext, raw):
    """添加表情/动画"""
    if face_type == "3":
        if face_id == "358":
            content_list.append({"type": "dice", "data": {"result": ''}})
        elif face_id == "359":
            content_list.append({"type": "rps", "data": {"result": ''}})
        else:
            content_list.append({"type": "face", "data": {"id": face_id, "type": face_type, "ext": ext}})
    elif face_type == "4":
        content_list.append({"type": "image", "data": {"summary": "[动画表情]", "file": ext}})
    else:
        _append_text(content_list, raw)


def _append_attachment(content_list, attachment):
    """添加附件"""
    ATTACHMENT_TYPES = {
        "image/jpeg": "image",
        "image/png": "image",
        "image/gif": "image",
        "video/mp4": "video",
        "voice": "record",
    }
    attachment_type = ATTACHMENT_TYPES.get(attachment.get("content_type"), "file")
    content_list.append({
        "type": attachment_type,
        "data": {
            "file": attachment.get("filename"),
            "url": attachment.get("url"),
            "file_size": attachment.get("size"),
            "width": attachment.get("width", 0),
            "height": attachment.get("height", 0),
        }
    })

@monitor_adapter("LR232")
async def lr232_msg_deal(data):
    """消息处理"""
    event_id = data.get("id")  # 事件id
    if not event_id or event_id in cache_5s:
        adapter_logger.info(
            f"⌈LR232⌋ 跳过 5 秒内重复消息 -> {data}", extra={"event": "消息接收"}
        )
        return  # 消息去重
    cache_5s[event_id] = True

    t = data.get("t")
    d = data.get("d", {})
    if not t or not d:
        raise Exception(f"参数不完整 | 数据:{data}")
    KIND_MAP = {
        "C2C_MESSAGE_CREATE": "私聊接收",
        "FRIEND_ADD": "私聊添加",
        "FRIEND_DEL": "私聊删除",
        "GROUP_AT_MESSAGE_CREATE": "群聊接收",
        "GROUP_ADD_ROBOT": "群聊添加",
        "GROUP_DEL_ROBOT": "群聊删除",
    }
    kind = KIND_MAP.get(t)
    if not t:
        raise Exception(f"未定义的消息类型 | 类型: {t} |消息: {data}")
    if kind == "私聊添加":  # 其他三种不处理
        Msg(
            platform="LR232",
            kind=kind,
            event="处理",
            seq=event_id,
            user=d.get("openid"),
        )
    elif kind.endswith("接收"):
        FACE_PATTERN = re.compile(r'<faceType=(\d+),\s*faceId="(.*?)",\s*ext="(.*?)">')
        raw_content = d.get("content")
        content = []
        last_index = 0

        for match in FACE_PATTERN.finditer(raw_content):
            start, end = match.span()
            _append_text(content, raw_content[last_index:start])
            _append_face(content, *match.groups(), raw=match.group(0))
            last_index = end

        _append_text(content, raw_content[last_index:])

        for attachment in d.get("attachments", []) or []:
            _append_attachment(content, attachment)

        Msg(
            platform="LR232",
            kind=kind,
            event="处理",
            user=d.get("author", {}).get("id"),
            seq=d.get("id"),
            content=content,
            group=d.get("group_id"),
        )
