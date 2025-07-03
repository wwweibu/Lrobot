from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query
from config import get_mongo_db

router = APIRouter()
mongo_db = get_mongo_db()

@router.get("/logs")
async def get_logs(
    page: int = 1,
    page_size: int = 100,
    level: Optional[str] = None,
    source: Optional[str] = None,
    event: Optional[str] = None,
    keyword: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
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
        # 正则匹配 message 字段
        query["message"] = {"$regex": keyword, "$options": "i"}

    print(query)

    skip = (page - 1) * page_size
    total = await mongo_db.system_log.count_documents(query)
    cursor = mongo_db.system_log.find(query).sort("time", -1).skip(skip).limit(page_size)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    print(results)

    return {"data": results, "total": total}