import json
from fastapi import APIRouter, Request, Depends
from .cookie import get_account_from_cookie
from config import loggers,update_database,query_database


router = APIRouter()
website_logger = loggers["website"]

@router.get("/firefly")
async def get_firefly():
    query = "SELECT id, name, description, url, tasks FROM system_panel"
    rows = await query_database(query)
    result = []
    for row in rows:
        id = row["id"]
        name = row["name"]
        description = row["description"]
        url = row["url"]
        tasks = json.loads(row["tasks"])
        result.append({
            "id": id,
            "name": name,
            "description": description,
            "imageUrl": url,
            "tasks": tasks
        })
    return result

@router.post("/firefly")
async def update_firefly(request: Request,account: str = Depends(get_account_from_cookie)):
    data = await request.json()

    feature_id = data.get("id")
    tasks = data.get("tasks", [])

    if feature_id is None:
        return {"error": "缺少参数 id"}

    # 转换为 JSON 字符串以存入数据库
    tasks_json = json.dumps(tasks, ensure_ascii=False)
    query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
    await update_database(query, (tasks_json, feature_id))
    website_logger.info(f"{account} 上传答案:{tasks}",
                        extra={"event": "请求成功"})

    return {"message": "更新成功"}