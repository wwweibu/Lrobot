"""wiki 页面"""

from fastapi import APIRouter

from config import database_query, database_update

router = APIRouter()


@router.get("/wiki")
async def wiki_get_all():
    """获取所有wiki页面"""
    query = "SELECT id, title, group_name, content FROM system_wiki ORDER BY sort"
    result = await database_query(query)
    return result


@router.post("/wiki")
async def wiki_create(data: dict):
    """创建新的wiki页面"""
    title = data.get("title")
    group_name = data.get("group_name")
    content = data.get("content", "")
    if title == group_name:
        sort_query = "SELECT MIN(sort) AS target_sort FROM system_wiki WHERE group_name = %s"
    else:
        sort_query = "SELECT MAX(sort) AS target_sort FROM system_wiki WHERE group_name = %s"

    # 获取整个表的最大sort值作为默认值
    max_table_query = "SELECT MAX(sort) AS max_table_sort FROM system_wiki"
    max_table_res = await database_query(max_table_query)
    default_sort = int(max_table_res[0]["max_table_sort"]) + 1 if max_table_res else 1

    sort_res = await database_query(sort_query, (group_name,))
    target_sort = sort_res[0]["target_sort"]
    if target_sort:
        target_sort = int(target_sort)
        if title != group_name:
            target_sort += 1
    else:
        target_sort = default_sort

    shift_query = "UPDATE system_wiki SET sort = sort + 1 WHERE sort >= %s"
    await database_update(shift_query, (target_sort,))
    insert_query = "INSERT INTO system_wiki (title, group_name, content, sort) VALUES (%s, %s, %s, %s)"
    await database_update(insert_query, (title, group_name, content, target_sort))
    return {"success": True}


@router.put("/wiki")
async def wiki_update(data: dict):
    """更新wiki页面"""
    update_query = "UPDATE system_wiki SET content = %s WHERE id = %s"
    update_params = (data.get("content", ""), data.get("id", ""))
    await database_update(update_query, update_params)
    return {"success": True}


@router.put("/wiki/name")
async def wiki_update_name(data: dict):
    """更新wiki名称（组名或标题）"""
    edit_type = data.get("type")

    if edit_type == "group":
        # 更新组名
        old_group = data.get("old_group")
        new_group = data.get("new_group")

        if not old_group or not new_group:
            return {"success": False, "message": "组名不能为空"}

        # 更新所有属于该组的页面
        update_query = "UPDATE system_wiki SET group_name = %s WHERE group_name = %s"
        await database_update(update_query, (new_group, old_group))

        return {"success": True}

    elif edit_type == "title":
        # 更新页面标题
        page_id = data.get("id")
        new_title = data.get("title")

        if not page_id:
            return {"success": False, "message": "页面ID不能为空"}

        # 更新指定页面的标题
        update_query = "UPDATE system_wiki SET title = %s WHERE id = %s"
        await database_update(update_query, (new_title, page_id))

        return {"success": True}

    else:
        return {"success": False, "message": "无效的编辑类型"}


@router.put("/wiki/sort")
async def update_wiki_sort(sort_data: list[dict]):
    """
    接收前端传回的排序结果，重新赋值 sort
    """
    update_query = "UPDATE system_wiki SET sort = %s WHERE id = %s"
    for item in sort_data:
        await database_update(update_query, (item["sort"], item["id"]))
    return {"success": True}


@router.put("/wiki/move")
async def wiki_move_page(data: dict):
    """拖动排序时的组重命名"""
    page_id = data.get("id")
    new_group = data.get("new_group")
    if not page_id or not new_group:
        return {"success": False, "message": "参数缺失"}
    update_query = "UPDATE system_wiki SET group_name = %s WHERE id = %s"
    await database_update(update_query, (new_group, page_id))
    return {"success": True}
