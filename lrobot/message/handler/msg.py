"""消息类"""

import time

from config import config


class Msg:
    """消息类"""

    __slots__ = (
        "num",  # 消息序号
        "platform",  # 平台
        "event",  # 触发事件
        "kind",  # 种类
        "seq",  # 平台原 ID
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
        attributes = {
            slot: getattr(self, slot)
            for slot in self.__slots__
            if hasattr(self, slot) and getattr(self, slot) is not None
        }
        return str(attributes)

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

    @classmethod
    def _content_token_match(cls, content):
        """解析 content 字符串中的消息段 [prefix:value]，支持 value 中嵌套 [] 的情况。"""
        result = []
        i = 0
        while i < len(content):
            if content[i] == "[":
                start = i
                i += 1
                colon_index = -1
                depth = 1
                while i < len(content):
                    if content[i] == "[":
                        depth += 1
                    elif content[i] == "]":
                        depth -= 1
                        if depth == 0:
                            break
                    elif content[i] == ":" and depth == 1 and colon_index == -1:
                        colon_index = i
                    i += 1
                if depth != 0:
                    raise ValueError(f"未闭合的消息段落: {content[start:i + 1]}")
                if colon_index != -1:
                    prefix = content[start + 1: colon_index]
                    value = content[colon_index + 1: i]
                else:
                    prefix = content[start + 1: i]  # 不带冒号的 [] 段
                    value = None
                result.append((prefix, value, start, i + 1))
                i += 1
            else:
                i += 1
        return result

    @classmethod
    def content_join(cls, content):
        """消息字段打印"""
        if not content:
            return
        content_join = ""
        for item in content:
            msg_type = item.get("type")
            msg_data = item.get("data", "")
            if msg_type == "text":
                content_join += msg_data.get("text", "")
            elif msg_type == "face":
                face_id = msg_data.get("id")
                face = config["emojis"].get(face_id)
                if not face:
                    face_text = msg_data.get("raw", {}).get("faceText")
                    if face_text is None:
                        raise Exception(f"无法解析的表情 | 表情: {item}")
                    face = face_text.strip("[]").lstrip("/")
                    # 将新表情添加至 emojis
                    emojis = config["emojis"]
                    emojis[face_id] = face
                    sorted_emojis = dict(
                        sorted(emojis.items(), key=lambda x: int(x[0]))
                    )  # 按照 key 以数字顺序排序(不加 int:1,10,2)
                    config["emojis"] = sorted_emojis
                content_join += f"[表情:{face}]"
            elif msg_type == "at":
                qq = msg_data.get("qq")
                content_join += f"[at:{qq}]"
            elif msg_type == "rps":
                rps_id = msg_data.get("result")
                rps_map = {"1": "布", "2": "剪刀", "3": "石头"}
                rps_result = rps_map.get(rps_id, "未知结果")
                content_join += f"[猜拳:{rps_result}]"
            elif msg_type == "dice":
                dice_id = msg_data.get("result")
                dice_result = dice_id if dice_id in {"1", "2", "3", "4", "5", "6"} else "未知结果"
                content_join += f"[骰子:{dice_result}]"
            elif msg_type == "reply":
                reply_content = msg_data.get("content", [])
                if reply_content:
                    content_join += f"[回复:[{Msg.content_join(reply_content)}]]"
                else:
                    content_join += f"[回复:[{msg_data.get('id')}]"
            elif msg_type == "forward":
                forward_content = msg_data.get("content", [])
                if forward_content:
                    inner_text = ""
                    for node in forward_content:
                        inner_msg_list = node.get("message", [])
                        inner_text += Msg.content_join(inner_msg_list)
                        inner_text += "|"
                    content_join += f"[转发:[{inner_text}]]"
                else:
                    content_join += f"[转发:[{msg_data.get('id')}]]"
            elif msg_type == "poke":
                content_join += "[戳戳:戳一戳]"
            elif msg_type == "mface":
                content_join += f"[动画表情:{msg_data.get('summary', '未知的动画表情')}]"
            elif msg_type == "image":
                summary = msg_data.get("summary", "")
                if summary:
                    content_join += f"[动画表情:{summary}]"
                else:
                    content_join += f"[图片:{msg_data.get('file', '未知的图片')}]"
            elif msg_type == "record":
                content_join += f"[语音:{msg_data.get('file', '未知的语音')}]"
            elif msg_type == "video":
                content_join += f"[视频:{msg_data.get('file', '未知的视频')}]"
            elif msg_type == "file":
                name = msg_data.get('name', '')
                if name:
                    content_join += f"[文件:{name}]"
                else:
                    content_join += f"[文件:{msg_data.get('file', '未知的文件')}]"
            elif msg_type == "json":
                data_str = msg_data.get('data', '')
                content_join += f"[卡片:{data_str.get('prompt', '未知的卡片')}]"
            elif msg_type == "node":
                forward_content = msg_data.get("content", [])
                inner_text = Msg.content_join(forward_content)
                content_join += f"[节点:{inner_text}]"
            else:
                raise Exception(f" 无法解析的消息段落 | 消息: {item}")
        return content_join

    @classmethod
    def content_disjoin(cls, content):
        """将字符串内容解析为消息字段"""
        if isinstance(content, list):
            return content
        content = str(content)
        segments = []
        parsed = cls._content_token_match(content)
        last_index = 0

        if not parsed or all(p[1] is None for p in parsed):  # 纯文字消息
            return [{"type": "text", "data": {"text": content}}]

        for prefix, value, start, end in parsed:  # value 一定为字符串

            # 添加之前的纯文本部分
            if start > last_index:
                plain_text = content[last_index:start]
                segments.append({"type": "text", "data": {"text": plain_text}})
            last_index = end

            # 根据匹配的结构添加消息段
            if prefix == "表情":
                segments.append(
                    {
                        "type": "face",
                        "data": {
                            "id": next((k for k, v in config["emojis"].items() if v == value), None)
                        },
                    }
                )
            elif prefix == "at":
                segments.append({"type": "at", "data": {"qq": value}})
            elif prefix == "猜拳":
                rps_reverse = {"布": "1", "剪刀": "2", "石头": "3"}
                segments.append(
                    {"type": "rps", "data": {"result": rps_reverse.get(value, "any")}}
                )
            elif prefix == "骰子":
                dice_value = value if value in {"1", "2", "3", "4", "5", "6"} else "any"
                segments.append({"type": "dice", "data": {"result": dice_value}})
            elif prefix == "回复":
                segments.append({"type": "reply", "data": {"id": value}})
            elif prefix == "转发":
                segments.append({"type": "forward", "data": {"id": value}})
            elif prefix == "戳戳":
                segments.append({"type": "poke", "data": {"type": "1", "id": "1"}})
            elif prefix == "动画表情":
                if "|" in value:  # 发送格式: summary|name(LR5921)
                    summary, name = value.split("|")
                    if name in config["shop_emojis"]:
                        raw = config["shop_emojis"][name]
                        key, emoji_id, emoji_package_id = raw.split("|")
                        segments.append({"type": "mface", "data": {"summary": summary, "key": key, "emoji_id": emoji_id,
                                                                   "emoji_package_id": emoji_package_id}})
                else:  # 判断格式: summary;发送格式: summary(BILI)
                    segments.append({"type": "image", "data": {"summary": value}})
            elif prefix == "图片":
                if "|" in value:  # 发送格式: summary|file(LR5921)
                    summary, file = value.split("|")
                    segments.append(
                        {"type": "image", "data": {"file": file, "summary": summary}}
                    )
                else:  # 判断格式: file;发送格式: file(BILI)
                    segments.append({"type": "image", "data": {"file": value}})
            elif prefix == "语音":
                segments.append({"type": "record", "data": {"file": value}})
            elif prefix == "视频":
                if "|" in value:  # 发送格式: file|title|description(WECHAT)
                    file, title, description = value.split("|")
                    segments.append(
                        {"type": "video", "data": {"file": file, "title": title, "description": description}})
                else:
                    segments.append({"type": "video", "data": {"file": value}})
            elif prefix == "文件":
                if "|" in value:  # 发送格式: file|name(LR5921)
                    file, name = value.split("|")
                    segments.append(
                        {"type": "file", "data": {"file": file, "name": name}}
                    )
                else:  # 判断格式: file;发送格式: file(LR5921)
                    segments.append({"type": "file", "data": {"file": value}})
            elif prefix == "卡片":
                if "|" in value:
                    value_list = value.split("|")
                    if value_list[0] == "微信-音乐":
                        # 发送格式: 微信-音乐|title|description|url
                        prompt, title, description, url = value.split("|")
                        segments.append(
                            {
                                "type": "json",
                                "data":
                                    {
                                        "data":
                                            {
                                                "prompt": prompt,
                                                "title": title,
                                                "description": description,
                                                "url": url
                                            }}})
                    elif value_list[0] == "微信-图文":
                        # 发送格式: 微信-图文|title|description|picurl|url
                        prompt, title, description, picurl, url = value.split("|")
                        segments.append(
                            {
                                "type": "json",
                                "data": {
                                    "data": {
                                        "prompt": prompt,
                                        "title": title,
                                        "description": description,
                                        "picurl": picurl,
                                        "url": url,
                                    }
                                },
                            }
                        )
                else:
                    # 判断格式: prompt;发送格式: data(LR5921)
                    segments.append({"type": "json", "data": {"data": value}})
            elif prefix == "转发":  # 发送格式: id
                segments.append({"type": "forward", "data": {"id": value}})
            elif prefix == "节点":  # 发送格式: user_id|nickname|[消息列表段]
                user_id, nickname, content = value.split("|", 2)
                node_data = {
                    "type": "node",
                    "data": {
                        "user_id": user_id,
                        "nickname": nickname,
                        "content": Msg.content_disjoin(content)
                    }
                }
                segments.append(node_data)
            else:
                raise Exception(f"未知消息段类型 -> {prefix} : {value}")

        # 末尾如果还有文本
        if last_index < len(content):
            segments.append({"type": "text", "data": {"text": content[last_index:]}})

        return segments

    @classmethod
    def content_pattern_contains(cls, content, pattern):
        """判断消息字段是否包含指令字段"""
        if not content:
            return False
        pattern = Msg.content_disjoin(pattern)
        pattern_len = len(pattern)
        content_len = len(content)

        for i in range(content_len - pattern_len + 1):
            # 比较 pattern 消息列表是否与 content[i: i+ len] 消息列表完全相同
            match = True
            for j in range(pattern_len):
                pattern_seg = pattern[j]
                content_seg = content[i + j]
                if not Msg.content_match(content_seg, pattern_seg):
                    match = False
                    break
            if match:
                return True
        return False

    @classmethod
    def content_match(cls, content, pattern):
        """判断消息列表中某项是否包含某项"""
        if content["type"] != pattern["type"]:
            return False

        content_data = content.get("data", {})
        pattern_data = pattern.get("data", {})

        if content["type"] == "text":
            if pattern_data.get("text") == " ":
                return True
            return pattern_data.get("text", "") in content_data.get("text", "")

        elif content["type"] == "at":
            return pattern_data.get("qq") in (content_data.get("qq"), "any")

        elif content["type"] in ["rps", "dice"]:
            return pattern_data.get("result") in (content_data.get("result"), "any")

        elif content["type"] in ["face", "reply"]:
            return pattern_data.get("id") in (content_data.get("id"), "any")

        elif content["type"] == "poke":
            return True

        elif content["type"] == "image":
            pattern_result = pattern_data.get("summary")
            if pattern_result:  # 动画表情
                return pattern_result in (content_data.get("summary"), "any")
            else:
                if not content_data.get("summary"):
                    return pattern_data.get("file") in (content_data.get("file"), "any")

        elif content["type"] in ["record", "video", "file"]:
            return pattern_data.get("file") in (content_data.get("file"), "any")

        elif content["type"] == "json":  # 匹配字段是 data:prompt，消息字段是 data:{prompt:prompt}
            return pattern_data.get("data") in (content_data.get("prompt"), "any")

        # 指令匹配中不出现"节点""转发"
        return False

    @staticmethod
    def content_pattern_equal(content, pattern):
        """判断两个消息段是否相等"""
        if not content:
            return False
        pattern = Msg.content_disjoin(pattern)
        if len(content) != len(pattern):
            return False

        for content_seg, pattern_seg in zip(content, pattern):
            if content_seg["type"] != pattern_seg["type"]:
                return False

            content_data = content_seg.get("data", {})
            pattern_data = pattern_seg.get("data", {})

            if content_seg["type"] == "text":
                if pattern_data.get("text", "") != content_data.get("text", ""):
                    return False

            elif content_seg["type"] == "at":
                if pattern_data.get("qq") not in ("any", content_data.get("qq")):
                    return False

            elif content_seg["type"] in ["rps", "dice"]:
                if pattern_data.get("result") not in ("any", content_data.get("result")):
                    return False

            elif content_seg["type"] in ["face", "reply"]:
                if pattern_data.get("id") not in ("any", content_data.get("id")):
                    return False

            elif content_seg["type"] == "image":
                pattern_result = pattern_data.get("summary")
                if pattern_result:  # 动画表情
                    if pattern_result not in ("any", content_data.get("summary")):
                        return False
                else:
                    if pattern_data.get("file") not in ("any", content_data.get("file")):
                        return False

            elif content_seg["type"] in ["record", "video", "file"]:
                if pattern_data.get("file") not in ("any", content_data.get("file")):
                    return False

            elif content_seg["type"] == "json":
                if pattern_data.get("data") not in ("any", content_data.get("prompt")):
                    return False

            elif content_seg["type"] in ["node", "forward"]:
                return False  # 不能接收节点字段，不匹配转发字段

            # TODO poke
        return True
