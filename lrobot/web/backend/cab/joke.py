"""笑话获取"""

from cachetools import TTLCache

from logic import ip_ban
from config import database_update, database_query, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, Dict, ip_get, Request

router = APIRouter()
ip_cache = TTLCache(maxsize=20000, ttl=10)

@router.post("/joke")
@monitor_adapter("#活动_笑话添加")
async def joke_add(data: Dict):
    """插入到 jokes 表中"""
    try:
        query = "INSERT INTO system_joke (text) VALUES (%s)"
        await database_update(query, (data["text"],))
        return R(status="success", data=data["text"])
    except Exception as e:
        website_logger.error(f"[笑话]写入失败 -> {e}", extra={"event": "网页日志"})
        return R(status="fail", data=e)


@router.get("/joke")
async def joke_get(ip=Depends(ip_get)):
    """返回笑话"""
    if ip != "222.20.193.18":  # 武汉大学 ip
        ip_cache[ip] = ip_cache.get(ip, 0) + 1
        if ip_cache[ip] >= 10:
            await ip_ban(ip)
            ip_cache[ip] = 0
            joke = "无法获取启发内容，或许这就是认知的边界？"
            return R(status="success", data=joke)
    result = await database_query(
        "SELECT text FROM system_joke ORDER BY RAND() LIMIT 1;"
    )
    joke = result[0]["text"] if result else "无法获取启发内容，或许这就是认知的边界？"
    return R(status="success", data=joke)


@router.put("/joke")
async def joke_put(ip=Depends(ip_get)):
    """前端心跳，用于清除短期计数"""
    if ip in ip_cache:
        ip_cache[ip] = max(ip_cache[ip] - 1, 0)
    return R(status="success")
