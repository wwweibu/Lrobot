"""消息池"""

import asyncio
import os
import time

from config import RUNTIME_METRICS, future, loggers, storage
from message.handler.msg import Msg
from message.handler.msg_process import msg_process

msg_logger = loggers["message"]

MESSAGE_QUEUE_MAX = max(10, int(os.getenv("LROBOT_MESSAGE_QUEUE_MAX", "500")))
CONTROL_QUEUE_MAX = max(10, int(os.getenv("LROBOT_CONTROL_QUEUE_MAX", "500")))
MESSAGE_WORKERS = max(1, int(os.getenv("LROBOT_MESSAGE_WORKERS", "16")))
CONTROL_WORKERS = max(1, int(os.getenv("LROBOT_CONTROL_WORKERS", "8")))
MESSAGE_POOL_MAX = max(100, int(os.getenv("LROBOT_MESSAGE_POOL_MAX", "20000")))

RUNTIME_METRICS.setdefault("message_dropped", 0)
RUNTIME_METRICS.setdefault("control_dropped", 0)
RUNTIME_METRICS.setdefault("message_pool_evicted", 0)


class MsgPool:
    """消息存储池 + 消息队列"""

    # 接收命令和发送/适配器回调分队列，避免 worker 全部等待回调时死锁。
    _message_queue = asyncio.Queue(maxsize=MESSAGE_QUEUE_MAX)
    _control_queue = asyncio.Queue(maxsize=CONTROL_QUEUE_MAX)
    seq_index = {}  # seq-num 索引

    @classmethod
    def add(cls, msg: Msg):
        """添加消息到池"""
        global msg_pool  # num-msg_data  消息池
        queue = cls._message_queue if msg.event == "处理" else cls._control_queue
        try:
            queue.put_nowait(msg)
        except asyncio.QueueFull:
            metric = "message_dropped" if msg.event == "处理" else "control_dropped"
            RUNTIME_METRICS[metric] += 1
            if msg.event != "处理":
                future.set_exception(msg.num, RuntimeError("[消息队列]发送队列已满"))
            if RUNTIME_METRICS[metric] == 1 or RUNTIME_METRICS[metric] % 100 == 0:
                msg_logger.warning(
                    f"[消息队列]已满-> {metric}={RUNTIME_METRICS[metric]}",
                    extra={"event": "消息处理"},
                )
            return False

        while len(msg_pool) >= MESSAGE_POOL_MAX:
            oldest_num = next(iter(msg_pool))
            cls.remove(oldest_num)
            RUNTIME_METRICS["message_pool_evicted"] += 1

        msg_data = {"time": time.time(), **{key: getattr(msg, key) for key in Msg.__slots__}}
        msg_pool[msg.num] = msg_data
        if msg_data.get("seq") is not None:
            cls.seq_index[msg_data["seq"]] = msg.num
        return True

    @classmethod
    def get(cls, num):
        """获取消息"""
        return msg_pool.get(num)

    @classmethod
    def seq_get(cls, seq):
        """根据序号获取消息"""
        num = cls.seq_index.get(seq)
        return msg_pool.get(num) if num else None

    @classmethod
    def remove(cls, num):
        """删除消息"""
        global msg_pool
        msg_data = msg_pool.pop(num, None)
        if msg_data and msg_data.get("seq") in cls.seq_index:
            cls.seq_index.pop(msg_data["seq"], None)

    @classmethod
    async def process(cls):
        """使用固定 worker 消费两个有界队列。"""
        async with asyncio.TaskGroup() as group:
            for index in range(MESSAGE_WORKERS):
                group.create_task(
                    cls._worker(cls._message_queue),
                    name=f"message-worker-{index + 1}",
                )
            for index in range(CONTROL_WORKERS):
                group.create_task(
                    cls._worker(cls._control_queue),
                    name=f"control-worker-{index + 1}",
                )

    @staticmethod
    async def _worker(queue):
        while True:
            msg = await queue.get()
            try:
                await msg_process(msg)
            except Exception as error:
                # 单条坏消息不能让 TaskGroup 取消全部固定 worker。
                msg_logger.error(
                    f"[消息处理]worker 异常-> {type(error).__name__}: {error}",
                    extra={"event": "运行失败"},
                )
            finally:
                queue.task_done()

    @classmethod
    def stats(cls):
        """返回队列与消息池的可观测指标。"""
        return {
            "message_queue": cls._message_queue.qsize(),
            "message_queue_max": cls._message_queue.maxsize,
            "control_queue": cls._control_queue.qsize(),
            "control_queue_max": cls._control_queue.maxsize,
            "message_pool": len(msg_pool),
            "message_dropped": RUNTIME_METRICS["message_dropped"],
            "control_dropped": RUNTIME_METRICS["control_dropped"],
            "message_pool_evicted": RUNTIME_METRICS["message_pool_evicted"],
        }

    @classmethod
    async def clean(cls, interval):
        """清理旧消息"""
        global msg_pool
        expire_time = time.time() - interval  # 过期时间

        to_delete = [
            num
            for num, msg_data in msg_pool.items()
            if msg_data["time"] < expire_time
        ]

        for num in to_delete:
            cls.remove(num)

        msg_logger.debug(f"[消息清理]完成-> 共清理 {len(to_delete)} 条消息", extra={"event": "消息处理"})


msg_pool = storage.setdefault("msg_pool", {})
while len(msg_pool) > MESSAGE_POOL_MAX:
    msg_pool.pop(next(iter(msg_pool)))
    RUNTIME_METRICS["message_pool_evicted"] += 1
for msg_num, data in msg_pool.items():  # 重新构建索引
    if data.get("seq") is not None:
        MsgPool.seq_index[data["seq"]] = msg_num
