import json
from config import update_database,query_database
async def add_panel(name,description):
    """面板插入新功能"""
    query = """
        INSERT INTO system_panel (name, description, tasks)
        VALUES (%s, %s, %s)
    """
    empty_tasks = json.dumps([])
    id = await update_database(query, (name, description, empty_tasks))

    url = f"/hjd/static/panel/{id}.png"
    query = "UPDATE system_panel SET url = %s WHERE id = %s"
    await update_database(query, (url, id))


async def add_panel_task(name,task):
    """功能添加任务"""
    query = "SELECT id, tasks FROM system_panel WHERE name = %s"
    result = await query_database(query, (name,))
    if result:
        id = result[0]["id"]
        task_text = result[0]["tasks"]
        tasks = json.loads(task_text or "[]")
        tasks.append({
            "title": task,
            "answers": []
        })

        query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
        await update_database(query, (json.dumps(tasks, ensure_ascii=False), id))




