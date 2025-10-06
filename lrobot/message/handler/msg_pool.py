"""消息池"""

import time
import asyncio

from config import loggers, storage
from message.handler.msg import Msg
from message.handler.msg_process import msg_process

msg_logger = loggers["message"]


class MsgPool:
    """消息存储池 + 消息队列"""

    _queue = asyncio.Queue()  # 消息队列
    seq_index = {}  # seq-num 索引

    @classmethod
    def add(cls, msg: Msg):
        """添加消息到池"""
        global msg_pool  # num-msg_data  消息池
        content_str = Msg.content_join(msg.content) or msg.kind
        msg_data = {"time": time.time(), **{key: getattr(msg, key) for key in Msg.__slots__}}
        msg_pool[msg.num] = msg_data
        if msg_data.get("seq") is not None:
            cls.seq_index[msg_data["seq"]] = msg.num
        cls._queue.put_nowait(msg)

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
        """消息处理"""
        while True:
            msg = await cls._queue.get()  # 队列为空时自动挂起
            asyncio.create_task(msg_process(msg))

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
for msg_num, data in msg_pool.items():  # 重新构建索引
    if data.get("seq") is not None:
        MsgPool.seq_index[data["seq"]] = msg_num
