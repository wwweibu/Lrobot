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
