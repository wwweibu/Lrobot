"""LR232 消息接收"""

import re
import json
import base64
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
            raise Exception(f"[回调配置]⌈LR232⌋请求失败-> 数据不完整: {data}")
        signature = generate_signature(config["LR232_SECRET"], event_ts, plain_token)
        adapter_logger.debug(f"[回调]⌈LR232⌋-> 成功: {data}", extra={"event": "消息接收"})
        return {"plain_token": plain_token, "signature": signature}
    elif op == 0:  # qqbot 消息
        adapter_logger.debug(f"[接收]⌈LR232⌋{data}", extra={"event": "消息接收"})
        await lr232_msg_deal(data)
        return {"op": 12}, 200
    else:
        raise Exception(f"[消息接收]⌈LR232⌋请求失败-> 不存在 op 码: {data}")


def _text_append(content_list, text):
    """添加文本段落"""
    text = text.strip()  # 去除 @ 后面/默认指令后面跟着的空格
    if text:
        content_list.append({"type": "text", "data": {"text": text}})


def ext_summary(ext):
    """解析 ext 字段"""
    try:
        raw = base64.b64decode(ext).decode('utf-8', errors='ignore')
    except Exception:
        raw = ext

    if raw.startswith('{'):
        try:
            obj = json.loads(raw)
            text = obj.get('text', '')
            if text:
                return text
        except Exception:
            pass

    return '[动画表情]'


def _face_append(content_list, face_type, face_id, ext):
    """添加表情/动画"""
    if face_type == "3":
        if face_id == "358":
            content_list.append({"type": "dice", "data": {"result": ''}})
        elif face_id == "359":
            content_list.append({"type": "rps", "data": {"result": ''}})
        else:
            content_list.append(
                {"type": "face", "data": {"id": face_id, "type": face_type, "summary": ext_summary(ext)}})
    else:
        content_list.append({"type": "image", "data": {"summary": ext_summary(ext)}})


def _attachment_append(content_list, attachment):
    """添加附件"""
    ATTACHMENT_TYPES = {
        "image/jpeg": "image",
        "image/png": "image",
        "image/gif": "image",
        "video/mp4": "video",
        "voice": "record",
    }
    attachment_type = ATTACHMENT_TYPES.get(attachment.get("content_type"), "file")
    data = {
        "file": attachment.get("filename"),
        "url": attachment.get("url"),
        "file_size": attachment.get("size"),
    }

    if attachment_type in ("image", "video"):
        data.update({
            "width": attachment.get("width", 0),
            "height": attachment.get("height", 0),
        })
    content_list.append({
        "type": attachment_type,
        "data": data
    })


def _faces_merge(content_list):
    """合并或过滤动画表情与图片"""
    # 找出动画表情和文件图片
    face6_idx = [i for i, c in enumerate(content_list)
                 if c.get("type") == "image" and c["data"].get("summary") == "动画表情"]
    image_idx = [i for i, c in enumerate(content_list)
                 if c.get("type") == "image" and "file" in c["data"]]

    # 一一合并
    if len(face6_idx) == len(image_idx) and face6_idx:
        for f_i, img_i in zip(face6_idx, image_idx):
            face_item = content_list[f_i]
            image_item = content_list[img_i]
            merged = {
                "type": "image",
                "data": {
                    "summary": face_item["data"].get("summary", "[动画表情]"),
                    "file": image_item["data"].get("file"),
                    "url": image_item["data"].get("url"),
                    "file_size": image_item["data"].get("file_size"),
                    "width": image_item["data"].get("width"),
                    "height": image_item["data"].get("height"),
                }
            }
            content_list[f_i] = merged  # 原位替换 face
        for i in sorted(image_idx, reverse=True):
            del content_list[i]

    else:  # 数量不等，即表情+图片，全部保留为图片
        content_list[:] = [
            c for c in content_list
            if not (c.get("type") == "image" and c["data"].get("summary") == "动画表情")
        ]

@monitor_adapter("LR232")
async def lr232_msg_deal(data):
    """消息处理"""
    event_id = data.get("id")  # 事件id
    if not event_id or event_id in cache_5s:
        adapter_logger.debug(
            f"⌈LR232⌋{data}", extra={"event": "消息去重"}
        )
        return
    cache_5s[event_id] = True

    t = data.get("t")
    d = data.get("d", {})
    if not t or not d:
        raise Exception(f"[消息接收]⌈LR232⌋请求失败-> 数据不完整: {data}")
    KIND_MAP = {
        "C2C_MESSAGE_CREATE": "私聊接收",
        "FRIEND_ADD": "私聊添加",
        "FRIEND_DEL": "私聊删除",
        "GROUP_AT_MESSAGE_CREATE": "群聊接收",
        "GROUP_ADD_ROBOT": "群聊添加",
        "GROUP_DEL_ROBOT": "群聊删除",
    }
    kind = KIND_MAP.get(t)
    if not kind:
        raise Exception(f"[消息接收]⌈LR232⌋请求失败-> 未定义的 t: {data}")
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
            _text_append(content, raw_content[last_index:start])
            _face_append(content, *match.groups())
            last_index = end

        _text_append(content, raw_content[last_index:])

        for attachment in d.get("attachments", []) or []:
            _attachment_append(content, attachment)

        _faces_merge(content)

        Msg(
            platform="LR232",
            kind=kind,
            event="处理",
            user=d.get("author", {}).get("id"),
            seq=d.get("id"),
            content=content,
            group=d.get("group_id"),
        )
