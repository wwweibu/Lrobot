from config import config,loggers,connect

adapter_logger = loggers["adapter"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Origin": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
}

async def bili_get_info():
    """私聊查询账号(信息)"""
    client = connect()
    url = "https://api.bilibili.com/x/member/web/account"
    cookies = {
        "SESSDATA": config["BILI_SESSDATA"]
    }
    response = await client.get(url, cookies=cookies, headers=headers)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[BILI]账号信息 -> {response.json()['data']}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"账号信息查询失败 -> [{response.status_code}]{response.text}")

async def bili_set_sign(sign:str):
    """私聊修改(账号)签名，需要较长时间审核"""
    client = connect()
    url = "https://api.bilibili.com/x/member/web/sign/update"
    cookies = {
        "SESSDATA": config["BILI_SESSDATA"]
    }
    data = {
        "user_sign": sign,
        "csrf": config["BILI_JCT"]
    }
    response = await client.post(url, headers=headers, data=data, cookies=cookies)
    if response.status_code == 200:
        adapter_logger.debug(
            f"[BILI]修改签名 -> {sign}", extra={"event": "消息发送"}
        )
    else:
        raise Exception(f"修改签名失败 -> [{response.status_code}]{response.text}")


