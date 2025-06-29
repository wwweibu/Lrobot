from fastapi import FastAPI, HTTPException, APIRouter,Request,Depends
from .cookie import get_account_from_cookie
from config import update_database,query_database,loggers

website_logger = loggers["website"]
router = APIRouter()

# 获取所有节点
@router.get("/nodes")
async def get_nodes(account: str = Depends(get_account_from_cookie)):
    website_logger.info(f"{account} 获取泡泡", extra={"event": "请求成功"})
    query = "SELECT node_id AS id, date, event, tag FROM system_timeline ORDER BY id ASC"
    rows = await query_database(query)
    return rows

# 创建新节点
@router.post("/nodes")
async def create_node(request: Request):
    data = await request.json()
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        raise HTTPException(status_code=400, detail="缺少 date 或 event 字段")

    # 获取最大 node_id
    max_id_query = "SELECT MAX(node_id) as max_id FROM system_timeline"
    result = await query_database(max_id_query)
    next_node_id = (result[0]["max_id"] or 0) + 1

    insert_query = """
        INSERT INTO system_timeline (node_id, date, event, tag)
        VALUES (%s, %s, %s, %s)
    """
    await update_database(insert_query, (next_node_id, date_val, event_val, tag_val))

    return {"id": next_node_id, "date": date_val, "event": event_val, "tag": tag_val}

# 更新节点
@router.put("/nodes/{node_id}")
async def update_node(node_id: int, request: Request):
    data = await request.json()
    date_val = data.get("date")
    event_val = data.get("event")
    tag_val = data.get("tag", "事件")

    if not date_val or not event_val:
        raise HTTPException(status_code=400, detail="缺少 date 或 event 字段")

    check_query = "SELECT 1 FROM system_timeline WHERE node_id = %s"
    exist = await query_database(check_query, (node_id,))
    if not exist:
        raise HTTPException(status_code=404, detail="Node not found")

    update_query = """
        UPDATE system_timeline SET date = %s, event = %s, tag = %s WHERE node_id = %s
    """
    await update_database(update_query, (date_val, event_val, tag_val, node_id))
    return {"id": node_id, "date": date_val, "event": event_val, "tag": tag_val}

# 删除节点
@router.delete("/nodes/{node_id}")
async def delete_node(node_id: int):
    delete_query = "DELETE FROM system_timeline WHERE node_id = %s"
    await update_database(delete_query, (node_id,))
    return {"message": "Node deleted"}