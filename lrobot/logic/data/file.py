import os
from config import connect

async def download_file(path, url):
    client = connect()
    response = await client.get(url)
    response.raise_for_status()  # 如果失败抛出异常
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(response.content)
