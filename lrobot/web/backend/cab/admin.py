"""测试接口及 ip逻辑"""

from fastapi.responses import FileResponse
from fastapi import APIRouter, Request, Response, HTTPException
from logic import ip_check
from config import path, loggers, database_update, database_query


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
    base_path = path / "storage/file/resource"
    requested_path = (base_path / file_path).resolve()
    if not str(requested_path).startswith(str(base_path)):
        raise HTTPException(status_code=400, detail="无法访问上层文件或非法路径")
    if requested_path.exists():
        return FileResponse(requested_path)
    else:
        raise HTTPException(status_code=404, detail=f"文件未找到 | 位置: {file_path}")


@router.post("/answer")
async def answer(data: dict):
    """插入到 jokes 表中"""
    text = data.get("text")
    query = "INSERT INTO system_joke (text) VALUES (%s)"
    await database_update(query, (text,))
    return {"success": True, "message": "Answer submitted successfully!"}


@router.get("/joke")
async def joke_get(request: Request):
    """返回一个笑话"""
    ip = request.client.host
    if await ip_check(ip):
        website_logger.error(f" IP {ip} 被封禁 10 分钟", extra={"event": "超频访问"})
        return {"joke": ""}
    result = await database_query(
        "SELECT text FROM system_joke ORDER BY RAND() LIMIT 1;"
    )
    joke = result[0]["text"] if result else "No jokes found."
    return {"joke": joke}
