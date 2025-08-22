"""测试接口及 ip逻辑"""

import os
from fastapi.responses import FileResponse
from fastapi import APIRouter, Request, Response, HTTPException, Query

from logic import ip_check
from config import path, loggers, database_update, database_query, connect


router = APIRouter()
command_path = path / "storage/config/command.yaml"
users_path = path / "storage/config/user.yaml"
website_logger = loggers["website"]


@router.get("/test")
async def test():
    """测试端口"""
    return Response(content="Hello World!", media_type="text/plain")


@router.get("/static/{file_path:path}")
async def static_file(file_path: str):
    """静态资源文件"""
    base_path = path / "storage/file/resource"
    requested_path = (base_path / file_path).resolve()
    if not str(requested_path).startswith(str(base_path)):
        raise HTTPException(status_code=400, detail="无法访问上层文件或非法路径")
    if requested_path.exists():
        return FileResponse(requested_path)
    else:
        raise HTTPException(status_code=404, detail=f"文件未找到 | 位置: {file_path}")


@router.post("/answer")
async def answer(data: dict):
    """插入到 jokes 表中"""
    text = data.get("text")
    query = "INSERT INTO system_joke (text) VALUES (%s)"
    await database_update(query, (text,))
    return {"success": True, "message": "Answer submitted successfully!"}


@router.get("/joke")
async def joke_get(request: Request):
    """返回一个笑话"""
    ip = request.client.host
    if await ip_check(ip):
        website_logger.error(f" IP {ip} 被封禁 10 分钟", extra={"event": "超频访问"})
        return {"joke": ""}
    result = await database_query(
        "SELECT text FROM system_joke ORDER BY RAND() LIMIT 1;"
    )
    joke = result[0]["text"] if result else "No jokes found."
    return {"joke": joke}


@router.get("/map/search")
async def search(q: str = Query(...)):
    params = {
        "q": q,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "accept-language": "zh-CN"
    }
    client = connect()
    r = await client.get("https://nominatim.openstreetmap.org/search", params=params)
    return r.json()


@router.get("/map/{z}/{x}/{y}.png")
async def proxy_tile(z: int, x: int, y: int):
    """请求 OSM 地图"""
    CACHE_DIR = f"{path}/storage/data/map"
    OSM_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    cache_path = os.path.join(CACHE_DIR, str(z), str(x))
    os.makedirs(cache_path, exist_ok=True)
    file_path = os.path.join(cache_path, f"{y}.png")

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return Response(content=data, media_type="image/png")

    url = OSM_URL.format(s="a", z=z, x=x, y=y)  # 可以轮询 a/b/c 子域
    client = connect()
    r = await client.get(url)
    data = r.content
    with open(file_path, "wb") as f:
        f.write(data)

    return Response(content=data, media_type="image/png")
