"""海龟汤游戏"""

import datetime

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter, loggers


def _format_surface(soup):
    """格式化汤面消息"""
    title = soup["title"] or ""
    parts = []
    if title:
        parts.append(f"【海龟汤·{title}】")
    else:
        parts.append("【海龟汤】")
    parts.append(f"作者：{soup['author']}")
    parts.append("")
    parts.append("汤面：")
    parts.append(soup["surface"])
    parts.append("")
    parts.append("想知道汤底？请回复 /海龟汤认领 担任主持人")
    return "\n".join(parts)


@monitor_adapter("/海龟汤_开始")
async def soup_start(msg: Msg):
    """抽取一条海龟汤发送汤面"""
    if not msg.group:
        return

    # 读取当前对局状态，切换时避免重复
    state = await data.soup_state_get(msg.group)
    exclude_id = state.get("soup_id") if state else None

    soup = await data.soup_random_get(exclude_id=exclude_id)
    if not soup:
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content="暂无可用海龟汤",
            user=msg.user,
            group=msg.group,
        )
        return

    # 写入对局状态（覆盖上一局，清空主持人）
    new_state = {
        "soup_id": soup["id"],
        "surface": soup["surface"],
        "bottom": soup["bottom"],
        "title": soup["title"],
        "author": soup["author"],
        "host_qq": None,
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    await data.soup_state_set(msg.group, new_state)

    content = _format_surface(soup)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/海龟汤_认领")
async def soup_claim(msg: Msg):
    """认领主持人，汤底私信发给认领者"""
    if not msg.group:
        return

    state = await data.soup_state_get(msg.group)
    if not state:
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content="当前没有进行中的海龟汤，请先发送 /海龟汤 抽取一题",
            user=msg.user,
            group=msg.group,
        )
        return

    if state.get("host_qq"):
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content="本局海龟汤已有主持人",
            user=msg.user,
            group=msg.group,
        )
        return

    # 记录主持人
    state["host_qq"] = msg.user
    await data.soup_state_set(msg.group, state)

    # 私信发汤底
    title = state.get("title") or ""
    header = f"【海龟汤·{title}】汤底" if title else "【海龟汤】汤底"
    bottom_content = f"{header}\n\n{state['bottom']}"
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=bottom_content,
        user=msg.user,
    )

    # 群里提示认领成功
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="已将汤底私信发送给认领者，请等待主持人引导",
        user=msg.user,
        group=msg.group,
    )
    return bottom_content
