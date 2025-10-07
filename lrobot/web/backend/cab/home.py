"""主页"""

import os

from .base import APIRouter, Query, Response, website_logger, HTTPException
from config import connect, path

router = APIRouter()


@router.get("/map/search")
async def home_search(q: str = Query(...)):
    """主页搜索转发"""
    params = {
        "q": q,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "accept-language": "zh-CN"
    }
    async with connect(use_agent=True) as client:
        try:
            r = await client.get("https://nominatim.openstreetmap.org/search", params=params)
            return r.json()
        except Exception as e:
            website_logger.error(f"[主页]搜索失败-> {q}: {e}", extra={"event": "网页日志"})
            return HTTPException(status_code=500, detail=e)


@router.get("/map/{z}/{x}/{y}.png")
async def home_map_get(z: int, x: int, y: int):
    """请求 OSM 地图"""
    CACHE_DIR = f"{path}/storage/data/map"
    cache_path = os.path.join(CACHE_DIR, str(z), str(x))
    os.makedirs(cache_path, exist_ok=True)
    file_path = os.path.join(cache_path, f"{y}.png")

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return Response(content=data, media_type="image/png")

    url = f"https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
    async with connect(use_agent=True) as client:
        try:
            r = await client.get(url)
            data = r.content
            with open(file_path, "wb") as f:
                f.write(data)
            return Response(content=data, media_type="image/png")
        except Exception as e:
            website_logger.error(f"[主页]地图获取失败-> {z}/{x}/{y}: {e}", extra={"event": "网页日志"})
            return HTTPException(status_code=500, detail=e)
