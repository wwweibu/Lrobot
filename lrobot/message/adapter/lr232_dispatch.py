"""LR232 API 调用"""

import os
import json
import base64
from datetime import datetime, timedelta

from .acess_token import access_tokens
from logic import record_convert, video_compress, image_compress
from config import loggers, connect, future, database_query, database_update

adapter_logger = loggers["adapter"]


def data_format(data):
    """转换数据中文件源码"""
    if "file_data" in data:
        return {**data, "file_data": f"<base64 length={len(data['file_data'])}>"}
    return data

async def request_deal(url, data, tag):
    """请求统一处理"""
    headers = {"Authorization": f"QQBot {access_tokens['LR232']['token']}"}
    client = connect(True)
    format_data = data_format(data)  # 避免文件数据爆日志
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
        raise Exception(f"{tag} 请求异常 ->  {type(e).__name__}: {e} | data: {format_data}")
    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {format_data}"
        )
    json_resp = response.json()
    adapter_logger.info(
        f"[LR232] {tag} 成功 -> {format_data} | {json_resp}",
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
        order=1
):
    """LR232 消息发送/消息添加发送"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/users/{user}/files"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{group}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/groups/{group}/files"
    tag = "event_id" if kind.endswith("添加发送") else "msg_id"

    text_parts = [i["data"].get("text", "") for i in content if i["type"] == "text"]
    file_parts = [i["data"]["file"] for i in content if
                  i["type"] in ["image", "record", "video", "file"] and "file" in i["data"]]

    seq_list = []
    if text_parts:
        data = {
            "content": "".join(text_parts),
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
    query = "SELECT media_json, qq FROM user_media WHERE filepath = %s"
    result = await database_query(query, (file,))
    if result:
        js, t = result[0]["media_json"], result[0]["qq"]
        if js and t and datetime.now() < t + timedelta(hours=1):
            return json.loads(js)
    file_name = os.path.basename(file)
    if file_name.endswith((".png", ".jpeg", ".gif")):
        file_type = 1
        file_data = await image_compress(file, target_size_mb=20, return_type=1)
    elif file_name.endswith(".mp4"):
        file_type = 2
        # 上限 10 Mb，虽然文档里没写
        file_data = await video_compress(file, target_size_mb=9.99, return_type=1)
    elif file_name.endswith(".silk"):
        file_type = 3
        file_data = base64.b64encode(open(file, "rb").read()).decode("utf-8")
    elif file_name.endswith(".mp3"):
        file_type = 3
        file_path = await record_convert(file)
        file_data = base64.b64encode(open(file_path, "rb").read()).decode("utf-8")
    else:
        raise Exception(f"文件上传失败 -> 文件类型不支持 | 文件名 :{file_name}")

    data = {
        "file_type": file_type,
        "srv_send_msg": False,
        "file_data": file_data,
    }
    response = await request_deal(url, data, "文件上传")
    query = """
                   INSERT INTO user_media (filepath, media_json)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE 
                       media_json = VALUES(media_json),
                       qq = CURRENT_TIMESTAMP
               """
    await database_update(query, (file, json.dumps(response)))
    return response


async def lr232_withdraw(seq, user=None, kind=None):
    """LR232 撤回消息"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{user}/messages/{seq}"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{user}/messages/{seq}"
    await request_deal(url, {}, f"{kind[:2]}撤回")
