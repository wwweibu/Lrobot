from typing import List
from fastapi import APIRouter, HTTPException,Request,WebSocket,WebSocketDisconnect,Depends
from .cookie import get_account_from_cookie
from config import update_database,query_database,loggers

router = APIRouter()
website_logger = loggers["website"]
bubbles_connections: List[WebSocket] = []  # 数据库 ws 连接

@router.post("/bubbles")
async def upsert_bubble(request: Request,account: str = Depends(get_account_from_cookie)):
    data = await request.json()
    bubble_id = data.get('id')
    content = data.get('content')
    x = data.get('x')
    y = data.get('y')
    active = data.get('active', False)

    if not content or x is None or y is None:
        return {"status": "error", "message": "Missing content, x, or y"}

    if bubble_id:  # 修改或移动
        query = "UPDATE system_bubble SET content = %s, x = %s, y = %s, active = %s WHERE id = %s"
        await update_database(query, (content, x, y, active, bubble_id))
        await broadcast_bubbles_update()
        website_logger.info(f"[{account}] 修改泡泡({content},{x},{y})", extra={"event": "请求成功"})
        return {"status": "updated"}
    else:  # 创建新泡泡
        query = "INSERT INTO system_bubble (content, x, y, active) VALUES (%s, %s, %s, %s)"
        result = await update_database(query, (content, x, y, active))
        await broadcast_bubbles_update()
        website_logger.info(f"[{account}] 新建泡泡({content},{x},{y})", extra={"event": "请求成功"})
        return {"status": "inserted", "id": result}

@router.post("/bubbles/delete")
async def delete_bubble(request: Request,account: str = Depends(get_account_from_cookie)):
    data = await request.json()
    bubble_id = data.get('id')
    if not bubble_id:
        return {"status": "error", "message": "Missing id"}
    query = "DELETE FROM system_bubble WHERE id = %s"
    await update_database(query, (bubble_id,))
    await broadcast_bubbles_update()
    website_logger.info(f"[{account}] 删除泡泡({bubble_id})", extra={"event": "请求成功"})
    return {"status": "deleted"}

@router.get("/bubbles")
async def get_bubbles():
    query = "SELECT id, content, x, y, active FROM system_bubble ORDER BY id ASC"
    result = await query_database(query)
    print(result)
    return result

@router.websocket("/bubbles/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    bubbles_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        bubbles_connections.remove(websocket)


async def broadcast_bubbles_update():
    for connection in bubbles_connections:
        try:
            await connection.send_text("bubbles_updated")
        except Exception:
            bubbles_connections.remove(connection)