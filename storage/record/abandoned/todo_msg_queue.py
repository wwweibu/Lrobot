import re
import time
import asyncio
from .msg import Msg
from lrobot.config import config
from lrobot.log import robot_log
from .msg_log import msg_log
from .msg_process import msg_process
from lrobot.database import users_status_check, users_id_query, users_group_query, users_id_update


class MsgQueue:
    def __init__(self):
        self.msg_queue = asyncio.Queue()
        self.pending1 = []
        self.pending2 = []
        self.pending3 = []
        self.remove = []

    async def add_message(self, msg: Msg):
        # 消息队列添加
        log_event(msg.robot, "消息添加调试", f"\n{msg.print_attributes()}")
        msg.content = msg.content.replace(" ", "")
        if msg.robot == "LR232":  # 官方user_id转换成qq号
            msg.qq = await users_id_query(msg.off_qq)
        if msg.kind in (10, 11, 12):  # 私聊消息直接入队
            await self.msg_queue.put(msg)
        elif msg.kind in (20, 21, 22):  # 群聊消息
            if msg.robot == "LR232":  # 群聊消息@LR232
                msg.group = await users_group_query(msg.off_group)  # 官方group_id转换成群号
                if msg.qq:  # 已激活成员发送的消息
                    self.pending1.append((msg, time.time()))
                else:
                    self.pending2.append((msg, time.time()))
            else:  # 群聊消息@LR5921
                await self.msg_queue.put(msg)
        elif msg.kind in (13, 23):  # 消息回复
            await self.msg_queue.put(msg)
        elif msg.kind in (14, 24):  # 戳戳
            await msg_log(msg)
        elif msg.kind in (19, 29):  # 撤回消息
            await msg_log(msg)
        elif msg.kind == 33:  # 群消息配对
            self.pending3.append((msg, time.time()))
        elif msg.kind == 34:  # 其他群消息
            pass
        elif msg.kind == 35:  # 回应消息
            await msg_log(msg)

    async def process_messages(self):
        # 消息队列循环处理
        while True:
            # 尝试配对消息
            await self.pair_message()
            await self.check_message()
            log_event(
                "LR232",
                "队列消息检查",
                f"pending1: {[msg.content for msg, _ in self.pending1]}, "
                f"pending2: {[msg.content for msg, _ in self.pending2]}, "
                f"pending3: {[msg.content for msg, _ in self.pending3]},"
                f"msg_queue:{[msg.content for msg in self.msg_queue._queue]}"
            )

            # 清除已配对的消息
            self.pending1 = [(msg, ts) for msg, ts in self.pending1 if (msg, ts) not in self.remove]
            self.pending2 = [(msg, ts) for msg, ts in self.pending2 if (msg, ts) not in self.remove]
            self.pending3 = [(msg, ts) for msg, ts in self.pending3 if (msg, ts) not in self.remove]

            tasks = []  # 存储处理任务
            # 处理队列中的消息
            while not self.msg_queue.empty():  # 当队列不为空时
                msg = await self.msg_queue.get()  # 取出一条消息
                tasks.append(msg_process(msg))  # 添加处理任务

            # 使用 gather 并发处理所有消息
            if tasks:
                await asyncio.gather(*tasks)

            await asyncio.sleep(1)  # 防止 CPU 占用过高

    async def pair_message(self):
        # 消息配对
        try:
            for msg1, timestamp1 in self.pending1:
                for msg3, timestamp3 in self.pending3:
                    if self.first_matching(msg1, msg3):
                        new_msg = self.combine_message(msg1, msg3)
                        await self.msg_queue.put(new_msg)
                        self.remove.append((msg1, timestamp1))
                        self.remove.append((msg3, timestamp3))

            for msg2, timestamp2 in self.pending2:
                for msg3, timestamp3 in self.pending3:
                    if self.second_matching(msg2, msg3):
                        new_msg = self.combine_message(msg2, msg3)
                        await users_id_update(new_msg)
                        await self.msg_queue.put(new_msg)
                        self.remove.append((msg2, timestamp2))
                        self.remove.append((msg3, timestamp3))
        except Exception as e:
            log_event("LR232", "消息配对异常", f"处理消息时出错：{str(e)}")

    async def check_message(self):
        # 检查超时未处理的消息
        current_time = time.time()

        for msg1, timestamp1 in self.pending1:
            if current_time - timestamp1 > 60:
                log_event(msg1.robot, "消息配对异常", f"[{msg1.group}][{msg1.qq}]{msg1.content}")
                self.remove.append((msg1, timestamp1))
        for msg2, timestamp2 in self.pending2:
            if current_time - timestamp2 > 60:
                log_event(msg2.robot, "消息配对异常", f"[{msg2.group}][{msg2.off_qq}]{msg2.content}")
                self.remove.append((msg2, timestamp2))
        for msg3, timestamp3 in self.pending3:
            if current_time - timestamp3 > 60:
                log_event(msg3.robot, "消息配对异常", f"[{msg3.group}][{msg3.qq}]{msg3.content}")
                self.remove.append((msg3, timestamp3))

    @staticmethod
    def first_matching(msg1: Msg, msg3: Msg):
        # 已激活成员的消息配对
        content1 = re.sub(r"[.*?]", "", msg1.content)
        content3 = re.sub(r"[.*?]", "", msg3.content)
        return (
                msg1.group == msg3.group and
                msg1.qq == msg3.qq and
                content1 == content3
        )

    @staticmethod
    def second_matching(msg2: Msg, msg3: Msg):
        content2 = re.sub(r"[.*?]", "", msg2.content)
        content3 = re.sub(r"[.*?]", "", msg3.content)
        # 未激活成员的消息配对，基于内容
        return (
                msg2.group == msg3.group and
                content2 == content3
        )

    @staticmethod
    def combine_message(msg1: Msg, msg2: Msg):
        # 合并LR232和LR5921接收的同一条消息
        msg = Msg(
            robot="LR232",
            content=msg2.content,
            kind=msg1.kind,
            file_name=msg2.file_name,
            file_url=msg2.file_url,
            group=msg2.group,
            qq=msg2.qq,
            seq=msg2.seq,
            off_qq=msg1.off_qq,
            off_group=msg1.off_group,
            off_seq=msg1.off_seq,
        )
        return msg
