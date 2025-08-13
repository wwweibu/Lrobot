"""LR5921 调用 API"""

import json

from logic import file_download
from config import config, loggers, connect, future

base_url = "http://napcat:5921"
adapter_logger = loggers["adapter"]
headers = {"Content-Type": "application/json"}


async def request_deal(url, data, tag):
    """请求统一处理"""
    timeout = 15.0
    if ".mp4" in str(data):
        timeout = 60.0
    client = connect()
    try:
        response = await client.post(url, json=data, headers=headers, timeout=timeout)
    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  e: {e} | data: {data}")

    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {data}"
        )

    json_resp = response.json()
    if json_resp.get("status") != "ok":
        raise Exception(f"{tag} 请求失败 -> {json_resp} | data: {data}")

    adapter_logger.info(
        f"[LR5921] {tag} 成功 -> {data} | {json_resp}",
        extra={"event": "消息发送"},
    )
    return json_resp


async def lr5921_dispatch(
        content,
        kind=None,
        user=None,
        group=None,
        num=None,
        seq=None,
        order=None
):
    """发送"""
    msg_type = content[0].get("type")
    data = content[0].get("data", {})
    if msg_type == "forward":
        url = f"{base_url}/forward_friend_single_msg"
        tag1 = "message_id"
        content = data.get("id")
    elif msg_type == "node":
        url = f"{base_url}/send_forward_msg"
        tag1 = "messages"
        content = data.get("content")
    elif msg_type == "poke":
        url = f"{base_url}/send_poke"
        if kind.startswith("私聊"):
            tag1 = "111"
        else:
            tag1 = "user_id"
            content = user
    else:
        url = f"{base_url}/send_private_msg" if kind.startswith("私聊") else f"{base_url}/send_group_msg"
        tag1 = "message"
    tag2 = "user_id" if kind.startswith("私聊") else "group_id"
    id = user if kind.startswith("私聊") else group

    data = {
        tag2: id,
        tag1: content,
    }

    response = await request_deal(url, data, "消息发送")
    future.set(num, response.get("data").get("message_id", ""))


async def lr5921_msg_get(seq, num=None, user=None):
    """消息获取"""
    url = f"{base_url}/get_msg"
    data = {"message_id": seq}
    data = await request_deal(url, data, "消息获取")
    message_list = data.get("data").get("message", "")
    for message in message_list:
        if message.get("type", "") == "json":
            if isinstance(message["data"]["data"], str):
                try:
                    message["data"]["data"] = json.loads(message["data"]["data"])
                except json.JSONDecodeError:
                    pass
    future.set(num, message_list)


async def lr5921_file_download(file, path):
    """文件下载"""
    url = f"{base_url}/get_private_file_url"
    data = {"file_id": file}
    response = await request_deal(url, data, "文件下载")
    url = response.get("data").get("url")
    await file_download(path, url)


async def lr5921_withdraw(seq, user=None, kind=None):
    """撤回消息"""
    url = f"{base_url}/delete_msg"
    data = {"message_id": seq}

    await request_deal(url, data, f"{kind[:2]}撤回")


async def lr5921_signature(sign):
    """私聊签名"""
    url = f"{base_url}/set_self_longnick"
    data = {"longNick": sign}
    await request_deal(url, data, "私聊签名")


async def lr5921_status(state=None, battery_status=None, emoji=None, word=None):
    """私聊状态，输入'状态|电量'或'自定义|表情|文字"""
    if emoji:
        emoji_id = next((k for k, v in config["emojis"].items() if v == emoji), None)
        url = f"{base_url}/set_diy_online_status"
        data = {"face_id": emoji_id, "face_type": 1, "wording": word}
    else:
        status = config["online_status"][state].split("|")
        if not status:
            raise Exception(f"状态不存在 | 状态: {state}")
        url = f"{base_url}/set_online_status"
        data = {
            "status": status[0],
            "ext_status": status[1],
            "battery_status": battery_status,
        }
    await request_deal(url, data, "私聊状态设置")


async def lr5921_member(num, group):
    """群聊成员"""
    url = f"{base_url}/get_group_member_list"

    data = {"group_id": group}
    data = await request_deal(url, data, "群聊成员")
    user_list = [
        {"user_id": u["user_id"], "nickname": u["nickname"]} for u in data.get("data")
    ]
    future.set(num, user_list)


async def lr5921_sign_in(group):
    """群聊签到"""
    url = f"{base_url}/send_group_sign"
    data = {"group_id": group}

    await request_deal(url, data, "群聊签到")


async def lr5921_echo(seq, emoji):
    """群聊回应"""
    url = f"{base_url}/set_msg_emoji_like"
    emoji_id = next((k for k, v in config["emojis"].items() if v == emoji), None)
    if emoji_id:
        data = {"message_id": seq, "emoji_id": emoji_id, "set": True}
        await request_deal(url, data, "群聊回应")


async def lr5921_essence(id, content=None):
    """群聊精华"""
    if content == "删除":
        url = f"{base_url}/delete_essence_msg"
    else:
        url = f"{base_url}/set_essence_msg"

    data = {"message_id": id}

    data = await request_deal(url, data, "群聊精华")
    word = data.get("data", "").get("result", "").get("wording")
    if word:
        raise Exception(f"精华设置失败 -> {data}")


async def lr5921_title(user, group, title):
    """群聊头衔"""
    url = f"{base_url}/set_group_special_title"

    data = {"group_id": group, "user_id": user, "special_title": title}

    await request_deal(url, data, "群聊头衔")


async def lr5921_card(num, type, title, desc, picUrl, jumpUrl):
    """卡片"""
    url = f"{base_url}/get_mini_app_ark"

    data = {
        "type": type,
        "title": title,
        "desc": desc,
        "picUrl": picUrl,
        "jumpUrl": jumpUrl,
    }

    data = await request_deal(url, data, "测试消息")
    future.set(num, data.get("data").get("data"))

# TODO 群文件上传下载整理相关
# TODO 获取昵称
