"""消息处理"""

import traceback

from config import config, loggers
from message.handler.msg import Msg
from message.handler.msg_send import msg_send
from logic import status_check, user_identify, command

msg_logger = loggers["message"]


async def msg_process(msg):
    """消息处理错误捕获"""
    try:
        await safe_msg_process(msg)
    except Exception as e:
        content_str = Msg.content_join(msg.content) or msg.kind
        msg_logger.error(
            f"⌈{msg.num}⌋出错: '{content_str}' -> {e}",
            extra={"event": "消息处理"},
        )
        loggers["system"].error(traceback.format_exc(), extra={"event": "错误堆栈"})


async def safe_msg_process(msg: Msg):
    """消息处理"""
    print(msg)  # 调试用

    content_str = Msg.content_join(msg.content) or msg.kind

    if msg.event == "处理":
        msg_logger.info(
            f"⌈{msg.platform}⌋: {msg.kind} -> {content_str}",
            extra={"event": "消息处理"},
        )
        for commands in config["commands"]:
            # 平台和消息类型
            if msg.platform not in commands["platforms"] or msg.kind not in commands["kind"]:
                continue
            if msg.group:  # 群需要在 groups 列表里
                if commands["groups"] and not any(msg.group in config["public"][group] for group in commands["groups"]):
                    continue
            else:  # 个人需要身份在 users 列表里
                if commands["users"]:
                    identity_list = await user_identify(msg.user, msg.platform)
                    if not any(
                            identity in identity_list for identity in commands["users"]
                    ):
                        continue
            # 如果待匹配状态为空，则用户任意状态都可以匹配
            # 如果待匹配状态不为空，则用户状态必须包含系统状态
            if commands["state"]:
                states = await status_check(msg.user if msg.user else "system")
                if not any(state in states for state in commands["state"]):
                    continue

            # 包含时，待匹配内容为空，匹配所有内容
            judge = commands["judge"]
            contents = commands["content"]
            matched = (
                (not contents or any(Msg.content_pattern_contains(msg.content, v) for v in contents))
                if judge == "contains"
                else any(Msg.content_pattern_equal(msg.content, v) for v in contents)
            )
            if not matched:
                continue
            func = getattr(command, commands["function"])
            await func(msg)
            return

    elif msg.event.startswith("发送"):
        await msg_send(msg)
