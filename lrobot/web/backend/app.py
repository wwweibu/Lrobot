"""fastapi 主逻辑"""

import uvicorn
import traceback
from fastapi import FastAPI, Request, Response
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from web.backend.cab import *
from config import path, loggers


website_logger = loggers["website"]
# 禁用文档页
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# 注册 APIRouter
routers = [
    admin_router,
    command_router,
    database_router,
    file_router,
    login_router,
    user_router,
    time_router,
    bubble_router,
    panel_router,
    log_router,
    wiki_router
]
for router in routers:
    app.include_router(router, prefix="/hjd")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # 允许所有主机
app.add_middleware(GZipMiddleware)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """异常捕获"""
    website_logger.error(
        f"IP: {request.client.host} | 请求路径: {request.url} -> {str(exc)}",
        extra={"event": "运行日志"},
    )
    loggers["system"].error(traceback.format_exc(), extra={"event": "错误堆栈"})
    return JSONResponse(status_code=200, content={})


@app.get("/")
async def homepage():
    """主页"""
    return FileResponse(path / "web/frontend/dist/index.html")


@app.get("/favicon.ico")
def favicon():
    """图标"""
    file_path = path / "storage/file/firefly/logo.png"
    return FileResponse(file_path) if file_path.exists() else JSONResponse({"error": "File not found"}, status_code=404)


@app.get("/test")
async def test():
    """正常测试"""
    return Response(content="Hello World!", media_type="text/plain")


@app.get("/test1")
async def test1():
    """错误测试"""
    raise ValueError("This is an internal server error.")


@app.get("/{full_path:path}")
async def vue(full_path: str):
    """vue 挂载"""
    dist_path = path / "web/frontend/dist"
    filepath = dist_path / full_path
    return FileResponse(filepath) if filepath.exists() else FileResponse(dist_path / "index.html")


async def server_runner():
    """后端启动"""
    website_logger.info("后台服务启动", extra={"event": "运行日志"})
    config = uvicorn.Config(app, host="0.0.0.0", port=5922, log_config=None)
    server = uvicorn.Server(config)
    await server.serve()
