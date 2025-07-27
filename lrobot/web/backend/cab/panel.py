"""功能展板"""

import json
from fastapi import APIRouter, Request, Depends
from .cookie import cookie_account_get
from config import loggers, database_update, database_query


router = APIRouter()
website_logger = loggers["website"]


@router.get("/firefly")
async def firefly_get():
    """获取展板信息"""
    query = "SELECT id, name, description, url, tasks FROM system_panel"
    rows = await database_query(query)
    result = []
    for row in rows:
        id = row["id"]
        name = row["name"]
        description = row["description"]
        url = row["url"]
        tasks = json.loads(row["tasks"])
        result.append(
            {
                "id": id,
                "name": name,
                "description": description,
                "imageUrl": url,
                "tasks": tasks,
            }
        )
    return result


@router.post("/firefly")
async def firefly_update(request: Request, account: str = Depends(cookie_account_get)):
    """上传展板评论"""
    data = await request.json()

    feature_id = data.get("id")
    tasks = data.get("tasks", [])

    if feature_id is None:
        return {"error": "缺少参数 id"}

    # 转换为 JSON 字符串以存入数据库
    tasks_json = json.dumps(tasks, ensure_ascii=False)
    query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
    await database_update(query, (tasks_json, feature_id))
    website_logger.info(f"[{account}] 上传评论: {tasks}", extra={"event": "管理操作"})

    return {"message": "更新成功"}
