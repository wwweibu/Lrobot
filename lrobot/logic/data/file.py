# TODO 获取文件相关命令
import httpx


async def download_file(path, url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # 如果失败抛出异常
        with open(path, "wb") as f:
            f.write(response.content)
