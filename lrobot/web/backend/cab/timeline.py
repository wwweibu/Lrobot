"""时间轴页面"""

from fastapi import HTTPException, APIRouter, Request, Depends
from .cookie import cookie_account_get
from config import database_update, database_query, loggers

website_logger = loggers["website"]
router = APIRouter()


@router.get("/nodes")
async def node_get():
    """获取时间节点"""

    query = "SELECT node_id AS id, date, event, tag FROM system_timeline"
    rows = await database_query(query)
    return rows


@router.post("/nodes")
async def node_create(request: Request, account: str = Depends(cookie_account_get)):
    """创建时间节点"""
    data = await request.json()
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        raise HTTPException(status_code=400, detail="缺少 date 或 event 字段")

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
        f"[{account}] 创建时间点 :{next_node_id},{date_val},{event_val},{tag_val}",
        extra={"event": "管理操作"},
    )
    return {"id": next_node_id, "date": date_val, "event": event_val, "tag": tag_val}


@router.put("/nodes/{node_id}")
async def node_update(
    node_id: int, request: Request, account: str = Depends(cookie_account_get)
):
    """更新时间节点"""
    data = await request.json()
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        raise HTTPException(status_code=400, detail="缺少 date 或 event 字段")

    check_query = "SELECT 1 FROM system_timeline WHERE node_id = %s"
    exist = await database_query(check_query, (node_id,))
    if not exist:
        raise HTTPException(status_code=404, detail="Node not found")

    update_query = """
        UPDATE system_timeline SET date = %s, event = %s, tag = %s WHERE node_id = %s
    """
    await database_update(update_query, (date_val, event_val, tag_val, node_id))
    website_logger.info(
        f"[{account}] 更新时间点: {node_id}, {date_val}, {event_val}, {tag_val}",
        extra={"event": "管理操作"},
    )
    return {"id": node_id, "date": date_val, "event": event_val, "tag": tag_val}


@router.delete("/nodes/{node_id}")
async def node_delete(node_id: int, account: str = Depends(cookie_account_get)):
    """删除时间节点"""
    delete_query = "DELETE FROM system_timeline WHERE node_id = %s"
    await database_update(delete_query, (node_id,))
    website_logger.info(
        f"[{account}] 删除时间点: {node_id}", extra={"event": "管理操作"}
    )
    return {"message": "Node deleted"}
