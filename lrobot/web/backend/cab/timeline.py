"""时间轴页面"""

import json

from config import database_update, database_query, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Dict, Query


router = APIRouter()


@router.get("/nodes")
async def node_get():
    """获取时间节点"""
    query = "SELECT node_id AS id, date, event, tag FROM system_timeline"
    rows = await database_query(query)
    return R(status="success", data=rows)


@router.post("/nodes")
@monitor_adapter("#内阁_节点创建")
async def node_create(data: Dict, account: str = Depends(cookie_account_get)):
    """创建时间节点"""
    if not account:
        return
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        return R(status="fail", data="缺少 date 或 event 字段")

    # 获取最大 node_id
    max_id_query = "SELECT MAX(node_id) as max_id FROM system_timeline"
    result = await database_query(max_id_query)
    next_node_id = (result[0]["max_id"] or 0) + 1

    insert_query = """
        INSERT INTO system_timeline (node_id, date, event, tag)
        VALUES (%s, %s, %s, %s)
    """
    await database_update(insert_query, (next_node_id, date_val, event_val, tag_val))
    website_logger.info(
        f"[时间点创建]{account}-> {next_node_id},{date_val},{event_val},{tag_val}",
        extra={"event": "网页日志"},
    )
    return R(status="success", data={"id": next_node_id, "date": date_val, "event": event_val, "tag": tag_val})


@router.put("/nodes")
@monitor_adapter("#内阁_节点更新")
async def node_update(data: Dict, account: str = Depends(cookie_account_get)):
    """更新时间节点"""
    if not account:
        return
    node_id = data.get("id")
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        return R(status="fail", data="缺少 date 或 event 字段")

    check_query = "SELECT 1 FROM system_timeline WHERE node_id = %s"
    exist = await database_query(check_query, (node_id,))
    if not exist:
        return R(status="fail", data="节点不存在")

    update_query = """
        UPDATE system_timeline SET date = %s, event = %s, tag = %s WHERE node_id = %s
    """
    await database_update(update_query, (date_val, event_val, tag_val, node_id))
    website_logger.info(
        f"[时间点更新]{account}-> {node_id}, {date_val}, {event_val}, {tag_val}",
        extra={"event": "网页日志"},
    )
    return R(status="success", data={"id": node_id, "date": date_val, "event": event_val, "tag": tag_val})


@router.delete("/nodes")
@monitor_adapter("#内阁_节点删除")
async def node_delete(data: str = Query(...), account: str = Depends(cookie_account_get)):
    """删除时间节点"""
    if not account:
        return
    data_dict = json.loads(data)
    node_id = data_dict["id"]
    delete_query = "DELETE FROM system_timeline WHERE node_id = %s"
    await database_update(delete_query, (node_id,))
    website_logger.info(
        f"[时间点删除]{account}-> {node_id}", extra={"event": "网页日志"}
    )
    return R(status="success")
