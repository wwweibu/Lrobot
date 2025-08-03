"""微信开放平台测试代码"""
import hashlib
import time
import requests
import json

# 请求的基础信息
APP_ID = ""  # 替换为你的 APP ID
TOKEN = ""  # 替换为你的 Token
ACCOUNT = ""  # 替换为你的账户
key = ""
access_token = ""
task_id1 = ""


def generate_sign(token, timestamp, nonce, body):
    """
    根据文档生成签名 sign = md5(Token + str(unix_timestamp) + nonce + md5(body))
    """
    body_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sign_str = f"{token}{timestamp}{nonce}{body_md5}"
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    return sign


def send_request():
    # 时间戳和随机字符串
    timestamp = int(time.time())
    nonce = "abc"  # 这里可以使用更复杂的随机字符串
    url = "https://openaiapi.weixin.qq.com/v2/token"

    # 请求体
    body = json.dumps({"account": ACCOUNT})

    # 生成签名
    sign = generate_sign(TOKEN, timestamp, nonce, body)

    # 请求头
    headers = {
        "X-APPID": APP_ID,
        "request_id": "",  # 可以使用随机生成的 UUID
        "timestamp": str(timestamp),
        "nonce": nonce,
        "sign": sign,
        "content-type": "application/json",
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=body)

    # 打印结果
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")


def import_simple_qna():
    # 时间戳和随机字符串
    timestamp = int(time.time())
    nonce = "abc"  # 这里可以用随机生成的字符串
    url = "https://openaiapi.weixin.qq.com/v2/bot/import/json"

    # 请求体
    body = json.dumps(
        {
            "mode": 0,
            "data": [
                {
                    "skill": "AAA",
                    "intent": "BBC",
                    "threshold": "0.9",
                    "disable": False,
                    "questions": ["q", "q2"],
                    "answers": ["a"],
                }
            ],
        }
    )

    # 生成签名
    sign = generate_sign(TOKEN, timestamp, nonce, body)

    # 请求头
    headers = {
        "content-type": "application/json",
        "X-OPENAI-TOKEN": access_token,
        "request_id": ACCOUNT,
        "timestamp": str(timestamp),
        "nonce": nonce,
        "sign": sign,
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=body)

    # 打印响应结果
    if response.status_code == 200:
        print("导入成功！返回数据：")
        print(response.json())
    else:
        print(f"导入失败，状态码：{response.status_code}")
        print(response.text)


def query_qna(task_id):
    timestamp = int(time.time())
    nonce = "abc"  # 这里可以用随机生成的字符串
    url = "https://openaiapi.weixin.qq.com/v2/async/fetch"

    # 请求体
    body = json.dumps({"task_id": task_id})

    # 生成签名
    sign = generate_sign(TOKEN, timestamp, nonce, body)


if __name__ == "__main__":
    send_request()
    # import_simple_qna()
