"""wiki 页面"""

from config import database_query, database_update, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get

router = APIRouter()


@router.get("/wiki")
async def wiki_get_all():
    """获取所有wiki页面"""
    query = "SELECT id, title, group_name, content FROM system_wiki ORDER BY sort"
    result = await database_query(query)
    return R(status="success", data=result)


@router.post("/wiki")
@monitor_adapter("#内阁_wiki创建")
async def wiki_create(data: dict, account: str = Depends(cookie_account_get)):
    """创建新的wiki页面"""
    if not account:
        return
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
    website_logger.info(
        f"[wiki 创建]{account}-> {data}", extra={"event": "网页日志"}
    )
    return R(status="success")


@router.put("/wiki")
@monitor_adapter("#内阁_wiki更新")
async def wiki_update(data: dict, account: str = Depends(cookie_account_get)):
    """更新wiki页面"""
    if not account:
        return
    update_query = "UPDATE system_wiki SET content = %s WHERE id = %s"
    update_params = (data.get("content", ""), data.get("id", ""))
    await database_update(update_query, update_params)
    website_logger.info(
        f"[wiki 更新]{account}-> {data}", extra={"event": "网页日志"}
    )
    return R(status="success")


@router.put("/wiki/name")
@monitor_adapter("#内阁_wiki名称更新")
async def wiki_update_name(data: dict, account: str = Depends(cookie_account_get)):
    """更新wiki名称（组名或标题）"""
    if not account:
        return
    website_logger.info(
        f"[wiki 名更新]{account}-> {data}", extra={"event": "网页日志"}
    )
    edit_type = data.get("type")

    if edit_type == "group":
        # 更新组名
        old_group = data.get("old_group")
        new_group = data.get("new_group")

        if not old_group or not new_group:
            return R(status="fail", data="组名不能为空")

        # 更新所有属于该组的页面
        update_query = "UPDATE system_wiki SET group_name = %s WHERE group_name = %s"
        await database_update(update_query, (new_group, old_group))

        return R(status="success")

    elif edit_type == "title":
        # 更新页面标题
        page_id = data.get("id")
        new_title = data.get("title")

        if not page_id or not new_title:
            return R(status="fail", data="页面ID及标题不能为空")

        # 更新指定页面的标题
        update_query = "UPDATE system_wiki SET title = %s WHERE id = %s"
        await database_update(update_query, (new_title, page_id))

        return R(status="success")

    else:
        return R(status="fail", data="无效的编辑类型")


@router.put("/wiki/sort")
@monitor_adapter("#内阁_wiki排序")
async def update_wiki_sort(data: dict, account: str = Depends(cookie_account_get)):
    """
    接收前端传回的排序结果，重新赋值 sort
    """
    if not account:
        return

    sort_data = data["order"]
    update_query = "UPDATE system_wiki SET sort = %s WHERE id = %s"
    for item in sort_data:
        await database_update(update_query, (item["sort"], item["id"]))
    website_logger.info(
        f"[wiki 排序]{account}-> {sort_data}", extra={"event": "网页日志"}
    )
    return R(status="success")


@router.put("/wiki/move")
@monitor_adapter("#内阁_wiki组重命名")
async def wiki_move_page(data: dict, account: str = Depends(cookie_account_get)):
    """拖动排序时的组重命名"""
    if not account:
        return
    page_id = data.get("id")
    new_group = data.get("new_group")
    if not page_id or not new_group:
        return R(status="fail", data="参数缺失")
    update_query = "UPDATE system_wiki SET group_name = %s WHERE id = %s"
    await database_update(update_query, (new_group, page_id))
    website_logger.info(
        f"[wiki 组排序]{account}-> {data}", extra={"event": "网页日志"}
    )
    return R(status="success")
