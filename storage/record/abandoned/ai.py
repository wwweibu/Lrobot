# ai 相关逻辑
# 使用ai时需要更改数据库展示页面，处理blob类型数据，需要修改 get_database函数中：all_data[table] = [serialize_row(row) for row in rows]
def serialize_row(row: dict) -> dict:
    """序列化数据库行，处理 BLOB 字段为 base64 字符串"""
    new_row = {}
    for key, value in row.items():
        if isinstance(value, bytes):  # 处理 BLOB 类型
            new_row[key] = base64.b64encode(value).decode("ascii")
        else:
            new_row[key] = value
    return new_row


# 连接
# model_connect.py 服务端接口
import asyncio
from fastapi import WebSocket, APIRouter
from logic import set_connected_service

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

# model_join.py 客户端接口
import json
import asyncio
import websockets
from ollama import chat, ChatResponse


def ollama_model_request(model, messages, tool):
    # 模拟一个长时间任务
    model = model.replace("ollama_", "")
    if model == "qwen":
        model = "qwen2.5:14b"
    completion: ChatResponse = chat(model, messages=messages, tools=tool)
    response = completion.model_dump()
    return response["message"]


async def send_heartbeat(websocket, interval=5):
    """每隔 interval 秒发送一次心跳状态"""
    try:
        while True:
            await asyncio.sleep(interval)
            await websocket.send(json.dumps({"status": "working", "type": "heartbeat"}))
    except websockets.exceptions.ConnectionClosed:
        # 连接已关闭，终止心跳
        pass


async def serve_model(uri: str):
    async with websockets.connect(uri) as websocket:
        print("连接到调用方成功")

        while True:
            try:
                message = await websocket.recv()
                request = json.loads(message)
                print("收到请求:", request)

                model = request.get("model", "")
                messages = request.get("messages", [])
                tool = request.get("tool", None)

                # 创建心跳发送任务
                task_heartbeat = asyncio.create_task(send_heartbeat(websocket))

                # 创建模型处理任务
                result = await asyncio.to_thread(
                    ollama_model_request, model, messages, tool
                )

                # 等待模型处理完成
                print("模型处理完成:", result)

                # 模型完成后取消心跳任务
                task_heartbeat.cancel()
                try:
                    await task_heartbeat
                except asyncio.CancelledError:
                    pass

                # 发送最终结果
                await websocket.send(json.dumps(result))

            except Exception as e:
                print("处理失败，断开连接:", e)
                break


# 启动客户端
if __name__ == "__main__":
    asyncio.run(serve_model("wss://whumystery.cn/hjd/ollama"))
