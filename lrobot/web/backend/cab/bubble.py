"""泡泡界面"""

from typing import List
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    Depends,
)
from .cookie import cookie_account_get
from config import database_update, database_query, loggers

router = APIRouter()
website_logger = loggers["website"]
bubbles_connections: List[WebSocket] = []  # 数据库 ws 连接


@router.post("/bubbles")
async def bubble_upsert(request: Request, account: str = Depends(cookie_account_get)):
    """编辑泡泡"""
    data = await request.json()
    bubble_id = data.get("id")
    content = data.get("content")
    x = data.get("x")
    y = data.get("y")
    active = data.get("active", False)

    if not content or x is None or y is None:
        return {"status": "error", "message": "Missing content, x, or y"}

    if bubble_id:  # 修改或移动
        query = "UPDATE system_bubble SET content = %s, x = %s, y = %s, active = %s WHERE id = %s"
        await database_update(query, (content, x, y, active, bubble_id))
        await broadcast_bubbles_update()
        website_logger.info(
            f"[{account}] 修改泡泡({content},{x},{y})", extra={"event": "管理操作"}
        )
        return {"status": "updated"}
    else:  # 创建新泡泡
        query = (
            "INSERT INTO system_bubble (content, x, y, active) VALUES (%s, %s, %s, %s)"
        )
        result = await database_update(query, (content, x, y, active))
        await broadcast_bubbles_update()
        website_logger.info(
            f"[{account}] 新建泡泡({content},{x},{y})", extra={"event": "管理操作"}
        )
        return {"status": "inserted", "id": result}


@router.post("/bubbles/delete")
async def bubble_delete(request: Request, account: str = Depends(cookie_account_get)):
    """删除泡泡"""
    data = await request.json()
    bubble_id = data.get("id")
    if not bubble_id:
        return {"status": "error", "message": "Missing id"}
    query = "DELETE FROM system_bubble WHERE id = %s"
    await database_update(query, (bubble_id,))
    await broadcast_bubbles_update()
    website_logger.info(
        f"[{account}] 删除泡泡({bubble_id})", extra={"event": "管理操作"}
    )
    return {"status": "deleted"}


@router.get("/bubbles")
async def bubbles_get():
    """获取泡泡"""
    query = "SELECT id, content, x, y, active FROM system_bubble"
    result = await database_query(query)
    return result


@router.websocket("/bubbles/ws")
async def websocket_endpoint(websocket: WebSocket):
    """泡泡编辑通信"""
    await websocket.accept()
    bubbles_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        bubbles_connections.remove(websocket)


async def broadcast_bubbles_update():
    """泡泡更新"""
    for connection in bubbles_connections:
        try:
            await connection.send_text("bubbles_updated")
        except Exception:
            bubbles_connections.remove(connection)
