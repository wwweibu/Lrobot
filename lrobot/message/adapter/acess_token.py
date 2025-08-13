"""令牌刷新"""

import time
import asyncio

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
print(111)
print(access_tokens)


async def update_tokens(platform_list):
    """检查并刷新即将过期的令牌"""
    client = connect(True)
    current_time = time.time()

    async def update_token(platform):
        """刷新单平台"""
        try:
            response = await client.post(
                TOKEN_API[platform],
                json=AUTH_PARAMS[platform],
                timeout=10,
            )
            token_data = response.json()

            # 校验响应
            if "access_token" not in token_data:
                adapter_logger.error(
                    f"⌈{platform}⌋ 令牌刷新失败 -> 无 access_token，响应: {token_data}",
                    extra={"event": "令牌刷新"},
                )
                return

            expires_in = int(token_data.get("expires_in", 10800))  # 默认 3h
            access_tokens[platform] = {
                "token": token_data["access_token"],
                "expires_at": current_time + expires_in
            }

            adapter_logger.debug(
                f"⌈{platform}⌋ 令牌有效期 {expires_in}",
                extra={"event": "令牌刷新"},
            )

        except Exception as e:
            adapter_logger.exception(
                f"⌈{platform}⌋ 令牌刷新失败 -> {e}",
                extra={"event": "令牌刷新"},
            )

    # 提前 60 秒刷新
    platforms_to_refresh = [
        p for p in platform_list
        if p in access_tokens and current_time >= access_tokens[p]["expires_at"] - 60
    ]

    if platforms_to_refresh:
        for p in platforms_to_refresh:
            await update_token(p)


async def refresh_tokens(platform_list):
    """刷新各平台令牌"""
    await update_tokens(platform_list)
    asyncio.create_task(scheduler_add(update_tokens, platform_list, interval=60))
