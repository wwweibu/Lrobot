import sys
import traceback
import importlib
from config import config,loggers
from message.handler.msg import Msg
from message.handler.msg_send import msg_send
#from logic import check_status, identify_user, chat, forward_all


msg_logger = loggers["message"]


async def msg_process(msg):
    """消息处理"""
    try:
        await safe_msg_process(msg)
    except Exception as e:
        error_trace = traceback.format_exc()
        msg_logger.error(
            f"⌈{msg.num}⌋出错:'{msg.content}'->{e}", extra={"event": "消息处理错误"}
        )
        print(error_trace)  # 开发用


async def safe_msg_process(msg: Msg):
    print(msg)
    return
    qq = await identify_user(msg.source, msg.robot)
    if qq:
        states = await check_status(qq)  # 用户状态
    else:
        states = []
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
        f"⌈{msg.robot}⌋:{msg.kind}->{msg.content}",
        extra={"event": f"{msg.event}消息"},
    )
    print(msg)
    if msg.event == "功能":
        for command in config["commands"]:
            if msg.robot not in command["platforms"]:
                continue
            if msg.kind not in command["kind"]:
                continue
            # 如果没有用户组，即所有用户都能使用
            if command["users"]:
                result = await check_user(qq, command["users"], 1)
                if not result:
                    continue
            if msg.group and command["groups"]:
                result = await check_user(msg.group, command["groups"], 0)
                if not result:
                    continue
            # 如果系统状态为空，则用户任意状态都可以匹配
            # 如果系统状态不为空，则用户状态必须包含系统状态
            if command["state"] and not any(
                state in states for state in command["state"]
            ):
                continue
            # 如果系统内容为空，则匹配所有 in，不匹配所有非空 equal
            # 如果 in 为空，则匹配所有内容
            if command["judge"] == "contains":
                if not command["content"] or any(
                    val in msg.content for val in command["content"]
                ):
                    await load_module(command["function"], msg)
                    return
            else:
                if msg.content in command["content"]:
                    await load_module(command["function"], msg)
                    return

        # 如果没有匹配的指令，返回格式错误提示，并转发给管理员
        await forward_all(msg)

    elif msg.event.endswith("发送"):
        await msg_send(msg)
    elif msg.event == "对话":
        await chat(msg)
    elif msg.event == "游戏":
        pass
    else:
        print(f"未知的消息格式 | 消息: {msg}")


async def load_module(function, msg: Msg):
    # 动态加载模块并执行函数
    module_path = f"logic.command.{function.split('_', 1)[0]}"
    # 清理模块缓存
    if module_path in sys.modules:
        del sys.modules[module_path]
    module = importlib.import_module(module_path)
    func = getattr(module, function)
    await func(msg)


async def check_user(qq, users_list, is_private=0):
    """
    判断参数是否在指定用户的私聊/群聊列表中。
    """
    if is_private == 1:  # 私聊
        for user in users_list:
            if user == ["社员"]:
                if qq:
                    return 1
            else:
                if user in config["私聊"] and qq in config["私聊"][user]:
                    return 1
    else:  # 群聊
        for user in users_list:
            if user in config["群聊"] and qq in config["群聊"][user]:
                return 1
    return 0
