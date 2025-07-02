import re
from logic import data
from message.handler.msg import Msg


async def panel_add_func(msg:Msg):
    parts = re.split(r"[，,]", msg.content, maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    await data.add_panel(parts[1].strip(), parts[2].strip())


async def panel_add_task(msg:Msg):
    parts = re.split(r"[，,]", msg.content, maxsplit=2)
    while len(parts) < 3:
        parts.append("")
    await data.add_panel_task(parts[1].strip(), parts[2].strip())

