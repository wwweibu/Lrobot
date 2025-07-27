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
        msg_logger.error(
            f"⌈{msg.num}⌋出错: '{Msg.content_join(msg.content) if Msg.content_join(msg.content) else msg.kind}' -> {e}",
            extra={"event": "消息处理"},
        )
        loggers["system"].error(traceback.format_exc(), extra={"event": "错误堆栈"})


async def safe_msg_process(msg: Msg):
    """消息处理"""
    print(msg)  # TODO 调试用

    if msg.event == "处理":
        msg_logger.info(
            f"⌈{msg.platform}⌋: {msg.kind} -> {Msg.content_join(msg.content) if Msg.content_join(msg.content) else msg.kind}",
            extra={"event": "消息处理"},
        )
        for commands in config["commands"]:
            if msg.platform not in commands["platforms"]:
                continue
            if msg.kind not in commands["kind"]:
                continue
            if msg.group:  # 群需要在 groups 列表里
                if commands["groups"]:
                    if not any(
                            msg.group in config["public"][group]
                            for group in commands["groups"]
                    ):
                        continue
            else:  # 个人需要身份在 users 列表里
                identity_list = await user_identify(msg.user, msg.platform)
                if commands["users"]:
                    if not any(
                            identity in identity_list for identity in commands["users"]
                    ):
                        continue
            # 如果待匹配状态为空，则用户任意状态都可以匹配
            # 如果待匹配状态不为空，则用户状态必须包含系统状态
            states = await status_check(msg.user if msg.user else "system")
            if commands["state"] and not any(
                    state in states for state in commands["state"]
            ):
                continue

            # 包含时，待匹配内容为空，匹配所有内容
            if commands["judge"] == "contains":
                if not commands["content"] or any(
                        Msg.content_pattern_contains(msg.content, val)
                        for val in commands["content"]
                ):
                    func = getattr(command, commands["function"])
                    await func(msg)
                    return
            else:
                for val in commands["content"]:
                    if Msg.content_pattern_equal(msg.content, val):
                        func = getattr(command, commands["function"])
                        await func(msg)
                        return

    elif msg.event.startswith("发送"):
        await msg_send(msg)
