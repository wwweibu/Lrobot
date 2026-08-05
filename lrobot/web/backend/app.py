"""fastapi 主逻辑"""

import uuid
import uvicorn
import traceback
from fastapi import FastAPI, Request, Response
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from web.backend.cab import *
from logic import ip_check, ip_ban
from web.backend.cab.base import R
from config import path, loggers, temp_key


website_logger = loggers["website"]
# 禁用文档页
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# 注册 APIRouter
routers = [
    command_router,
    database_router,
    file_router,
    home_router,
    joke_router,
    log_router,
    login_router,
    metrics_router,
    panel_router,
    static_router,
    textgame_router,
    time_router,
    user_router,
    wiki_router
]
for router in routers:
    app.include_router(router, prefix="/hjd")
app.include_router(textgame_page_router)  # 页面直出,和前端一样走 /cab
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # 允许所有主机
app.add_middleware(GZipMiddleware)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """异常捕获"""
    website_logger.error(
        f"{exc} | {request.client.host}: {request.url}",
        extra={"event": "运行失败"},
    )
    loggers["system"].debug(f"[后端运行]-> 堆栈: {traceback.format_exc()}\n变量: {locals()}",
                            extra={"event": "错误堆栈"})
    if request.url.path.startswith("/hjd"):
        return JSONResponse(
            status_code=200,
            content=R(status="fail", data=f"服务器异常: {exc}").model_dump()
        )
    return JSONResponse(status_code=200, content={})


@app.middleware("http")
async def temp_middleware(request: Request, call_next):
    """管理页面临时分享"""
    path_parts = request.url.path.strip("/").split("/")
    if path_parts and path_parts[0] == temp_key["uuid"]:
        # 去掉 uid 部分，转发到 /share/xxx
        new_path = "/share/" + "/".join(path_parts[1:])
        response = RedirectResponse(url=new_path, status_code=302)
        response.set_cookie(
            "cab",
            "cab_temp",
            max_age=600,
            path="/share",
            httponly=False,
            samesite="lax"
        )
        return response
    # 正常访问
    return await call_next(request)

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


async def rotator():
    """更换 uuid"""
    temp_key["uuid"] = uuid.uuid4().hex

@app.get("/{full_path:path}")
async def vue(full_path: str, request: Request):
    """vue 挂载"""
    if full_path.startswith("bnecxy"):
          from message.adapter.wechat_receive import set_callback
          params = request.query_params
          return set_callback(
              params.get("signature", ""),
              params.get("timestamp", ""),
              params.get("nonce", ""),
              params.get("echostr", "")
          )
    ip = request.client.host
    if ip != "222.20.193.18":  # 武汉大学 ip
        if await ip_check(ip):
            return Response(status_code=418, content="I'm a teapot")
    dist_path = path / "web/frontend/dist"
    filepath = dist_path / full_path
    if filepath.exists():
        return FileResponse(filepath)
    if ip != "222.20.193.18":
        ip_cache[ip] = ip_cache.get(ip, 0) + 1

        if ip_cache[ip] >= 10:
            await ip_ban(ip)
            ip_cache[ip] = 0
            return Response(status_code=418, content="I'm a teapot")

    return FileResponse(dist_path / "index.html")


async def server_runner():
    """后端启动"""
    website_logger.info("[网页服务]启动", extra={"event": "网页日志"})
    config = uvicorn.Config(app, host="0.0.0.0", port=5922, log_config=None, proxy_headers=True,
                            forwarded_allow_ips="*")
    server = uvicorn.Server(config)
    await server.serve()


temp_key["uuid"] = uuid.uuid4().hex
