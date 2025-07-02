# LR5921 发送消息
import re
from config import config, loggers, connect,future

base_url = "http://napcat:5921"
adapter_logger = loggers["adapter"]
headers = {"Content-Type": "application/json"}


def msg_content_join(content):
    """将带 [标记] 的 content 转为 message 列表"""
    message = []

    # 拆分成 [xxx] 和非 [xxx] 的文本段
    parts = re.split(r"(\[.*?\])", content)

    for part in parts:
        if not part or part.isspace():
            continue

        match = re.match(r"\[(.*?)\]", part)
        if match:
            inner = match.group(1)
            if ":" in inner:
                key, value = inner.split(":", 1)
                key = key.strip()
                value = value.strip()
            else:
                key, value = inner.strip(), None

            if key == "at" and value:
                message.append({
                    "type": "at",
                    "data": {"qq": value}
                })
            elif key == "表情" and value:
                message.append({
                    "type": "face",
                    "data": {"id": value}
                })
            elif key == "回复" and value:
                message.append({
                    "type": "reply",
                    "data": {"id": value}
                })
            else:
                # 不支持的标签视为文本
                message.append({
                    "type": "text",
                    "data": {"text": part}
                })
        else:
            # 普通文本
            message.append({
                "type": "text",
                "data": {"text": part}
            })

    return message


async def lr5921_dispatch(kind, id, content=None, files=None):
    """发送消息"""
    if kind.startswith("私聊"):
        url = f"{base_url}/send_private_msg"
        tag = "user_id"
    else:
        url = f"{base_url}/send_group_msg"
        tag = "group_id"

    message = []
    if content:
        message_list = msg_content_join(content)
        message.extend(message_list)
    if files:
        for file in files:
            if file[0].lower().endswith((".png", ".jpg", ".jpeg")):
                message.append({"type": "image", "data": {"file": f"file://{file[1]}"}})
            else:
                message.append({"type": "file", "data": {"file": f"file://{file[1]}"}})
    data = {
        tag: id,
        "message": message,
    }

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        # TODO 待测试日志
        adapter_logger.debug(
            f"[LR5921]发送 -> {content if content is not None else files[0][0]}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def lr5921_dispatch_record(kind, id, files):
    """发送语音消息"""
    if kind.startswith("私聊"):
        url = f"{base_url}/send_private_msg"
        tag = "user_id"
    else:
        url = f"{base_url}/send_group_msg"
        tag = "group_id"

    message = []
    for file in files:
        message.append({"type": "record", "data": {"file": f"file://{file[1]}"}})
    data = {
        tag: id,
        "message": message,
    }

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921]发送语音 -> {files[0][0]}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def lr5921_get_share(group=None, user=None, phone=None):
    """TODO 分享名片"""
    url = f"{base_url}/ArkSharePeer"

    if group:
        data = {"group_id": group}
    else:
        data = {"user_id": user, "phoneNumber": phone}

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921]分享二维码 -> {user if user else group}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"二维码分享失败 -> [{response.status_code}]{response.text}")


async def lr5921_set_status(status, ext_status, battery_status):
    """私聊设置状态"""
    url = f"{base_url}/set_online_status"

    data = {
        "status": status,
        "ext_status": ext_status,
        "battery_status": battery_status,
    }

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921]设置状态 -> {status} | {ext_status} | {battery_status}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"状态设置失败 -> [{response.status_code}]{response.text}")


async def lr5921_get_status(id):
    """私聊获取状态"""
    # TODO 解析结果
    url = f"{base_url}/nc_get_user_status"

    data = {"user_id": id}

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921]获取属性 -> {response.text}", extra={"event": "消息发送"}
        )
        data = response.json().get("data", {})
        status = data.get("status")
        ext_status = data.get("ext_status")
        status_map = config["online_status"]
        state = "未知状态"
        for name, key in status_map.items():
            if key == f"{status}|{ext_status}":
                state = name
        print(f"状态为{state}")
    else:
        raise Exception(f"属性获取失败 -> [{response.status_code}]{response.text}")


async def lr5921_set_info(nickname, note, sex):
    """私聊设置信息"""
    url = f"{base_url}/set_qq_profile"
    data = {"nickname": nickname, "personal_note": note, "sex": sex}

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921]设置信息 -> {nickname} | {note} | {sex}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"信息设置失败 -> [{response.status_code}]{response.text}")


async def lr5921_get_info(id,seq):
    """私聊获取信息"""
    url = f"{base_url}/get_stranger_info"

    data = {"user_id": id}

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        future.set(seq, response)
    else:
        raise Exception(f"好友属性获取失败 -> [{response.status_code}]{response.text}")


async def lr5921_get_group(id,seq):
    """群聊获取信息（成员列表）"""
    url = f"{base_url}/get_group_member_list"

    data = {"group_id": id}

    client = connect()
    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        future.set(seq, response)
    else:
        raise Exception(f"好友属性获取失败 -> [{response.status_code}]{response.text}")