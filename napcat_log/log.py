"""napcat日志捕获"""

import sys
import time
import docker
import asyncio

from config import loggers, log_writer


async def log_streamer():
    """监听 napcat 容器日志流"""
    client = docker.from_env()
    container = client.containers.get("napcat")

    loop = asyncio.get_running_loop()
    start_time = int(time.time())

    def stream_logs():
        """日志捕获"""
        for line in container.logs(stream=True, follow=True, since=start_time):
            output = line.decode(errors="ignore").rstrip()
            loop.call_soon_threadsafe(loggers["napcat"].info, output)

    await asyncio.to_thread(stream_logs)


async def main():
    """程序入口"""
    try:
        await asyncio.gather(log_writer(), log_streamer())
    except Exception as e:
        loggers["system"].error(f"[任务]napcat_log 异常-> {type(e).__name__}: {e}", extra={"event": "运行失败"})
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
