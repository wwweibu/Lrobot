"""LR5921 调用 API"""

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
        f"[LR5921] {tag} 成功 -> {data}",
        extra={"event": "消息发送"},
    )
    return json_resp


async def lr5921_sign_in(group):
    """群聊签到"""
    url = f"{base_url}/send_group_sign"
    data = {"group_id": group}

    await request_deal(url, data, "群聊签到")


async def lr5921_poke(user, group=None):
    """戳戳"""
    url = f"{base_url}/send_poke"
    data = {
        "user_id": config["private"]["LR5921"][0],
        **({"group_id": group} if group else {}),
        "target_id": user,
    }
    await request_deal(url, data, f"{'群聊' if group else '私聊'}戳戳")


async def lr5921_share(num, user=None, group=None):
    """分享"""
    url = f"{base_url}/ArkSharePeer"
    data = {
        **({"user_id": user} if user else {}),
        **({"group_id": group} if group else {}),
    }
    data = await request_deal(url, data, f"{'群聊' if group else '私聊'}分享")
    data = data.get("data", "")

    if data:
        err_code = data.get("errCode")
        if err_code != 0:
            raise Exception(
                f"{'群聊' if group else '私聊'}分享失败 -> {data.get('errMsg', '无错误信息')}"
            )
        if user:
            future.set(num, data.get("arkMsg"))
        else:
            future.set(num, data.get("arkJson"))


async def lr5921_status_set(status, ext_status, battery_status, id, word):
    """私聊状态设置，输入'状态|电量'或'自定义|电量|表情|文字"""
    url = f"{base_url}/set_online_status"
    data = {
        "status": status,
        "ext_status": ext_status,
        "battery_status": battery_status,
    }
    if id:
        url = f"{base_url}/set_diy_online_status"
        data = {"face_id": id, "face_type": 1, "wording": word}
    await request_deal(url, data, "私聊状态设置")


async def lr5921_echo(seq, emoji):
    """群聊回应"""
    url = f"{base_url}/set_msg_emoji_like"
    emoji_id = next((k for k, v in config["emojis"].items() if v == emoji), None)
    if emoji_id:
        data = {"message_id": seq, "emoji_id": emoji_id, "set": True}
        await request_deal(url, data, "群聊回应")


async def lr5921_signature(sign):
    """私聊签名"""
    url = f"{base_url}/set_self_longnick"
    data = {"longNick": sign}
    await request_deal(url, data, "私聊签名")


async def lr5921_msg_get(num, seq):
    """私聊消息获取"""
    url = f"{base_url}/get_msg"
    data = {"message_id": seq}
    data = await request_deal(url, data, "私聊获取消息")
    future.set(num, data.get("data").get("message", ""))


async def lr5921_favor(content, brief):
    """私聊收藏"""
    url = f"{base_url}/create_collection"
    data = {"rawData": content, "brief": brief}
    await request_deal(url, data, "私聊收藏")


async def lr5921_status_get(num, user):
    """私聊状态获取"""
    url = f"{base_url}/nc_get_user_status"
    data = {"user_id": user}
    data = await request_deal(url, data, "私聊状态获取")
    status = None
    target_status = str(data.get("data").get("status"))
    target_ext_status = str(data.get("data").get("ext_status"))
    for name, code in config["online_status"].items():
        status_code, ext_code = code.split("|")
        if status_code == target_status and ext_code == target_ext_status:
            status = name
    if status:
        future.set(num, status)
    else:
        raise Exception(f"未知状态 | 用户: {user} | 数据: {data.get('data')}")


async def lr5921_dispatch(
        content,
        kind=None,
        user=None,
        group=None,
        num=None,
        msg_id=None,
        msg_seq=None,
):
    """消息发送"""
    if kind.startswith("私聊"):
        if content[0].get("type") == "forward":
            url = f"{base_url}/forward_friend_single_msg"
            tag1 = "message_id"
            content = content[0].get("data").get("id")
        elif content[0].get("type") == "node":
            url = f"{base_url}/send_forward_msg"
            tag1 = "messages"
            content = content[0].get("data").get("content")
        elif content[0].get("type") == "poke":
            url = f"{base_url}/send_poke"
            tag1 = "111"
        else:
            url = f"{base_url}/send_private_msg"
            tag1 = "message"
        tag2 = "user_id"
        id = user
    else:
        if content[0].get("type") == "forward":
            url = f"{base_url}/forward_friend_single_msg"
            tag1 = "message_id"
            content = content[0].get("data").get("id")
        elif content[0].get("type") == "node":
            url = f"{base_url}/send_forward_msg"
            tag1 = "messages"
            content = content[0].get("data").get("content")
        elif content[0].get("type") == "poke":
            url = f"{base_url}/send_poke"
            tag1 = "user_id"
            content = user
        else:
            url = f"{base_url}/send_group_msg"
            tag1 = "message"
        tag2 = "group_id"
        id = group

    data = {
        tag2: id,
        tag1: content,
    }

    await request_deal(url, data, "消息发送")


async def lr5921_withdraw(seq, user=None, kind=None):
    """撤回消息"""
    url = f"{base_url}/delete_msg"

    data = {"message_id": seq}

    await request_deal(url, data, f"撤回")


async def lr5921_essence(id, content=None):
    """群聊精华"""
    if content == "添加":
        url = f"{base_url}/set_essence_msg"
    else:
        url = f"{base_url}/delete_essence_msg"

    data = {"message_id": id}

    data = await request_deal(url, data, "测试消息")
    word = data.get("data", "").get("result", "").get("wording")
    if word:
        raise Exception(f"设精失败 -> {data}")


async def lr5921_title(user, group, title):
    """群聊头衔"""
    url = f"{base_url}/set_group_special_title"

    data = {"group_id": group, "user_id": user, "special_title": title}

    await request_deal(url, data, "群聊头衔")


async def lr5921_list(num, group):
    """群聊列表"""
    url = f"{base_url}/get_group_member_list"

    data = {"group_id": group}
    data = await request_deal(url, data, "测试消息")
    user_list = [
        {"user_id": u["user_id"], "nickname": u["nickname"]} for u in data.get("data")
    ]
    future.set(num, user_list)


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
