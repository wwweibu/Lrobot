"""数据库面板"""

from typing import List
from fastapi.responses import JSONResponse
from fastapi import Request, WebSocket, WebSocketDisconnect, APIRouter, Depends
from .cookie import cookie_account_get
from config import database_update, database_query, loggers

router = APIRouter()
website_logger = loggers["website"]
database_connections: List[WebSocket] = []  # 数据库 ws 连接


@router.get("/database")
async def database_get():
    """获取数据库"""
    db_name = "lrobot_data"
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_type = 'BASE TABLE'"
    result = await database_query(query)
    table_names = [row["TABLE_NAME"] for row in result]
    all_data = {}
    for table in table_names:
        try:
            rows = await database_query(f"SELECT * FROM {table}")
            all_data[table] = rows
        except Exception as e:
            all_data[table] = {"error": str(e)}
    return {"tables": table_names, "data": all_data}


@router.put("/database")
async def database_renew(request: Request, account: str = Depends(cookie_account_get)):
    """更新数据库"""
    payload = await request.json()
    table_name = payload.get("table_name")
    action = payload.get("action")

    if not table_name or not action:
        return JSONResponse(
            status_code=400, content={"error": "Missing table_name or action"}
        )

    if action == "update_cell":
        row_id = payload.get("row_id")
        column = payload.get("column")
        value = payload.get("value")
        if column == "id":
            raise Exception("不允许修改主键字段 'id'")
        query = f"UPDATE {table_name} SET {column} = %s WHERE id = %s"
        await database_update(query, (value, row_id))
        website_logger.info(
            f"[{account}] 更新数据库: {table_name},{value},{row_id},{column}",
            extra={"event": "管理操作"},
        )

    elif action == "add_row":
        query = f"INSERT INTO {table_name} () VALUES ()"
        await database_update(query)
        website_logger.info(
            f"[{account}] 更新数据库: {table_name},新增行", extra={"event": "管理操作"}
        )

    elif action == "delete_row":
        row_id = payload.get("row_id")
        query = f"DELETE FROM {table_name} WHERE id = %s"
        await database_update(query, (row_id,))
        website_logger.info(
            f"[{account}] 更新数据库: {table_name},删除行", extra={"event": "管理操作"}
        )

    else:
        return JSONResponse(status_code=400, content={"error": "Unknown action type"})

    return JSONResponse(content={"status": "success"})


@router.websocket("/database/ws")
async def websocket_endpoint(websocket: WebSocket):
    """数据库页面 ws 连接"""
    await websocket.accept()
    database_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        database_connections.remove(websocket)


async def broadcast_db_update():
    """数据库更新提醒"""
    for connection in database_connections:
        try:
            await connection.send_text("database_updated")
        except Exception:
            database_connections.remove(connection)
