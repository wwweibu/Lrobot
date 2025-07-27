"""消息池"""

import time
import asyncio

from config import loggers, config
from message.handler.msg import Msg
from message.handler.msg_process import msg_process

msg_logger = loggers["message"]


class MsgPool:
    """消息存储池 + 消息队列"""

    _queue = asyncio.Queue()  # 消息队列

    @classmethod
    def add(cls, msg: Msg):
        """添加消息到池"""
        global msg_pool
        msg_pool[msg.num] = {"time": time.time(), **{key: getattr(msg, key) for key in Msg.__slots__}}
        cls._queue.put_nowait(msg)
        msg_logger.debug(
            f"⌈{msg.platform}⌋{msg.event}: {msg.kind} -> {Msg.content_join(msg.content) if Msg.content_join(msg.content) else msg.kind}",
            extra={"event": "消息存储"},
        )

    @classmethod
    def get(cls, num):
        """获取消息"""
        return msg_pool.get(num)

    @classmethod
    def remove(cls, num):
        """删除消息"""
        global msg_pool
        msg_pool.pop(num, None)

    @classmethod
    def seq_get(cls, seq):
        """根据序号获取消息"""
        for msg_data in msg_pool.values():
            if msg_data["seq"] == seq:
                return msg_data
        return None

    @classmethod
    async def process(cls):
        """消息处理"""
        while True:
            msg = await cls._queue.get()  # 队列为空时自动挂起，不占用 CPU
            asyncio.create_task(msg_process(msg))

    @classmethod
    async def clean(cls, interval):
        """清理旧消息"""
        global msg_pool
        to_delete = [
            num
            for num, msg_data in msg_pool.items()
            if msg_data["time"] < time.time() - interval
        ]

        for num in to_delete:
            del msg_pool[num]

        msg_logger.debug(f"共清理 {len(to_delete)} 条消息", extra={"event": "消息清理"})


msg_pool = config.load("msg_pool")
