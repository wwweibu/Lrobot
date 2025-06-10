import time


class Msg:
    """消息类"""

    __slots__ = (
        "num",  # 消息序号
        "robot",  # 平台名
        "kind",  # 种类
        "event",  # 触发事件
        "source",  # 来源
        "seq",  # 平台原 ID
        "content",  # 内容
        "files",  # 文件列表
        "group",  # 来源（群）
    )  # 避免动态创建属性

    _last_timestamp = int(time.time()) * 1000  # 上条消息的时间戳
    _counter = 0  # 计数器，用于同一秒内生成不同的 num

    def __init__(
        self,
        robot,
        kind,
        event,
        source,
        seq=None,
        content=None,
        files=None,
        group=None,
    ):
        """msg 类初始化函数"""
        # 自动生成 num
        self.num = Msg._generate_num()
        # 初始化其他属性，统一为字符串
        self.robot = str(robot)
        self.kind = str(kind)
        self.event = str(event)
        self.source = str(source)
        self.seq = str(seq) if seq else None
        self.content = str(content).strip() if content else None
        self.files = files if files else []  # 空值 "" 也会变成列表
        self.group = str(group) if group else None
        from message.handler.msg_pool import MsgPool

        MsgPool.add(self)  # 添加到消息池

    @classmethod
    def _generate_num(cls):
        """生成唯一的 num，基于时间戳和计数器"""
        current_timestamp = int(time.time()) * 1000  # 获取当前时间的时间戳

        if current_timestamp == cls._last_timestamp:
            cls._counter += 1  # 同一秒内递增计数器
        else:
            cls._last_timestamp = current_timestamp  # 更新时间戳
            cls._counter = 0  # 计数器重置

        # 生成 num，格式为 "时间戳+计数器"
        return current_timestamp + cls._counter

    def __repr__(self):
        """修改 print 方法"""
        attributes = {
            slot: getattr(self, slot)
            for slot in self.__slots__
            if hasattr(self, slot) and getattr(self, slot) is not None
        }
        return str(attributes)
