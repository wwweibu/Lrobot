import time
import asyncio
from config import loggers
from message.handler.msg import Msg
from message.handler.msg_process import msg_process


msg_logger = loggers["message"]


class MsgPool:
    """消息存储池 + 消息队列"""

    _pool = {}  # 存储 {num: (Msg 对象, 创建时间)}
    _queue = asyncio.Queue()  # 消息队列

    @classmethod
    def add(cls, msg: Msg):
        """添加消息到池"""
        cls._pool[msg.num] = (msg, time.time())
        cls._queue.put_nowait(msg)
        msg_logger.debug(f"⌈{msg.robot}⌋{msg.event}:{msg.kind}->{msg.content}", extra={"event": "消息存储"})

    @classmethod
    def get(cls, num: str):
        """获取消息对象"""
        return cls._pool.get(num, (None, None))[0]

    @classmethod
    def remove(cls, num: str):
        """删除消息对象"""
        cls._pool.pop(num, None)

    @classmethod
    async def process_messages(cls):
        """消息处理"""
        while True:
            msg = await cls._queue.get()  # 队列为空时自动挂起，不占用 CPU
            asyncio.create_task(msg_process(msg))

    @classmethod
    async def clean_messages(cls):
        """清理超过 2 天的旧消息（但保留仍被引用的消息）"""
        while True:
            await asyncio.sleep(86400 * 2)
            one_day_ago = time.time() - 86400 * 2  # 1 天前的时间戳

            to_delete = [
                num
                for num, (_, create_time) in cls._pool.items()
                if create_time < one_day_ago
            ]

            # 删除符合条件的消息
            for num in to_delete:
                del cls._pool[num]

            # TODO 待测试清理
            msg_logger.debug(
                f"共清理{len(to_delete)}条消息", extra={"event": "消息清理"}
            )
