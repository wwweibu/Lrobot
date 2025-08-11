"""消息类"""

import json
import time

from config import config


class Msg:
    """消息类"""

    __slots__ = (
        "num",  # 消息序号
        "platform",  # 平台
        "event",  # 触发事件
        "kind",  # 种类
        "seq",  # 消息原始 ID
        "content",  # 内容
        "user",  # 用户
        "group",  # 群
    )  # 避免动态创建属性

    _last_timestamp = int(time.time()) * 1000  # 上条消息的时间戳
    _counter = 0  # 计数器，用于同一秒内生成不同的 num

    def __init__(self, platform, event, kind, seq=None, content=None, user=None, group=None):
        """msg 类初始化函数"""
        # 自动生成 num
        self.num = Msg._generate_num()
        # 初始化其他属性，统一为字符串
        self.platform = str(platform)
        self.event = str(event)
        self.kind = str(kind)
        self.seq = str(seq) if seq else None
        self.content = self.content_disjoin(content) if content else None  # 自动转换成 list 格式
        self.user = str(user) if user else None
        self.group = str(group) if group else None
        from message.handler.msg_pool import MsgPool

        MsgPool.add(self)  # 添加到消息池

    def __repr__(self):
        """修改 print 方法"""
        attributes = {k: getattr(self, k) for k in self.__slots__ if getattr(self, k) is not None}
        return json.dumps(attributes, ensure_ascii=False)

    @classmethod
    def _generate_num(cls):
        """生成唯一的 num"""
        current_timestamp = int(time.time()) * 1000  # 获取当前时间的时间戳

        if current_timestamp == cls._last_timestamp:
            cls._counter += 1  # 同一秒内递增计数器
        else:
            cls._last_timestamp = current_timestamp  # 更新时间戳
            cls._counter = 0  # 计数器重置

        # 生成 num，格式为 "时间戳+计数器"
        return current_timestamp + cls._counter

    @staticmethod
    def _face_join(face_id, face_text=None):
        """表情添加"""
        face = config["emojis"].get(face_id)
        if not face:
            if not face_text:
                raise Exception(f"无法解析的表情 ID: {face_id}")
            face = face_text.strip("[]").lstrip("/")
            # 将新表情添加至 emojis
            emojis = config["emojis"]
            emojis[face_id] = face
            sorted_emojis = dict(
                sorted(emojis.items(), key=lambda x: int(x[0]))
            )  # 按照 key 以数字顺序排序(不加 int:1,10,2)
            config["emojis"] = sorted_emojis
        return face

    @classmethod
    def content_join(cls, content):
        """消息字段打印"""
        if not content:
            return ""
        handlers = {
            "text": lambda d: d.get("text", ""),
            "face": lambda d: f"[表情:{cls._face_join(d.get('id'), d.get('raw', {}).get('faceText'))}]",
            "at": lambda d: f"[at:{d.get('qq')}]",
            "rps": lambda d: f"[猜拳:{ {'1': '布', '2': '剪刀', '3': '石头'}.get(str(d.get('result')), '未知结果')}]",
            "dice": lambda
                d: f"[骰子:{str(d.get('result')) if str(d.get('result')) in {'1', '2', '3', '4', '5', '6'} else '未知结果'}]",
            "reply": lambda d: f"[回复:{cls.content_join(d.get('content', []))}]" if d.get(
                "content") else f"[回复:{d.get('id')}]",
            "forward": lambda
                d: f"[转发:{'|'.join(cls.content_join(n.get('message', [])) for n in d.get('content', []))}]" if d.get(
                "content") else f"[转发:{d.get('id')}]",
            "poke": lambda _: "[戳戳:戳一戳]",
            "mface": lambda d: f"[动画表情:{d.get('summary', '未知的动画表情')}]",
            "image": lambda d: f"[动画表情:{d['summary']}]" if d.get(
                "summary") else f"[图片:{d.get('file', '未知的图片')}]",
            "record": lambda d: f"[语音:{d.get('file', '未知的语音')}]",
            "video": lambda d: f"[视频:{d.get('file', '未知的视频')}]",
            "file": lambda d: f"[文件:{d.get('name') or d.get('file', '未知的文件')}]",
            "json": lambda d: f"[卡片:{d.get('data', {}).get('prompt', '未知的卡片')}]",
            "node": lambda d: f"[节点:{cls.content_join(d.get('content', []))}]"
        }
        return "".join(
            handlers.get(seg["type"], lambda _: f"[未知类型:{seg['type']}]")(seg.get("data", {})) for seg in content)

    @classmethod
    def _content_token_match(cls, content):
        """解析 content 字符串中的消息段 [prefix:value]，支持 value 中嵌套 [] 的情况。"""
        out, i, n = [], 0, len(content)
        while i < n:
            if content[i] != '[':
                # 收集纯文本直到 '['
                j = i
                while j < n and content[j] != '[':
                    j += 1
                out.append(("文本", content[i:j]))
                i = j
                continue

            # 现在 text[i] == '['
            depth = 1
            colon = None
            j = i + 1
            while j < n and depth:
                if content[j] == '[':
                    depth += 1
                elif content[j] == ']':
                    depth -= 1
                elif content[j] == ':' and depth == 1 and colon is None:
                    colon = j
                j += 1
            if depth:  # 未闭合
                out.append(("文本", content[i:]))  # 把剩余当纯文本
                break

            prefix = content[i + 1: colon] if colon else "文本"
            value = content[colon + 1: j - 1] if colon else content[i + 1: j - 1]
            out.append((prefix, value))
            i = j
        return out

    @staticmethod
    def _face_disjoin(value):
        """表情转换"""
        summary, name = value.split("|")
        if name in config["shop_emojis"]:
            raw = config["shop_emojis"][name]
            key, emoji_id, emoji_package_id = raw.split("|")
            return {"type": "mface", "data": {"summary": summary, "key": key, "emoji_id": emoji_id,
                                              "emoji_package_id": emoji_package_id}}

    @classmethod
    def content_disjoin(cls, content):
        """将字符串内容解析为消息字段"""
        if isinstance(content, list):
            return content
        handlers = {
            "文本": lambda v: {"type": "text", "data": {"text": v}},
            "表情": lambda v: {
                        "type": "face",
                        "data": {
                            "id": next((j for j, k in config["emojis"].items() if k == v), None)
                        },
            },
            "at": lambda v: {"type": "at", "data": {"qq": v}},
            "猜拳": lambda v: {"type": "rps", "data": {"result": {"布": "1", "剪刀": "2", "石头": "3"}.get(v, "any")}},
            "骰子": lambda v: {"type": "dice", "data": {"result": v if v in "123456" else "any"}},
            "回复": lambda v: {"type": "reply", "data": {"id": v}},
            "戳戳": lambda _: {"type": "poke", "data": {"type": "1", "id": "1"}},
            "动画表情": lambda v: (
                cls._face_disjoin(v) if "|" in v
                else {"type": "image", "data": {"summary": v}}
            ),

            "图片": lambda v: {"type": "image",
                               "data": {"file": v.split("|")[0], "summary": v.split("|")[1]} if "|" in v
                               else {"file": v}},
            "语音": lambda v: {"type": "record", "data": {"file": v}},
            "视频": lambda v: {
                "type": "video",
                "data": dict(zip(("file", "title", "description"), v.split("|"))) if "|" in v
                else {"file": v}},
            "文件": lambda v: {"type": "file", "data": dict(zip(("file", "name"), v.split("|"))) if "|" in v
            else {"file": v}
                               },
            "卡片": lambda v: {
                "type": "json",
                "data": {
                    "data":
                        dict(zip(("prompt", "title", "description", "url"), v.split("|"))) if v.startswith("微信-音乐")
                        else dict(
                            zip(("prompt", "title", "description", "picurl", "url"), v.split("|"))) if v.startswith(
                            "微信-图文")
                        else {"prompt": v}
                },
            },
            "转发": lambda v: {"type": "forward", "data": {"id": v}},
            "节点": lambda v: {
                "type": "node",
                "data": {"user_id": v.split("|")[0], "nickname": v.split("|")[1],
                         "content": Msg.content_disjoin(v.split("|", 2)[2])}
            },
        }

        return [handlers.get(p, lambda _: {"type": "text", "data": {"text": f"{p}:{v}"}})(v) for p, v in
                cls._content_token_match(str(content))]

    PATTERN_FIELDS = {
        'text': ('text',),
        'at': ('qq',),
        'rps': ('result',),
        'dice': ('result',),
        'face': ('id',),
        'reply': ('id',),
        'poke': (),  # poke 无条件匹配
        'record': ('file',),
        'video': ('file',),
        'file': ('file',),
        'json': ('prompt',),
    }

    @staticmethod
    def _seg_match(content_seg, pattern_seg, strict=False):
        """
        单段匹配/相等核心逻辑
        strict=True 表示“相等”模式，不支持子串；False 表示“包含”模式，支持子串
        """
        content_type = content_seg['type']

        # 不支持/不匹配的段直接 False
        if content_type != pattern_seg['type']:
            return False
        elif content_type in {'node', 'forward'}:
            return False
        elif content_type == 'poke':
            return True

        content_data = content_seg.get('data', {})
        pattern_data = pattern_seg.get('data', {})

        # image 单独处理
        if content_type == 'image':
            content_match = content_data.get('summary')
            pattern_match = pattern_data.get('summary')

            if not content_match or not pattern_match:
                content_match = content_data.get('file')
                pattern_match = pattern_data.get('file')
            return pattern_match in ('any', content_match)

        # 取出该类型需要比较的字段
        fields = Msg.PATTERN_FIELDS.get(content_type, ())
        for k in fields:
            content_val = content_data.get(k)
            pattern_val = pattern_data.get(k)

            # 通配
            if pattern_val == 'any':
                continue

            # 严格相等 / 子串包含
            if strict:
                if pattern_val != content_val:
                    return False
            else:
                # text 支持子串，其余按相等处理；text 支持空格代表 any
                if content_type == 'text':
                    if str(pattern_val) not in str(content_val) and str(pattern_val) != " ":
                        return False
                else:
                    if pattern_val != content_val:
                        return False
        return True

    @classmethod
    def content_pattern_contains(cls, content, pattern):
        """判断消息字段是否包含指令字段"""
        if not content or not pattern:
            return False
        pattern = cls.content_disjoin(pattern)
        return any(
            all(cls._seg_match(c, p) for c, p in zip(content[i:], pattern))
            for i in range(len(content) - len(pattern) + 1)
        )

    @classmethod
    def content_pattern_equal(cls, content, pattern):
        """判断两个消息段是否相等"""
        if not content or not pattern:
            return False
        pattern = cls.content_disjoin(pattern)
        return len(content) == len(pattern) and all(
            cls._seg_match(c, p, strict=True) for c, p in zip(content, pattern)
        )
