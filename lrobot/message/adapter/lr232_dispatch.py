# LR232 消息发送
import os
import base64
from config import loggers, connect
from .acess_token import access_tokens

adapter_logger = loggers["adapter"]
token = access_tokens["LR232"]["token"]
headers = {"Authorization": f"QQBot {token}"}

async def lr232_dispatch(
    kind, openid, content, event_id=None, msg_id=None, msg_seq=None, files=None
):
    """LR232 发送消息"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{openid}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/users/{openid}/files"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{openid}/messages"
        upload_url = f"https://api.sgroup.qq.com/v2/groups/{openid}/files"

    media = {}
    client = connect(True)
    if files:
        file_name, file_url = files[0]  # 只能上传一个文件
        if not os.path.isfile(file_url):
            raise Exception(f"文件上传失败 -> 路径{file_url}不存在")
        with open(file_url, "rb") as f:
            file_data = base64.b64encode(f.read()).decode(
                "utf-8"
            )  # 读取本地文件并编码为 base64
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
        upload_data = {
            "file_type": file_type,
            "srv_send_msg": False,
            "file_data": file_data,
        }
        response = await client.post(
            upload_url, json=upload_data, headers=headers, timeout=10.0
        )
        if response.status_code == 200:
            media = response.json()
        else:
            raise Exception(
                f"文件上传失败 -> 网络返回码[{response.status_code}]{response.text}"
            )
    data = {
        "content": content if content is not None else " ",
        "msg_type": 7 if files else 0,
        **({"media": media} if media else {}),
        **({"event_id": event_id} if event_id is not None else {}),
        **({"msg_id": msg_id} if msg_id is not None else {}),
        **({"msg_seq": msg_seq} if msg_seq is not None else {}),
    }
    response = await client.post(url, json=data, headers=headers)

    if response.status_code == 200:
        # TODO 待测试，发送图片消息日志
        adapter_logger.info(
            f"[LR232]发送 -> {content if content is not None else files[0][0]}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息发送失败 -> [{response.status_code}]{response.text}")


async def lr232_withdraw(kind, openid, msg_id):
    """LR232 撤回消息"""
    if kind.startswith("私聊"):
        url = f"https://api.sgroup.qq.com/v2/users/{openid}/messages/{msg_id}"
    else:
        url = f"https://api.sgroup.qq.com/v2/groups/{openid}/messages/{msg_id}"

    client = connect(True)
    response = await client.delete(url, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[LR232]撤回 -> 消息{msg_id}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"消息撤回失败 -> [{response.status_code}]{response.text}")
