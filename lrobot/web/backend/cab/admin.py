# 后端逻辑
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from config import path,loggers
#from logic import query_database, update_database, check_and_update_ip


router = APIRouter()
command_path = path / "storage/config/command.yaml"
users_path = path / "storage/config/user.yaml"
website_logger = loggers["website"]


# TODO 定义数据格式，之后删掉，下面都是TODO
class CommandData(BaseModel):
    content: str
    func: str
    judge: str
    kind: str
    platforms: List[str]
    state: str
    code: str


@router.get("/static/{file_path:path}")
async def custom_static(file_path: str):
    file_path = path / "storage/file/resource" / file_path
    if file_path.exists():
        return FileResponse(file_path)
    else:
        raise Exception(f" 找不到文件| 位置: {file_path}")


@router.get("/home")
async def home():
    return {"message": "开发中，晚上再来试试吧"}


class Answer(BaseModel):
    text: str


@router.post("/answer")
async def answer(data: dict):
    # 插入到 jokes 表中
    text = data.get("text")
    query = "INSERT INTO system_joke (text) VALUES (?)"
    await update_database(query, (text,))
    return {"success": True, "message": "Answer submitted successfully!"}


@router.get("/joke")
async def get_joke(request: Request):
    ip = request.client.host
    if await check_and_update_ip(ip):
        website_logger.error(f" IP {ip} 被封禁 10 分钟", extra={"event": "超频访问"})
        return {"joke": ""}
    result = await query_database(
        "SELECT text FROM system_joke ORDER BY RANDOM() LIMIT 1"
    )
    joke = result[0]["text"] if result else "No jokes found."
    return {"joke": joke}
