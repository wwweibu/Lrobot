"""数据库面板"""

from typing import List
from fastapi import WebSocket, WebSocketDisconnect

from config import database_update, database_query, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Dict

router = APIRouter()
database_connections: List[WebSocket] = []  # 数据库 ws 连接


@router.get("/database")
async def database_get():
    """获取数据库"""
    db_name = "lrobot_data"
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_type = 'BASE TABLE'"
    result = await database_query(query)
    table_names = [row["TABLE_NAME"] for row in result]
    priority = ["user_information", "user_external_information", "system_writer"]
    sorted_tables = [t for t in priority if t in table_names]
    remaining_tables = [t for t in table_names if t not in priority]
    table_names = sorted_tables + remaining_tables

    all_data = {}
    for table in table_names:
        try:
            rows = await database_query(f"SELECT * FROM {table}")
            all_data[table] = rows
        except Exception as e:
            website_logger.error(f"[数据页]获取错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
            return R(status="fail", data=str(e))
    return R(status="success", data={"tables": table_names, "data": all_data})


@router.put("/database")
@monitor_adapter("#内阁_数据更新")
async def database_renew(data: Dict, account: str = Depends(cookie_account_get)):
    """更新数据库"""
    if not account:
        return
    table_name = data["table_name"]
    action = data["action"]

    if not table_name or not action:
        return R(status="fail", data="表名和操作缺失")

    if action == "update_cell":
        row_id = data["row_id"]
        column = data["column"]
        value = data["value"]
        if column == "id":
            return R(status="fail", data="不允许修改id字段")
        query = f"UPDATE {table_name} SET {column} = %s WHERE id = %s"
        try:
            await database_update(query, (value, row_id))
        except Exception as e:
            website_logger.error(f"[数据页]更新错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
            return R(status="fail", data=str(e))
        website_logger.info(
            f"[数据库更新]{account}-> {table_name},{value},{row_id},{column}",
            extra={"event": "网页日志"},
        )

        return R(status="success", data=f"{table_name},{value},{row_id},{column}")

    elif action == "add_row":
        query = f"INSERT INTO {table_name} () VALUES ()"
        try:
            await database_update(query)
        except Exception as e:
            website_logger.error(f"[数据页]新增行错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
            return R(status="fail", data=str(e))
        website_logger.info(
            f"[数据库更新]{account}-> {table_name},新增行", extra={"event": "网页日志"}
        )
        return R(status="success", data=f"{table_name}新增行")

    elif action == "delete_row":
        row_id = data["row_id"]
        query = f"DELETE FROM {table_name} WHERE id = %s"
        try:
            await database_update(query, (row_id,))
        except Exception as e:
            website_logger.error(f"[数据页]删除行错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
            return R(status="fail", data=str(e))
        website_logger.info(
            f"[数据库更新]{account}-> {table_name},删除行", extra={"event": "网页日志"}
        )
        return R(status="success", data=f"{table_name}删除行")

    else:
        return R(status="fail", data="未知操作")


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
        except Exception as e:
            website_logger.error(
                f"[数据页]ws 连接错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"}
            )
            database_connections.remove(connection)
