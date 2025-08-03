"""B 站 API 调用"""

import os
import json
import time
import mimetypes

from config import config, loggers, connect, future

adapter_logger = loggers["adapter"]


async def request_deal(url, method, params, tag, files=None, headers=None):
    """请求统一处理"""
    if not headers:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Origin": "https://www.bilibili.com",
        }
    cookies = {"SESSDATA": config["BILI_SESSDATA"]}
    client = connect()
    try:
        if method == "get":
            response = await client.get(
                url, headers=headers, params=params, cookies=cookies
            )
        else:
            response = await client.post(
                url, headers=headers, data=params, files=files, cookies=cookies
            )

    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  {type(e).__name__}: {e} | data: {params}")

    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {params}"
        )

    json_resp = response.json()
    if json_resp.get("code") != 0:
        raise Exception(f"{tag} 请求失败 -> {json_resp} | data: {params}")

    adapter_logger.info(
        f"[BILI] {tag} 成功 -> {params} | {json_resp}",
        extra={"event": "消息发送"},
    )
    return json_resp


async def bili_signature(sign):
    """私聊签名，需要较长时间审核"""
    url = "https://api.bilibili.com/x/member/web/sign/update"
    params = {"user_sign": sign, "csrf": config["BILI_JCT"]}
    await request_deal(url, "post", params, "私聊签名")


async def bili_dispatch(
        content, kind=None, user=None, group=None, num=None, order=None, seq=None
):
    """私聊发送，返回消息序号列表"""
    url = "https://api.vc.bilibili.com/web_im/v1/web_im/send_msg"
    content_parts = []
    image_parts = []
    for item in content:
        if item["type"] == "image":
            if "file" in item["data"]:
                image_parts.append(item["data"]["file"])
            elif "summary" in item["data"]:
                summary = item["data"]["summary"]
                content_parts.append(summary)
        elif item["type"] == "text":
            text = item["data"].get("text", "")
            content_parts.append(text)
    final_content = "".join(content_parts)
    base_params = {
        "msg[sender_uid]": config["BILI_UID"],
        "msg[receiver_id]": user,
        "msg[receiver_type]": 1,
        "msg[dev_id]": config["BILI_UUID"],
        "msg[timestamp]": str(int(time.time())),
        "csrf_token": config["BILI_JCT"],
        "csrf": config["BILI_JCT"],
    }
    seq = []
    if final_content:
        params = base_params.copy()
        params["msg[msg_type]"] = 1
        params["msg[new_face_version]"] = 1
        params["msg[content]"] = json.dumps({"content": final_content})
        response = await request_deal(url, "post", params, "私聊发送")
        seq.append(response.get("data", {}).get("msg_key"))

    for file in image_parts:
        params = base_params.copy()
        params["msg[msg_type]"] = 2
        file_data = await bili_file_upload(file)
        params["msg[content]"] = json.dumps(
            {"url": file_data[0], "height": file_data[1], "width": file_data[2]})
        response = await request_deal(url, "post", params, "私聊发送")
        seq.append(response.get("data", {}).get("msg_key"))
    future.set(num, seq)


async def bili_withdraw(seq, user=None, kind=None):
    """私聊撤回"""
    url = "https://api.vc.bilibili.com/web_im/v1/web_im/send_msg"
    params = {
        "msg[sender_uid]": config["BILI_UID"],
        "msg[receiver_id]": user,
        "msg[receiver_type]": 1,
        "msg[msg_type]": 5,
        "msg[dev_id]": config["BILI_UUID"],
        "msg[timestamp]": str(int(time.time())),
        "msg[content]": seq,
        "csrf_token": config["BILI_JCT"],
        "csrf": config["BILI_JCT"],
    }
    await request_deal(url, "post", params, "私聊撤回")


async def bili_file_upload(filepath, type=None, url=None):
    """文件上传"""
    mime_type, _ = mimetypes.guess_type(filepath)
    url = "https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs"
    params = {"category": "daily",
              "csrf": config["BILI_JCT"],
              "biz": "im"}
    files = {
        "file_up": (os.path.basename(filepath), open(filepath, "rb"), mime_type)
    }

    response = await request_deal(url, "post", params, "私聊文件上传", files)
    data = response["data"]
    return [data["image_url"], data["image_height"], data["image_width"]]


async def bili_test(num):
    """私聊测试"""
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://link.bilibili.com",
        "referer": "https://link.bilibili.com/p/center/index",
        "sec-ch-ua": '"Microsoft Edge";v="137", "Not=A?Brand";v="8", "Chromium";v="137"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    }

    params = {
        "room_id": config["BILI_LIVE_ID"],
        "area_v2": 702,
        "platform": "pc_link",
        "csrf": config["BILI_JCT"],
        "csrf_token": config["BILI_JCT"],
        "type": 2
    }
    params = sign_data(params)
    response = await request_deal(url, "post", params, "私聊测试", headers)
    print(response)


def sign_data(data):
    data.update(
        {
            "access_key": "",
            "ts": str(int(time.time())),
            "build": "9343",
            "version": "7.17.0.9343",
            "appkey": "aae92bc66f3edfab",
        }
    )
    # 按照 key 重排参数
    signed_data = dict(sorted(data.items()))
    # 签名
    from hashlib import md5
    from urllib.parse import urlencode
    sign = md5(
        (urlencode(signed_data, encoding="utf-8") + "af125a0d5279fd576c1b4418a3e8276d").encode(
            encoding="utf-8"
        )
    ).hexdigest()
    # 添加到尾部
    signed_data.update({"sign": sign})
    return signed_data

# TODO 直播间信息更改
