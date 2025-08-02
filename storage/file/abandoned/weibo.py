# 微博粉丝服务平台消息接收/发送
import json
import time
import hashlib
import requests
from fastapi import APIRouter, Response, Request
from config import config,loggers

# 以下为接收
router = APIRouter()
adapter_logger = loggers["adapter"]


@router.get("/")
def set_callback(signature: str, timestamp: str, nonce: str, echostr: str):
    """回调地址验证"""
    try:
        token = config["WEIBO_SECRET"]
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()  # 计算SHA1哈希值
        for item in list:
            sha1.update(item.encode("utf-8"))
        hashcode = sha1.hexdigest()

        if hashcode == signature:  # 比对signature与计算出的hashcode
            adapter_logger.debug(
                f"⌈WEIBO⌋ 消息回调配置成功", extra={"event": "回调配置"}
            )
            return Response(content=echostr, media_type="text/plain")
        else:
            raise Exception(
                f"回调配置错误 | 数据不完整: signature-{signature} timestamp-{timestamp} nonce-{nonce} echostr-{echostr}"
            )

    except Exception as e:
        raise Exception(f"回调配置错误 | 错误: {e}")


@router.post("/")
async def handle_post(request: Request):
    print(request.body())

# 以下为发送
# 请求的基础信息
APP_KEY = ""  # 替换为你的 APP ID
APP_SECRET = ""  # 替换为你的 Token



def get_token():
    # 请求头
    headers = {
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": uri,  # 可以使用随机生成的 UUID
    }

    # 发送 POST 请求
    response = requests.post("https://api.weibo.com/oauth2/access_token", data=headers)

    # 打印结果
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")


def get_weibo():
    # 请求头
    headers = {"access_token": access_token, "screen_name": "whu推协"}

    # 发送 POST 请求
    response = session.get(
        "https://api.weibo.com/2/friendships/friends.json", params=headers
    )

    # 打印结果
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")


def get_mentions():
    # 请求头
    headers = {"access_token": access_token}

    # 发送 POST 请求
    response = session.get(
        "https://api.weibo.com/2/statuses/mentions.json", params=headers
    )

    # 打印结果
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")


get_mentions()
