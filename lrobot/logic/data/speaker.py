# TODO,调用LR5921的接口
import asyncio
from config import config

task_queue = asyncio.Queue()


async def get_speaker():
    # 获取龙王
    info = {
        "action": "get_group_honor_info",
        "params": {
            "group_id": config["水群"],
            "type": "all",
        },
        "echo": "get_talkative",
    }
    await global_ws.get("ws").send(json.dumps(info))

    # 调用获取今日发言用户的逻辑
    info = {
        "action": "get_group_member_list",
        "params": {
            "group_id": config["水群"],
            "no_cache": True,
        },
        "echo": "flush_speak",
    }
    await global_ws.get("ws").send(json.dumps(info))

    await asyncio.sleep(10)

    # 在队列中处理任务
    while True:
        try:
            # 尝试从任务队列获取用户数据
            info = task_queue.get_nowait()  # 使用 get_nowait() 尝试非阻塞获取消息
            await global_ws.get("ws").send(json.dumps(info))
            await asyncio.sleep(0.1)
            # 处理完消息后，调用 task_done()
            task_queue.task_done()

        except asyncio.QueueEmpty:
            # 如果队列为空，立即退出循环
            break
        except Exception as e:
            # 处理其他异常（可选）
            print("处理异常:", e)

    info = {
        "action": "get_group_member_list",
        "params": {
            "group_id": config["水群"],
            "no_cache": True,
        },
        "echo": "get_speak",
    }
    await global_ws.get("ws").send(json.dumps(info))
