# 后端逻辑
from fastapi.responses import FileResponse
from fastapi import APIRouter, Request,Response
from logic import check_and_update_ip
from config import path,loggers,update_database,query_database


router = APIRouter()
command_path = path / "storage/config/command.yaml"
users_path = path / "storage/config/user.yaml"
website_logger = loggers["website"]

@router.get("/test")
async def test():
    """测试端口"""
    return Response(content="Hello World!", media_type="text/plain")


@router.get("/static/{file_path:path}")
async def static_file(file_path: str):
    """静态资源文件"""
    file_path = path / "storage/file/resource" / file_path
    if file_path.exists():
        return FileResponse(file_path)
    else:
        raise Exception(f" 找不到文件 | 位置: {file_path}")


@router.post("/answer")
async def answer(data: dict):
    """插入到 jokes 表中"""
    text = data.get("text")
    query = "INSERT INTO system_joke (text) VALUES (%s)"
    await update_database(query, (text,))
    return {"success": True, "message": "Answer submitted successfully!"}


@router.get("/joke")
async def get_joke(request: Request):
    """返回一个笑话"""
    ip = request.client.host
    if await check_and_update_ip(ip):
        website_logger.error(f" IP {ip} 被封禁 10 分钟", extra={"event": "超频访问"})
        return {"joke": ""}
    result = await query_database(
        "SELECT text FROM system_joke ORDER BY RAND() LIMIT 1;"
    )
    joke = result[0]["text"] if result else "No jokes found."
    return {"joke": joke}
