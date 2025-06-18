# LR5921 消息接收
from typing import Dict
from fastapi import APIRouter
from message.handler.msg import Msg
from config import config, monitor_adapter, loggers


router = APIRouter()
adapter_logger = loggers["adapter"]
_msg_cache = {}


async def msg_content_join(content):
    """拆解内容信息"""
    content_join = ""
    files = []
    for item in content:
        msg_type = item.get("type")
        msg_data = item.get("data", "")
        if msg_type == "text":
            content_join += msg_data.get("text", "")
        elif msg_type == "face":
            face_id = msg_data.get("id")
            face = config["emojis"].get(int(face_id))
            if not face:
                face_text = msg_data.get("raw", {}).get("faceText")
                if face_text is None:
                    raise Exception(f"无法解析的表情 | 表情: {item}")
                face = face_text.strip("[]").lstrip("/")
                emojis = config["emojis"]
                emojis[int(face_id)] = face
                sorted_emojis = dict(
                    sorted(emojis.items(), key=lambda x: int(x[0]))
                )  # 按照 key 排序
                config["emojis"] = sorted_emojis
            content_join += f"[{face}]"
        elif msg_type == "rps":
            rps_id = msg_data.get("result")
            rps_mapping = {"1": "布", "2": "剪刀", "3": "石头"}
            rps_result = rps_mapping.get(
                rps_id, "未知结果"
            )  # 默认值为'未知结果'，如果rps_id不在映射中
            content_join += f"[猜拳:{rps_result}]"
        elif msg_type == "dice":
            dice_id = msg_data.get("result")
            content_join += f"[掷骰子{dice_id}点]"
        elif msg_type == "forward":
            content_join += f"[转发{msg_data.get('id')}]"
        elif msg_type == "node":
            content_join += f"[合并转发节点]"
        elif msg_type == "image":
            content_join += f"{msg_data.get('summary')}"
            files.append((msg_data.get("file"), msg_data.get("url")))
        elif msg_type in ["record", "file", "video"]:
            files.append((msg_data.get("file"), msg_data.get("url")))
        elif msg_type == "reply":
            content_join += f"[回复{msg_data.get('id')}]"
        elif msg_type == "at":
            qq = msg_data.get("qq")
            content_join += f"[@{qq}]"
        else:
            raise Exception(f" 无法解析的消息段落 | 消息: {item}")
    return content_join, files


@router.post("/")
async def lr5921_receive(data: Dict):
    """LR5921 消息接收"""
    adapter_logger.debug(f"⌈LR5921⌋{data}", extra={"event": "消息接收"})
    if data.get("post_type") == "meta_event":
        return {"status": "ok"}
    else:
        await lr5921_message_deal(data)
        return {"status": "ok"}


@monitor_adapter("LR5921")
async def lr5921_message_deal(data):
    post_type = data.get("post_type")
    seq = data.get("message_id", "")
    group = data.get("group_id", "")
    kind = "群聊" if data.get("message_type") == "group" else "私聊"
    content = data.get("message", "")
    source = data.get("user_id", "")
    files = ""
    if post_type == "notice":
        notice_type = data.get("notice_type")
        kind_map = {
            "friend_add": "私聊添加机器",
            "friend_recall": "私聊撤回消息",
            "group_admin": "群聊增加管理",
            "group_ban": "群聊开启禁言",
            "group_decrease": "群聊减少成员",
            "group_increase": "群聊申请加入",
            "group_recall": "群聊撤回消息",
            "group_upload": "群聊上传文件",
            "essence": "群聊设精消息",
            "group_msg_emoji_like": "群聊点赞消息",
            "notify": "消息提醒",
        }
        kind = kind_map.get(notice_type, "未知消息类型")
        if kind == "群聊增加管理":
            if data.get("sub_type") == "unset":
                kind = "群聊减少管理"
        elif kind == "群聊开启禁言":
            if data.get("sub_type") == "lift_ban":
                kind = "群聊解除禁言"
        elif kind == "群聊减少成员":
            if data.get("sub_type") == "kick":
                kind = "群聊踢出成员"
        elif kind == "群聊申请加入":
            if data.get("sub_type") == "invite":
                kind = "群聊邀请加入"
        elif kind == "群聊撤回消息":
            content = f"{data.get('operator_id')}撤回了{source}的消息"
        elif kind == "群聊上传文件":
            return {"status": "ok"}
        elif kind == "群聊设精消息":
            content = (
                f"{data.get('operator_id')}给{data.get('sender_id')}的消息设置了精华"
            )
        elif kind == "消息提醒":
            sub_type = data.get("sub_type")
            if sub_type == "input_status":
                return {"status": "ok"}
            elif sub_type == "poke":
                kind = "群聊戳戳消息"
                text = data.get("raw_info")
                targets = [
                    item["txt"]
                    for item in text
                    if item.get("type") == "nor" and "txt" in item
                ]
                content = f"{source}{targets[0]}{data.get('target_id')}{targets[1]}"
            elif sub_type == "profile_like":
                kind = "私聊点赞消息"
    elif post_type == "message_sent":
        kind += "发送"
        sender = data.get("sender")
        source = sender.get("user_id")
        nickname = sender.get("nickname", "")
        if nickname == "临时会话":
            kind += "临时"  # 私聊临时发送存在群名
        return  # TODO 暂时不处理发送消息
    elif post_type == "message":
        content, files = await msg_content_join(content)
        if content:
            if files:
                kind += "图文"
            else:
                kind += "文字"
        else:
            kind += "文件"
        sender = data.get("sender")
        nickname = sender.get("nickname", "")
        if nickname == "临时会话":
            kind += "临时"
        else:
            kind += "消息"
    else:
        raise Exception(f" 未定义的消息类型 | 消息: {data}")

    Msg(
        robot="LR5921",
        kind=kind,
        event="处理",
        source=source,
        seq=seq,
        content=content,
        group=group,
        files=files,
    )
