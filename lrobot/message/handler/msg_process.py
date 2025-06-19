# 消息处理
import traceback
from config import config,loggers
from message.handler.msg import Msg
from message.handler.msg_send import msg_send
from logic import check_status,command,forward_all

msg_logger = loggers["message"]


async def msg_process(msg):
    """消息处理错误捕获"""
    try:
        await safe_msg_process(msg)
    except Exception as e:
        error_trace = traceback.format_exc()
        msg_logger.error(
            f"⌈{msg.num}⌋出错: '{msg.content}' -> {e}", extra={"event": "消息处理"}
        )
        print(error_trace)  # 开发用


async def safe_msg_process(msg: Msg):
    """消息处理"""
    states = await check_status(msg.source)
    if msg.event == "处理":
        if msg.content.startswith("/"):
            msg.event = "功能"
        else:
            if "对话" in states:
                msg.event = "对话"
            elif "游戏" in states:
                msg.event = "游戏"
            else:
                msg.event = "其他"
    msg_logger.info(
        f"⌈{msg.robot}⌋{msg.event}: {msg.kind} -> {msg.content}",
        extra={"event": f"消息处理"},
    )
    if msg.event == "功能":
        for commands in config["commands"]:
            if msg.robot not in commands["platforms"]:
                continue
            if msg.kind not in commands["kind"]:
                continue
            if msg.group and commands["groups"]:
                if not any(
                        msg.group in config["群聊"][group]
                        for group in commands["groups"]
                ):
                    continue
            # 如果系统状态为空，则用户任意状态都可以匹配
            # 如果系统状态不为空，则用户状态必须包含系统状态
            if commands["state"] and not any(
                state in states for state in commands["state"]
            ):
                continue
            # 如果系统内容为空，则匹配所有 in，不匹配所有非空 equal
            # 如果 in 为空，则匹配所有内容
            if commands["judge"] == "contains":
                if not commands["content"] or any(
                    val in msg.content for val in commands["content"]
                ):
                    func_name = commands["function"]
                    func = getattr(command, func_name)
                    await func(msg)
                    return
            else:
                if msg.content in command["content"]:
                    func_name = commands["function"]
                    func = getattr(command, func_name)
                    await func(msg)
                    return
        # 如果没有匹配的指令，返回格式错误提示，并转发给管理员
        await forward_all(msg)

    elif msg.event.endswith("发送"):
        await msg_send(msg)
    elif msg.event == "对话":
        pass
    elif msg.event == "游戏":
        pass
    else:
        raise Exception(f"未知的消息格式 | 消息: {msg}")


