# 测试正向代理代码，使用需要安装 flask
import os
import asyncio
import aiohttp
import requests
from flask import Flask
from ssl import SSLContext
from aiohttp import ClientSession


# 设置SOCKS5代理
os.environ["HTTP_PROXY"] = "socks5://127.0.0.1:1080"
os.environ["HTTPS_PROXY"] = "socks5://127.0.0.1:1080"

response = requests.get("http://ifconfig.me")
print(response.text)

import aiohttp
import asyncio
from aiohttp_socks import ProxyConnector


class CustomClientSession(aiohttp.ClientSession):
    def __init__(self, *args, connector=None, **kwargs):
        # SOCKS5 代理配置
        proxy_host = "127.0.0.1"  # SOCKS5 代理地址
        proxy_port = 1080  # SOCKS5 代理端口

        # 如果传入了connector，获取connector中的配置
        ssl_context = getattr(
            connector, "ssl", SSLContext()
        )  # 获取SSL上下文，默认为默认SSLContext
        limit_per_host = getattr(
            connector, "limit_per_host", 500
        )  # 获取连接限制，默认为500
        force_close = getattr(
            connector, "force_close", True
        )  # 获取force_close，默认为True

        # 创建 ProxyConnector，使用传入的connector中的参数
        connector = ProxyConnector(
            host=proxy_host,
            port=proxy_port,
        )

        # 在初始化时设置代理连接器
        super().__init__(*args, connector=connector, **kwargs)


# 使用自定义的 ClientSession 替换默认实现
aiohttp.ClientSession = CustomClientSession


async def fetch(url):
    from aiohttp import WSMessage, ClientWebSocketResponse, TCPConnector

    connector = TCPConnector(limit=10, ssl=SSLContext())
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            return await response.text()


async def main():
    url = "http://ifconfig.me"
    content = await fetch(url)
    print(content)


# 运行测试
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
