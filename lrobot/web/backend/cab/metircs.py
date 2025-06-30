# TODO 展示其他的
from fastapi import APIRouter
from config import query_database

router = APIRouter()


# 获取监控数据
@router.get("/metrics")
async def get_metrics():
    query = "SELECT * FROM system_metrics ORDER BY timestamp ASC"
    records = await query_database(query)
    return {"data": records}


@router.get("/logs")
async def get_logs(
    level: str = None,
    source: str = None,
    event: str = None,
    keyword: str = None,
    start_time: str = None,
    end_time: str = None,
):
    query = "SELECT * FROM system_log WHERE 1=1"
    params = []

    if level:
        query += " AND level = ?"
        params.append(level)
    if source:
        query += " AND source = ?"
        params.append(source)
    if event:
        query += " AND event = ?"
        params.append(event)
    if keyword:
        query += " AND message LIKE ?"
        params.append(f"%{keyword}%")
    if start_time:
        query += " AND time >= ?"
        params.append(start_time)
    if end_time:
        query += " AND time <= ?"
        params.append(end_time)

    results = await query_database(query, tuple(params))
    return {"data": results}
