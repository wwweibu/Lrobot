# LR232 接收消息
import re
import time
import nacl.signing
import nacl.encoding
from fastapi import APIRouter
from message.handler.msg import Msg
from config import config, monitor_adapter, loggers


router = APIRouter()
adapter_logger = loggers["adapter"]
_msg_cache = {}


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


def msg_content_join(content):
    """转换内容中的表情包"""
    pattern = r'<faceType=(\d+),\s*faceId="(.*?)",\s*ext="(.*?)">'

    # 替换函数
    def replace_face(match):
        face_type = match.group(1)
        face_id = match.group(2)
        ext = match.group(3)

        if face_type in ["1", "3"]:
            face_id = int(face_id)  # 转换为整数
            emoji_name = config["emojis"][face_id]
            if not emoji_name:
                emoji_name = "未知表情"
            return f"[{emoji_name}]"
        elif face_type == "4":
            return f"[动画表情{ext}]"
        else:
            return match.group(0)  # 保留原始内容

    # 替换所有匹配项
    return re.sub(pattern, replace_face, content)


@router.post("/")
async def LR232_receive(data: dict):
    """LR232 接收消息"""
    op = data.get("op")
    if op == 13:  # 回调地址配置
        data = data.get("d", {})
        plain_token = data.get("plain_token")
        event_ts = data.get("event_ts")
        if not plain_token or not event_ts:
            raise Exception(f"回调配置错误 | 数据不完整: {data}")
        signature = generate_signature(config["LR232_SECRET"], event_ts, plain_token)
        adapter_logger.debug(f"⌈LR232⌋ 消息回调配置成功", extra={"event": "回调配置"})
        return {"plain_token": plain_token, "signature": signature}
    elif op == 0:  # qqbot 消息
        adapter_logger.debug(f"⌈LR232⌋ {data}", extra={"event": "消息接收"})
        await handle_lr232_message(data)
        return {"op": 12}, 200
    else:
        raise Exception(f" 不存在 op 码 | 数据: {data}")


@monitor_adapter("LR232")
async def handle_lr232_message(data):
    """消息处理"""
    now = time.time()
    event_id = data.get("id")  # 这个是事件id
    if event_id in _msg_cache and (now - _msg_cache[event_id] < 5):
        adapter_logger.debug(
            f"⌈LR232⌋ 跳过 5 秒内重复消息: {data}", extra={"event": "消息去重"}
        )
        return {"op": 12}, 200  # 消息去重
    _msg_cache[event_id] = now

    t = data.get("t")
    d = data.get("d", {})
    if not event_id or not t or not d:
        raise Exception(f"参数不完整 | 数据:{data}")
    kind_map = {
        "C2C_MESSAGE_CREATE": "私聊",
        "C2C_MSG_REJECT": "私聊关闭推送",
        "C2C_MSG_RECEIVE": "私聊开启推送",
        "GROUP_AT_MESSAGE_CREATE": "群聊",
        "GROUP_ADD_ROBOT": "群聊添加",
        "GROUP_DEL_ROBOT": "群聊删除",
        "GROUP_MSG_REJECT": "群聊关闭推送",
        "GROUP_MSG_RECEIVE": "群聊开启推送",
        "FRIEND_DEL": "好友删除",
        "FRIEND_ADD": "好友添加",
    }
    if t not in kind_map:
        raise Exception(f"未定义的消息类型 | 类型: {t} |消息: {data}")
    kind = kind_map.get(t, "未知消息类型")
    if kind not in ["私聊", "群聊"]:
        if kind.startswith("私聊"):
            user_id = d.get("openid")
            group_id = None
        else:
            user_id = d.get("op_member_openid")
            group_id = d.get("group_openid")
        Msg(
            robot="LR232",
            kind=kind,
            event="处理",
            source=user_id,
            seq=event_id,
            content="",
            group=group_id,
        )
    else:
        id = d.get("id")  # 这个是消息id
        content = d.get("content")
        author = d.get("author", {})
        user_id = author.get("id")
        group_id = d.get("group_id")
        attachments = d.get("attachments", {})
        files = []
        if kind.startswith("私聊"):
            event = "处理"
        else:
            if config["EXAM_MODE"] == 1:
                event = "处理"
            else:
                event = "匹配"  # 群聊中 @ 消息需要匹配
        if not attachments:  # 纯文字消息
            kind = kind + "文字消息"
        else:
            if not content:  # 纯文件消息
                kind = kind + "文件消息"
            else:
                kind = kind + "图文消息"
            for attachment in attachments:
                file_name = attachment.get("filename")
                file_url = attachment.get("url")
                if file_name and file_url:
                    files.append((file_name, file_url))
        Msg(
            robot="LR232",
            kind=kind,
            event=event,
            source=user_id,
            seq=id,
            content=msg_content_join(content),
            files=files,
            group=group_id,
        )
