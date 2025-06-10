import asyncio
from fastapi import WebSocket, APIRouter
#from logic import set_connected_service

router = APIRouter()


@router.websocket("/ollama")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    set_connected_service("ollama", websocket)
    print("服务方已连接")

    try:
        while True:
            await asyncio.sleep(1)  # 保持连接，不主动关闭
    except Exception as e:
        print("连接断开:", e)
        set_connected_service("ollama", None)
