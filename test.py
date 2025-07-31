import asyncio
from fastapi import FastAPI
import uvicorn
from uvicorn import Config, Server

# FastAPI 应用
app = FastAPI()

@app.get("/ping")
async def ping():
    return {"msg": "pong"}

# 自定义 Server：不安装信号处理器
class NoSignalServer(Server):
    def install_signal_handlers(self):
        pass

# 运行 uvicorn 的协程
async def server_runner():
    print("🔵 server_runner 启动")
    config = Config(app=app, host="0.0.0.0", port=5922, log_config=None)
    server = NoSignalServer(config)
    try:
        await server.serve()
    finally:
        print("🟡 server_runner finally 被执行")

# 主入口：用 gather 启动
async def main():
    try:
        await asyncio.gather(server_runner())
    finally:
        print("🟢 main finally 被执行")

if __name__ == "__main__":
    asyncio.run(main())
