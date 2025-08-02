"""航海日记"""

from logic import data
from config import path
from message.handler.msg import Msg


async def diary_prompt(msg: Msg):
    """题目提示词"""
    diary_prompts = {
        "diary_1": "摩斯电码",
        "diary_2": "繁体，培根",
        "diary_3": "'生母','复孕',两张表",
        "diary_4": "摩斯，屋檐一根",
        "diary_5": "摩斯，7个字",
        "diary_6": "数数，找不同",
        "diary_7": "字母表",
        "diary_8": "13凯撒",
        "diary_9": "键盘，凯撒",
        "diary_10": "摩斯",
        "diary_11": "/",
        "diary_12": "/",
        "diary_13": "213三个字",
        "diary_14": "/",
        "diary_15": "5*3*2/5=6，每个竖着写",
        "diary_16": "/",
    }
    status_list = await data.status_check(msg.user)
    content = ""
    for status in status_list:
        if status in diary_prompts:
            prompt = diary_prompts[status]
            content = prompt
            break
    Msg(
        platform=msg.platform,
        kind=f"{msg.kind[:2]}发送",
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


async def diary_common(n, msg: Msg):
    """通用函数"""
    msg_kind = msg.kind[:2]
    kind = f"{msg_kind}发送"
    if n < 17:
        await data.status_add(msg.user, f"diary_{n}")
    if n > 1:
        await data.status_delete(msg.user, f"diary_{n - 1}")

    Msg(
        platform=msg.platform,
        kind=kind,
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=Msg.content_disjoin(f"[图片:{path}/storage/file/command/diary/{n}.png]"),
        group=msg.group,
    )


async def diary_1(msg: Msg):
    status_list = await data.status_check(msg.user)
    for status in status_list:
        if status.startswith("diary_"):
            Msg(
                platform=msg.platform,
                kind=f"{msg.kind[:2]}发送",
                event="发送",
                user=msg.user,
                seq=msg.seq,
                content="所有答案的形式均为小写英文字母/数字/中文\n"
                        "且中间无空格\n"
                        "输入'航海日记提示'获取当前题目的提示\n"
                        "可在绑定的多平台同步答题\n"
                        "不要过于依赖提示哦＞﹏＜",
                group=msg.group,
            )
            return
    await diary_common(1, msg)


async def diary_2(msg: Msg):
    await diary_common(2, msg)


async def diary_3(msg: Msg):
    await diary_common(3, msg)


async def diary_4(msg: Msg):
    await diary_common(4, msg)


async def diary_5(msg: Msg):
    await diary_common(5, msg)


async def diary_6(msg: Msg):
    await diary_common(6, msg)


async def diary_7(msg: Msg):
    await diary_common(7, msg)


async def diary_8(msg: Msg):
    await diary_common(8, msg)


async def diary_9(msg: Msg):
    await diary_common(9, msg)


async def diary_10(msg: Msg):
    await diary_common(10, msg)


async def diary_11(msg: Msg):
    await diary_common(11, msg)


async def diary_12(msg: Msg):
    await diary_common(12, msg)


async def diary_13(msg: Msg):
    await diary_common(13, msg)


async def diary_14(msg: Msg):
    await diary_common(14, msg)


async def diary_15(msg: Msg):
    await diary_common(15, msg)


async def diary_16(msg: Msg):
    await diary_common(16, msg)


async def diary_17(msg: Msg):
    await diary_common(17, msg)
