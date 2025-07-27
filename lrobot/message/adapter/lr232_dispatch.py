"""LR232 API 调用"""

import os
import base64

from .acess_token import access_tokens
from config import loggers, connect, future

adapter_logger = loggers["adapter"]


async def request_deal(url, data, tag):
    """请求统一处理"""
    token = access_tokens["LR232"]["token"]
    headers = {"Authorization": f"QQBot {token}"}
    client = connect(True)
    try:
        response = await client.post(
            url, json=data, headers=headers, timeout=10.0
        )
    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  {type(e).__name__}: {e} | data: {data}")
    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {data}"
        )
    json_resp = response.json()
    print(json_resp)
    return json_resp


async def lr232_dispatch(
        content,
        kind=None,
        user=None,
        group=None,
        num=None,
        msg_id=None,
        msg_seq=None,
):
    """LR232 消息发送/私聊 or 群聊添加"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/users/{user}/files"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{group}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/groups/{group}/files"
    if kind.endswith("添加"):
        tag = "event_id"
    else:
        tag = "msg_id"
    if not msg_seq:
        msg_seq = 1

    content_parts = []
    file_parts = []
    for item in content:
        if item["type"] in ["image", "record", "video"]:
            if "file" in item["data"]:
                file_parts.append(item["data"]["file"])
        elif item["type"] == "text":
            text = item["data"].get("text", "")
            content_parts.append(text)
    final_content = "".join(content_parts)
    seq = []
    if final_content:
        data = {
            "content": final_content,
            "msg_type": 0,
            tag: msg_id,
            "msg_seq": msg_seq
        }
        msg_seq += 1
        response = await request_deal(url, data, "私聊发送")
        print(response)
        seq.append(response.get("id"))
    for file in file_parts:
        media = await lr232_file_upload(file, url=upload_url)
        # TODO 解析出 media
        data = {
            "msg_type": 7,
            tag: msg_id,
            "msg_seq": msg_seq,
            "media": media
        }
        msg_seq += 1

        response = await request_deal(url, data, "私聊发送")
        print(response)
        seq.append(response.get("id"))
    future.set(num, seq)


async def lr232_file_upload(filepath, type=None, url=None):
    """文件上传"""
    with open(filepath, "rb") as f:
        file_data = base64.b64encode(f.read()).decode(
            "utf-8"
        )  # 读取本地文件并编码为 base64
    file_name = os.path.basename(filepath)
    if (
            file_name.endswith(".png")
            or file_name.endswith(".png")
            or file_name.endswith(".jpeg")
    ):
        file_type = 1
    elif file_name.endswith(".mp4"):
        file_type = 2
    elif file_name.endswith(".silk"):
        file_type = 3
    else:
        raise Exception(f"文件上传失败 -> 文件类型不支持 | 文件名 :{file_name}")
    data = {
        "file_type": file_type,
        "srv_send_msg": False,
        "file_data": file_data,
    }
    response = await request_deal(url, data, "文件上传")
    return response


async def lr232_withdraw(seq, user, kind):
    """LR232 撤回消息"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages/{seq}"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{user}/messages/{seq}"
    await request_deal(url, {}, f"{kind[:2]}撤回")
