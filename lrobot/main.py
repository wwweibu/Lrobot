"""项目主入口"""

import signal
import asyncio

from config import config  # 放在前面
from secret import secret
from message.handler.msg_pool import MsgPool
from web.backend.app import server_runner, app, rotator
from logic import backup_mysql, backup_mongo, remind_load, subscribe_up_init, check_net
from config import (
    future,
    loggers,
    mysql_init,
    scheduler_add,
    log_writer,
    config_watcher,
    storage,
    mongo_indexes_create
)
from message.adapter import (
    refresh_tokens,
    LR232_router,
    WECHAT_router,
    LR5921_router,
    bili_receive,
    bili_fan_get
)


async def start():
    """初始化函数"""
    try:
        loop = asyncio.get_running_loop()
        future.init(loop)  # future 管理器记录主循环
        await mysql_init()
        await mongo_indexes_create()  # mongodb 建立索引
        await remind_load()  # 加载待办等待
    except Exception as e:
        loggers["system"].error(f"[初始化]失败-> {type(e).__name__}: {e}", extra={"event": "运行失败"})



def stop():
    """清理函数，必须同步"""
    config.save(storage)  # 持久化存储


async def scheduler():
    """定时任务"""
    await asyncio.sleep(5)  # 执行其他任务
    scheduler_add(backup_mysql, interval=86400)  # 备份 Mysql
    scheduler_add(backup_mongo, interval=86400)  # 备份 Mongo
    scheduler_add(MsgPool.clean, 86400, interval=86400)  # 消息池清理
    scheduler_add(rotator, interval=600)  # 临时网址更换



async def LR232_init():
    """LR232 初始化函数"""
    app.include_router(LR232_router, prefix=secret("/LR232"))
    scheduler_add(check_net, interval=300)  # 网址连通性检测


async def LR5921_init():
    """LR5921 初始化函数"""
    app.include_router(LR5921_router, prefix=secret("/LR5921"))


async def WECHAT_init():
    """WECHAT 初始化函数"""
    app.include_router(WECHAT_router, prefix=secret("/WECHAT"))


async def BILI_init():
    """BILI 初始化函数"""
    scheduler_add(bili_receive, 60, interval=60, at_once=True)  # 推荐刷新间隔 20
    scheduler_add(bili_fan_get, interval=300)  # 检测粉丝
    await subscribe_up_init()  # 轮询 up 更新

def tasks_set():
    """生成任务列表"""
    tasks = [
        config_watcher,  # 配置自动更新、写入
        log_writer,  # 日志记录器
        scheduler,  # 定时任务
        MsgPool.process,  # 消息处理
        server_runner,  # fastapi 运行
    ]
    PLATFORM_CONFIG = {
        "LR232": ["LR232_ID", "LR232_SECRET"],
        "LR5921": ["LR5921_ID"],
        "WECHAT": ["WECHAT_ID", "WECHAT_SECRET", "WECHAT_SELF", "WECHAT_TOKEN"],
        "BILI": ["BILI_SESSDATA", "BILI_JCT", "BILI_UID", "BILI_UUID"],
    }  # 平台配置参数

    platform_list = [
        name for name, keys in PLATFORM_CONFIG.items() if all(config[k] for k in keys)
    ]  # 激活的平台列表

    tasks.extend(
        [
            globals()[f"{name}_init"]  # 调用 xxx_init
            for name in platform_list
        ]
    )

    tasks.append(lambda: refresh_tokens(platform_list))  # 令牌刷新任务

    return tasks


def task_warp(func, exit_event):
    """任务接收退出信号"""

    async def wrapper():
        """装饰器"""
        task = asyncio.create_task(func())
        task.name = func.__name__
        await asyncio.wait(
            [task, asyncio.create_task(exit_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )  # 等待任意一个完成

        if exit_event.is_set():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                loggers["system"].debug(
                    f"[任务]被取消-> {func.__name__}", extra={"event": "运行日志"}
                )

        return await task if not task.cancelled() else None

    return asyncio.create_task(wrapper(), name=func.__name__)


async def main():
    """代码主入口，运行所有任务"""
    await start()

    exit_event = asyncio.Event()

    def signal_handle(sig, frame):
        """处理信号"""
        loggers["system"].debug(
            f"[信号]收到退出信号-> {sig}", extra={"event": "运行日志"}
        )
        exit_event.set()

    signal.signal(signal.SIGINT, signal_handle)
    signal.signal(signal.SIGTERM, signal_handle)

    tasks = [task_warp(t, exit_event) for t in tasks_set()]
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 检查并打印异常
        for task, r in zip(tasks, results):
            name = task.get_name()
            if isinstance(r, Exception):
                loggers["system"].error(
                    f"[任务]{name} 异常-> {type(r).__name__}: {r}", extra={"event": "运行失败"}
                )
    finally:
        stop()


if __name__ == "__main__":
    asyncio.run(main())
