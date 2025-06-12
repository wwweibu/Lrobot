# LR5921 发送消息
import httpx
from config import config, loggers, connect

base_url = "http://napcat:5921"
adapter_logger = loggers["adapter"]


async def LR5921_dispatch(kind, id, content=None, files=None):
    """发送消息"""
    if kind.startswith("私聊"):
        url = f"{base_url}/send_private_msg"
        tag = "user_id"
    else:
        url = f"{base_url}/send_group_msg"
        tag = "group_id"
    headers = {"Content-Type": "application/json"}
    message = []
    if content:
        message.append({"type": "text", "data": {"text": content}})
    if files:
        for file in files:
            message.append({"type": "file", "data": {"file": f"file://{file[1]}"}})
    data = {
        tag: id,
        "message": message,
    }
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_dispatch_record(kind, id, files):
    """发送语音消息"""
    if kind.startswith("私聊"):
        url = f"{base_url}/send_private_msg"
        tag = "user_id"
    else:
        url = f"{base_url}/send_group_msg"
        tag = "group_id"
    headers = {"Content-Type": "application/json"}
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
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_set_profile(nickname, note, sex):
    """设置信息"""
    url = f"{base_url}/set_qq_profile"
    headers = {"Content-Type": "application/json"}
    data = {"nickname": nickname, "personal_note": note, "sex": sex}
    print(data)
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_get_share(group=None, user=None, phone=None):
    """TODO 分享码"""
    url = f"{base_url}/ArkSharePeer"
    headers = {"Content-Type": "application/json"}
    if group:
        data = {"group_id": group}
    else:
        data = {"user_id": user, "phoneNumber": phone}
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_set_status(status, ext_status, battery_status):
    """设置状态"""
    url = f"{base_url}/set_online_status"
    headers = {"Content-Type": "application/json"}
    data = {
        "status": status,
        "ext_status": ext_status,
        "battery_status": battery_status,
    }
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_get_info(id):
    """获取好友属性"""
    url = f"{base_url}/get_stranger_info"
    headers = {"Content-Type": "application/json"}
    data = {"user_id": id}
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def LR5921_get_status(id):
    """获取属性"""
    url = f"{base_url}/nc_get_user_status"
    headers = {"Content-Type": "application/json"}
    data = {"user_id": id}
    client = connect()

    response = await client.post(url, json=data, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR5921][成功]{response.text}", extra={"event": "消息发送"}
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
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")
