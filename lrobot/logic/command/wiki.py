import re
from logic import data
from message.handler.msg import Msg


async def wiki_change_get(msg:Msg):
    kind = msg.kind[:2]
    parts = re.split(r"[，,]", msg.content, maxsplit=1)
    while len(parts) < 2:
        return
    content = await data.get_wiki(parts[1].strip())
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


async def wiki_change(msg:Msg):
    parts = re.split(r"[，,]", msg.content, maxsplit=2)
    while len(parts) < 3:
        return
    await data.set_wiki(parts[1].strip(), parts[2])