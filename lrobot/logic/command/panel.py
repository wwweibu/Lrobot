"""功能面板相关"""

import re
from logic import data

from message.handler.msg import Msg


async def panel_task(msg: Msg):
    """新建或修改面板功能"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    func = parts[1].strip()
    match = re.match(r"^\s*(\d+)\s*[，,]\s*(.*)$", parts[2], re.S)  # 除了开头是数字，里面还有\n
    if match:
        index = int(match.group(1))
        task_content = match.group(2)
        await data.panel_task_edit(func, index, task_content)
    else:
        await data.panel_task_add(func, parts[2])


async def panel_func(msg: Msg):
    """新增面板功能组"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    await data.panel_add(parts[1].strip(), parts[2].strip())
