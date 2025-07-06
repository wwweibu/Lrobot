import re
from logic import data
from message.handler.msg import Msg


async def panel_add_func(msg:Msg):
    # 为此项添加描述时会出现bug，因为/面板功能的匹配在/面板编辑上面，所以/面板编辑（任务），面板，0，/面板功能……会匹配到面板功能指令而不是面板编辑指令
    # 面板功能名和描述之后的修改只能手动在数据库中进行
    # 面板命令必须放在所有命令之前，否则会匹配到其他命令
    parts = re.split(r"[，,]", msg.content, maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    await data.add_panel(parts[1].strip(), parts[2].strip())


async def panel_add_task(msg:Msg):
    parts = re.split(r"[，,]", msg.content, maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    await data.add_panel_task(parts[1].strip(), parts[2])


async def panel_edit_task(msg:Msg):
    # 序号从0开始
    parts = re.split(r"[，,]", msg.content, maxsplit=3)
    while len(parts) < 4:
        parts.append("")
    await data.edit_panel_task(parts[1].strip(), parts[2].strip(),parts[3])