"""静态资源文件"""

from .base import APIRouter, HTTPException, FileResponse, website_logger
from config import path

router = APIRouter()

BASE_PATH = path / "storage/file/resource"
BASE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("/static/{file_path:path}")
async def static_file(file_path: str):
    """静态资源文件"""
    requested_path = (BASE_PATH / file_path).resolve()
    if not str(requested_path).startswith(str(BASE_PATH)):
        website_logger.error("[资源页]获取失败-> 无法访问上层文件或非法路径", extra={"event": "网页日志"})
    if requested_path.exists():
        return FileResponse(requested_path)
    else:
        website_logger.error(f"[资源页]获取失败-> 文件未找到 | 位置: {file_path}", extra={"event": "网页日志"})
