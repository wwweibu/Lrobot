"""令牌刷新"""

import time

from config import config, loggers, connect, scheduler_add, storage

TOKEN_API = {  # 请求地址
    "WECHAT": "https://api.weixin.qq.com/cgi-bin/stable_token",
    "LR232": "https://bots.qq.com/app/getAppAccessToken",
}

AUTH_PARAMS = {  # 请求参数
    "WECHAT": {
        "grant_type": "client_credential",
        "appid": config["WECHAT_ID"],
        "secret": config["WECHAT_SECRET"],
    },
    "LR232": {
        "appId": config["LR232_ID"],
        "clientSecret": config["LR232_SECRET"],
    },
}

adapter_logger = loggers["adapter"]

access_tokens = storage.setdefault("access_tokens",
                                   {"WECHAT": {"token": "", "expires_at": 0}, "LR232": {"token": "", "expires_at": 0}})


async def update_tokens(platform_list):
    """检查并刷新即将过期的令牌"""
    current_time = time.time()

    async def update_token(client, platform):
        """刷新单平台"""
        response = await client.post(
            TOKEN_API[platform],
            json=AUTH_PARAMS[platform],
            timeout=10,
        )
        token_data = response.json()
        # 校验响应
        if "access_token" not in token_data:
            raise Exception(f"[令牌刷新]⌈{platform}⌋请求失败-> 无 access_token: {token_data}")
        expires_in = int(token_data.get("expires_in", 10800))  # 默认 3h
        access_token = token_data["access_token"]
        access_tokens[platform] = {
            "token": access_token,
            "expires_at": current_time + expires_in
        }
        adapter_logger.debug(
            f"[令牌刷新]⌈{platform}⌋-> {access_token}: {expires_in}",
            extra={"event": "消息发送"},
        )

    # 提前 60 秒刷新
    platforms_to_refresh = [
        p for p in platform_list
        if p in access_tokens and current_time >= access_tokens[p]["expires_at"] - 60
    ]

    if platforms_to_refresh:
        async with connect(True) as http_client:
            for p in platforms_to_refresh:
                await update_token(http_client, p)


async def refresh_tokens(platform_list):
    """刷新各平台令牌"""
    scheduler_add(update_tokens, platform_list, interval=60, at_once=True)
