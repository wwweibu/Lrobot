"""面板展示相关"""

import json

from config import database_update, database_query


async def panel_add(name, description):
    """面板插入新功能"""
    query = """
        INSERT INTO system_panel (name, description, tasks)
        VALUES (%s, %s, %s)
    """
    empty_tasks = json.dumps([])
    id = await database_update(query, (name, description, empty_tasks))

    url = f"/hjd/static/panel/{id}.png"
    query = "UPDATE system_panel SET url = %s WHERE id = %s"
    await database_update(query, (url, id))


async def panel_task_add(name, task):
    """功能添加任务"""
    query = "SELECT id, tasks FROM system_panel WHERE name = %s"
    result = await database_query(query, (name,))
    if result:
        id = result[0]["id"]
        task_text = result[0]["tasks"]
        tasks = json.loads(task_text or "[]")
        tasks.append({"title": task, "answers": []})

        query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
        await database_update(query, (json.dumps(tasks, ensure_ascii=False), id))


async def panel_task_edit(name, index, new_title):
    """修改某个面板中的任务标题"""
    index = int(index)
    query = "SELECT id, tasks FROM system_panel WHERE name = %s"
    result = await database_query(query, (name,))

    if not result:
        raise ValueError(f"未找到名称为 {name} 的面板")

    id = result[0]["id"]
    task_text = result[0]["tasks"]
    tasks = json.loads(task_text or "[]")

    if index < 0 or index >= len(tasks):
        raise IndexError(f"任务编号 {index} 越界，当前任务数为 {len(tasks)}")

    tasks[index]["title"] = new_title

    update_query = "UPDATE system_panel SET tasks = %s WHERE id = %s"
    await database_update(update_query, (json.dumps(tasks, ensure_ascii=False), id))
