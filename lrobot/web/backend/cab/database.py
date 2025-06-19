import base64
from typing import List
from fastapi.responses import JSONResponse
from fastapi import Request, WebSocket, WebSocketDisconnect, APIRouter
from config import query_database, update_database

router = APIRouter()
database_connections: List[WebSocket] = []  # 数据库 ws 连接


@router.get("/database")
async def get_database():
    """获取数据库"""
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    result = await query_database(query)
    table_names = [row["name"] for row in result]
    all_data = {}
    for table in table_names:
        try:
            rows = await query_database(f"SELECT * FROM {table}")
            all_data[table] = rows
        except Exception as e:
            all_data[table] = {"error": str(e)}
    return {"tables": table_names, "data": all_data}


@router.put("/database")
async def renew_database(request: Request):
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
        query = f"UPDATE {table_name} SET {column} = ? WHERE id = ?"
        await update_database(query, (value, row_id))

    elif action == "add_row":
        query = f"INSERT INTO {table_name} DEFAULT VALUES"
        await update_database(query)

    elif action == "delete_row":
        row_id = payload.get("row_id")
        query = f"DELETE FROM {table_name} WHERE id = ?"
        await update_database(query, (row_id,))

    else:
        return JSONResponse(status_code=400, content={"error": "Unknown action type"})

    return JSONResponse(content={"status": "success"})


@router.websocket("/database/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    database_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        database_connections.remove(websocket)


async def broadcast_db_update():
    for connection in database_connections:
        try:
            await connection.send_text("database_updated")
        except Exception:
            database_connections.remove(connection)
