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

    query_select = "SELECT tasks FROM system_panel WHERE id = %s"
    rows = await database_query(query_select, (feature_id,))
    if not rows:
        return {"error": "指定 id 不存在"}
    old_tasks = json.loads(rows[0]["tasks"] or "[]")

    diff = {}

    for task_idx, (old_task, new_task) in enumerate(zip(old_tasks, tasks)):
        old_answers = old_task.get("answers", [])
        new_answers = new_task.get("answers", [])

        if len(new_answers) > len(old_answers):
            added = new_answers[len(old_answers):]
            diff = {"action": "新增", "task_index": task_idx, "answers": added}
            break

        elif len(new_answers) < len(old_answers):
            removed = [a for a in old_answers if a not in new_answers]
            diff = {"action": "删除", "task_index": task_idx, "answers": removed}
            break

    # 转换为 JSON 字符串以存入数据库
    tasks_json = json.dumps(tasks, ensure_ascii=False)
    query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
    await database_update(query, (tasks_json, feature_id))
    website_logger.info(f"[{account}] {diff['action']}: {tasks[diff['task_index']]['title']}->{diff['answers']}",
                        extra={"event": "管理操作"})

    return {"message": "更新成功"}
