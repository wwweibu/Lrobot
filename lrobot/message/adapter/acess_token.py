# 刷新各平台令牌
import time
import asyncio
from config import config,loggers,connect


adapter_logger = loggers["adapter"]

access_tokens = {
    "WECHAT": {"token": "", "expires_at": 0},
    "LR232": {"token": "", "expires_at": 0},
}  # 各平台令牌

TOKEN_API = {
    "WECHAT": "https://api.weixin.qq.com/cgi-bin/stable_token",
    "LR232": "https://bots.qq.com/app/getAppAccessToken",
}

AUTH_PARAMS = {
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


async def refresh_tokens(platform_list):
    """刷新各平台令牌"""
    while True:
        current_time = time.time()
        platforms_to_refresh = [
            p for p in platform_list if p in access_tokens
        ]  # 仅刷新配置参数的平台
        client = connect(True)
        for platform in platforms_to_refresh:
            data = access_tokens.get(platform)

            if current_time >= data["expires_at"] + 60:
                try:
                    response = await client.post(
                        TOKEN_API[platform],
                        json=AUTH_PARAMS[platform],
                        timeout=10,
                    )
                    token_data = response.json()
                    access_tokens[platform]["token"] = token_data.get(
                        "access_token", ""
                    )
                    expires_in = int(
                        token_data.get("expires_in", 10800)
                    )  # 默认3小时
                    access_tokens[platform]["expires_at"] = (
                        current_time + expires_in
                    )
                    adapter_logger.debug(
                        f"⌈{platform}⌋令牌有效期{expires_in}",
                        extra={"event": "令牌刷新"},
                    )
                except Exception as e:
                   adapter_logger.error(
                        f"⌈{platform}⌋令牌刷新失败: {e}",
                        extra={"event": "令牌刷新"},
                   )

        await asyncio.sleep(60)  # 每分钟检查一次
