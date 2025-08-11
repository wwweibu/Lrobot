"""LR232 API 调用"""

import os
import base64

from .acess_token import access_tokens
from config import loggers, connect, future
from logic import record_convert, video_compress, image_compress, record_compress

adapter_logger = loggers["adapter"]


def data_format(data):
    """转换数据中文件源码"""
    if "file_data" in data:
        length = len(data["file_data"])
        data["file_data"] = f"<base64 length={length}>"

async def request_deal(url, data, tag):
    """请求统一处理"""
    token = access_tokens["LR232"]["token"]
    headers = {"Authorization": f"QQBot {token}"}
    client = connect(True)
    try:
        if tag.endswith("撤回"):
            response = await client.delete(
                url, headers=headers, timeout=60.0
            )
        else:
            response = await client.post(
                url, json=data, headers=headers, timeout=60.0
            )
    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  {type(e).__name__}: {e} | data: {data_format(data)}")
    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {data_format(data)}"
        )
    json_resp = response.json()
    adapter_logger.info(
        f"[LR232] {tag} 成功 -> {data_format(data)} | {json_resp}",
        extra={"event": "消息发送"},
    )
    return json_resp


async def lr232_dispatch(
        content,
        kind=None,
        user=None,
        group=None,
        num=None,
        seq=None,
        order=None
):
    """LR232 消息发送/消息添加发送"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/users/{user}/files"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{group}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/groups/{group}/files"
    if kind.endswith("添加发送"):
        tag = "event_id"
    else:
        tag = "msg_id"
    if not order:
        order = 1

    content_parts = []
    file_parts = []
    for item in content:
        if item["type"] in ["image", "record", "video", "file"]:
            if "file" in item["data"]:
                file_parts.append(item["data"]["file"])
        elif item["type"] == "text":
            text = item["data"].get("text", "")
            content_parts.append(text)
    final_content = "".join(content_parts)
    seq_list = []
    if final_content:
        data = {
            "content": final_content,
            "msg_type": 0,
            tag: seq,
            "msg_seq": order
        }
        order += 1
        response = await request_deal(url, data, "私聊发送")
        seq_list.append(response.get("id"))
    for file in file_parts:
        media = await lr232_file_upload(file, url=upload_url)
        data = {
            "msg_type": 7,
            tag: seq,
            "msg_seq": order,
            "media": media
        }
        order += 1

        response = await request_deal(url, data, "私聊发送")
        seq_list.append(response.get("id"))
    future.set(num, seq_list)


async def lr232_file_upload(file, type=None, url=None):
    """文件上传"""
    file_name = os.path.basename(file)
    if (
            file_name.endswith(".png")
            or file_name.endswith(".png")
            or file_name.endswith(".jpeg")
            or file_name.endswith(".gif")
    ):
        file_type = 1
        file_data = await image_compress(file, target_size_mb=20, return_type=1)
    elif file_name.endswith(".mp4"):
        file_type = 2
        # 上限 10 Mb，虽然文档里没写
        file_data = await video_compress(file, target_size_mb=9.99, return_type=1)
    elif file_name.endswith(".silk"):
        file_type = 3
        with open(file, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
    elif file_name.endswith(".mp3"):
        file_type = 3
        file_path = await record_convert(file)
        with open(file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
    else:
        raise Exception(f"文件上传失败 -> 文件类型不支持 | 文件名 :{file_name}")

    data = {
        "file_type": file_type,
        "srv_send_msg": False,
        "file_data": file_data,
    }
    response = await request_deal(url, data, "文件上传")
    return response


async def lr232_withdraw(seq, user=None, kind=None):
    """LR232 撤回消息"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages/{seq}"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{user}/messages/{seq}"
    await request_deal(url, {}, f"{kind[:2]}撤回")
