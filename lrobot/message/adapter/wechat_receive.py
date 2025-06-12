# 微信公众号消息接收
import time
import hashlib
import asyncio
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Request, Response
from message.handler.msg import Msg
from config import config, loggers, monitor_adapter, future


router = APIRouter()
adapter_logger = loggers["adapter"]
_msg_cache = {}


@router.get("/")
def set_callback(signature: str, timestamp: str, nonce: str, echostr: str):
    """回调地址验证"""
    try:
        token = config["WECHAT_TOKEN"]
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()  # 计算SHA1哈希值
        for item in list:
            sha1.update(item.encode("utf-8"))
        hashcode = sha1.hexdigest()

        if hashcode == signature:  # 比对signature与计算出的hashcode
            adapter_logger.debug(
                f"⌈WECHAT⌋ 消息回调配置成功", extra={"event": "回调配置"}
            )
            return Response(content=echostr, media_type="text/plain")
        else:
            raise Exception(
                f"回调配置错误 | 数据不完整: signature-{signature} timestamp-{timestamp} nonce-{nonce} echostr-{echostr}"
            )

    except Exception as e:
        raise Exception(f"回调配置错误 | 错误: {e}")


@router.post("/")
async def LR232_receive(request: Request):
    """接收微信发送的 XML 消息"""
    body = await request.body()
    xml_data = body.decode("utf-8")
    adapter_logger.debug(f"⌈WECHAT⌋ {xml_data}", extra={"event": "消息接收"})
    seq = await handle_wechat_message(xml_data)
    if not seq:
        raise Exception(f" 消息去重 | 消息: {xml_data}")
    try:
        _future = future.get(seq)
        print(seq)
        response = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
        raise Exception(f" 消息超时 | 消息: {xml_data}")
    return response


@monitor_adapter("WECHAT")
async def handle_wechat_message(data):
    """解析微信消息"""
    root = ET.fromstring(data)
    # TODO 消息类型解析
    msg_type = root.find("MsgType").text
    from_user = root.find("FromUserName").text
    to_user = root.find("ToUserName").text
    content = root.find("Content").text if root.find("Content") is not None else ""
    seq = root.find("MsgId").text
    now = time.time()
    if seq in _msg_cache and (now - _msg_cache[seq] < 20):
        return
    _msg_cache[seq] = now
    print(_msg_cache)
    Msg(
        robot="WECHAT",
        kind="私聊文字消息",
        event="处理",
        source=from_user,
        seq=seq,
        content=content,
    )
    return seq
