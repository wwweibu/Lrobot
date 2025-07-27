"""微信公众号消息接收"""

import time
import random
import asyncio
import hashlib
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Request, Response

from message.handler.msg import Msg
from config import config, loggers, monitor_adapter, future


router = APIRouter()
adapter_logger = loggers["adapter"]
_msg_cache = {}


@router.get("/")
def set_callback(signature, timestamp, nonce, echostr):
    """回调地址验证"""
    try:
        token = config["WECHAT_TOKEN"]
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()  # 计算SHA1哈希值
        for item in list:
            sha1.update(item.encode("utf-8"))
        hashcode = sha1.hexdigest()

        if hashcode == signature:  # 比对 signature 与计算出的 hashcode
            adapter_logger.debug(f"⌈WECHAT⌋ 回调配置成功", extra={"event": "消息接收"})
            return Response(content=echostr, media_type="text/plain")
        else:
            raise Exception(
                f"回调配置错误 | 数据不完整: signature-{signature} timestamp-{timestamp} nonce-{nonce} echostr-{echostr}"
            )

    except Exception as e:
        raise Exception(f"回调配置错误 | 错误: {e}")


@router.post("/")
async def wechat_receive(request: Request):
    """接收微信发送的 XML 消息"""
    body = await request.body()
    xml_data = body.decode("utf-8")
    adapter_logger.debug(f"⌈WECHAT⌋ {xml_data}", extra={"event": "消息接收"})
    seq = await wechat_msg_deal(xml_data)
    if not seq:  # 消息重复/取消订阅
        adapter_logger.info(
            f"⌈WECHAT⌋ 跳过消息 -> {xml_data}", extra={"event": "消息接收"}
        )
        return
    try:
        _future = future.get(seq)
        response = await asyncio.wait_for(_future, timeout=15)
        print(response)  # TODO
    except asyncio.TimeoutError:
        adapter_logger.error(
            f"⌈WECHAT⌋ 消息超时 -> 消息: {xml_data}", extra={"event": "消息接收"}
        )
        return ""
    return response


@monitor_adapter("WECHAT")
async def wechat_msg_deal(data):
    """解析微信消息"""
    root = ET.fromstring(data)
    msg_type = root.find("MsgType").text
    from_user = root.find("FromUserName").text
    # 防止一秒内多条消息
    seq = f"{root.find('CreateTime').text}{random.randint(0, 99)}"
    if msg_type == "event":
        event = root.find("Event").text
        if event == "subscribe":
            kind = "私聊添加"
            content = ""
        elif event == "unsubscribe":
            return ""
        elif event == "VIEW":
            return ""  # 无法回复
        else:
            return ""
    else:
        msg_id = root.find("CreateTime").text
        now = time.time()
        if msg_id in _msg_cache and (now - _msg_cache[msg_id] < 20):
            return
        _msg_cache[msg_id] = now
        kind = "私聊接收"
        if msg_type == "text":
            content = root.find("Content").text
        elif msg_type == "image":
            content = [
                {
                    "type": "image",
                    "data": {
                        "file": root.find("MediaId").text,
                        "url": root.find("PicUrl").text,
                    },
                }
            ]
        elif msg_type == "voice":
            content = [{"type": "record", "data": {"file": root.find("MediaId").text}}]
        elif msg_type == "video":
            content = [{"type": "video", "data": {"file": root.find("MediaId").text}}]
        elif msg_type == "location":
            content = [
                {
                    "type": "json",
                    "data": {
                        "data": {
                            "prompt": root.find("Label").text,
                            "location_x": root.find("Location_X").text,
                            "location_y": root.find("Location_Y").text,
                            "scale": root.find("Scale").text,
                        }
                    },
                }
            ]
        elif msg_type == "link":
            content = [
                {
                    "type": "json",
                    "data": {
                        "data": {
                            "prompt": root.find("Title").text,
                            "description": root.find("Description").text,
                            "url": root.find("Url").text,
                        }
                    },
                }
            ]
        else:
            raise Exception(f" 未定义的消息类型 | 消息: {data}")

    Msg(
        platform="WECHAT",
        kind=kind,
        event="处理",
        user=from_user,
        seq=seq,
        content=content,
    )
    return seq
