"""日志查询界面"""

import re
from typing import Optional
from datetime import datetime
from fastapi import APIRouter
from config import mongo_get

router = APIRouter()
mongo_db = mongo_get()


@router.get("/logs")
async def log_get(
    page: int = 1,
    page_size: int = 100,
    level: Optional[str] = None,
    source: Optional[str] = None,
    event: Optional[str] = None,
    keyword: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
):
    """日志获取"""
    query = {}

    if level:
        query["level"] = level.upper()
    if source:
        query["source"] = source
    if event:
        query["event"] = event
    if start_time and end_time:
        try:
            st = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            et = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            query["time"] = {"$gte": st, "$lte": et}
        except ValueError:
            pass
    if keyword:
        try:
            re.compile(keyword)
            query["message"] = {"$regex": keyword, "$options": "i"}
        except re.error:
            # 如果是非法正则，就进行纯字符串匹配（转义特殊字符）
            safe_keyword = re.escape(keyword)
            query["message"] = {"$regex": safe_keyword, "$options": "i"}

    skip = (page - 1) * page_size
    total = await mongo_db.system_log.count_documents(query)
    cursor = (
        mongo_db.system_log.find(query).sort("time", -1).skip(skip).limit(page_size)
    )
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)

    return {"data": results, "total": total}
