"""笑话获取"""

from logic import ip_check
from config import database_update, database_query, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, Dict, ip_get, cookie_account_get

router = APIRouter()


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
    try:
        if await ip_check(ip):
            website_logger.error(f"[IP]{ip}-> 封禁 10 分钟", extra={"event": "网页日志"})
            return R(status="fail")
        result = await database_query(
            "SELECT text FROM system_joke ORDER BY RAND() LIMIT 1;"
        )
        joke = result[0]["text"] if result else "无法获取启发内容，或许这就是认知的边界？"
        return R(status="success", data=joke)
    except Exception as e:
        website_logger.error(f"[笑话]获取失败-> {e}", extra={"event": "网页日志"})
        return R(status="fail")
