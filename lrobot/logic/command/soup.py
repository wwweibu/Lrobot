"""海龟汤游戏"""

import asyncio
import datetime

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter


# 全局锁，保护同一时刻只有一个认领操作在读写状态
_soup_claim_lock = asyncio.Lock()


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
    """抽取一条海龟汤发送汤面，支持 /海龟汤 [标题] 按标题开局"""
    text = Msg.content_join(msg.content).strip()
    parts = text.split(" ", 1)
    title = parts[1].strip() if len(parts) == 2 else ""

    if title:
        rows = await data.soup_find_by_title(title)
        if not rows:
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=f"未找到标题为'{title}'的海龟汤",
                user=msg.user,
                group=msg.group,
            )
            return
        soup = rows[0]
    else:
        # 读取当前对局状态，切换时避免重复（群聊按群，私聊按用户）
        state_key = msg.group or msg.user
        state = await data.soup_state_get(state_key)
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

    # 群聊写入对局状态（覆盖上一局，清空主持人）；私聊不记状态
    if msg.group:
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

    async with _soup_claim_lock:
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
            host = state["host_qq"]
            if host == msg.user:
                content = "你已经是本局海龟汤的主持人了"
            else:
                content = "本局海龟汤已有主持人"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
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


# ---- 上传：多轮输入状态机 ----
# 状态 "海龟汤上传1"：等输入标题（可空）
# 状态 "海龟汤上传2"：等输入作者（可空，默认全民制作人）
# 状态 "海龟汤上传3"：等输入汤面
# 状态 "海龟汤上传4"：等输入汤底
# info 字段累积已输入内容

_UPLOAD_STEPS = [
    # (step_status, next_status, field, prompt)
    ("海龟汤上传1", "海龟汤上传2", "title", "请输入标题"),
    ("海龟汤上传2", "海龟汤上传3", "author", "请输入作者（留空默认'全民制作人'）"),
    ("海龟汤上传3", "海龟汤上传4", "surface", "请输入汤面"),
    ("海龟汤上传4", None, "bottom", "请输入汤底"),
]


def _upload_step(status):
    """根据当前状态查下一步配置"""
    for cur, nxt, field, prompt in _UPLOAD_STEPS:
        if cur == status:
            return nxt, field, prompt
    return None, None, None


@monitor_adapter("/海龟汤_上传")
async def soup_upload(msg: Msg):
    """开始上传海龟汤流程"""
    await data.status_add(msg.user, msg.platform, "海龟汤上传1", {"title": "", "author": "", "surface": "", "bottom": ""})
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content="开始上传海龟汤，请按提示依次输入\n发送 /取消 可随时取消",
    )
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=_UPLOAD_STEPS[0][3],
    )


@monitor_adapter("/海龟汤_上传_输入")
async def soup_upload_input(msg: Msg):
    """接收上传流程的每一步输入"""
    status = await data.status_check(msg.user, msg.platform)
    # status 是用户当前状态列表
    cur_status = None
    for s in status or []:
        if s.startswith("海龟汤上传"):
            cur_status = s
            break
    if not cur_status:
        return

    # 用户主动取消
    if Msg.content_join(msg.content).strip() in ("/海龟汤取消", "/取消"):
        await data.status_delete(msg.user, msg.platform, cur_status)
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            content="已取消海龟汤上传",
            user=msg.user,
        )
        return

    info = await data.status_check(msg.user, msg.platform, cur_status) or {}
    nxt, field, prompt = _upload_step(cur_status)
    text = Msg.content_join(msg.content).strip()

    # 作者允许为空，标题必填
    if field == "author":
        info[field] = "" if text in ("", "/取消") else text
    else:
        if not text:
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                content=f"{field}不能为空，请重新输入",
                user=msg.user,
            )
            return
        info[field] = text

    if nxt is None:
        # 最后一步完成，写入数据库
        title = info.get("title", "") or ""
        author = info.get("author", "") or "全民制作人"
        surface = info.get("surface", "")
        bottom = info.get("bottom", "")
        await data.soup_add(title, author, surface, bottom)
        await data.status_delete(msg.user, msg.platform, cur_status)
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            content=f"海龟汤上传成功\n标题：{title or '(无)'}\n作者：{author}\n汤面：{surface[:30]}...\n汤底：{bottom}",
            user=msg.user,
        )
    else:
        await data.status_add(msg.user, msg.platform, nxt, info)
        _, _, next_prompt = _upload_step(nxt)
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            content=next_prompt,
            user=msg.user,
        )


@monitor_adapter("/海龟汤_取消")
async def soup_cancel(msg: Msg):
    """取消上传流程"""
    status = await data.status_check(msg.user, msg.platform) or []
    upload_status = next((s for s in status if s.startswith("海龟汤上传")), None)
    if upload_status:
        await data.status_delete(msg.user, msg.platform, upload_status)
        content = "已取消海龟汤上传"
    else:
        content = "当前没有进行中的海龟汤上传"
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
    )


# ---- 删除：二次确认 ----
@monitor_adapter("/海龟汤_删除")
async def soup_delete(msg: Msg):
    """删除海龟汤：不带名称删最近一题，带名称按标题删"""
    parts = Msg.content_join(msg.content)
    parts = parts.split(" ", 1)
    title = parts[1].strip() if len(parts) == 2 else ""

    if title:
        rows = await data.soup_find_by_title(title)
        if not rows:
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=f"未找到标题为'{title}'的海龟汤",
                user=msg.user,
                group=msg.group,
            )
            return
        soup = rows[0]
    else:
        # 没指定名称，删当前群最近开过的
        if not msg.group:
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                content="请指定要删除的海龟汤名称，或在群内使用此指令",
                user=msg.user,
            )
            return
        state = await data.soup_state_get(msg.group)
        if not state or not state.get("soup_id"):
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content="当前群没有开过的海龟汤，请指定名称删除",
                user=msg.user,
                group=msg.group,
            )
            return
        soup = await data.soup_get(state["soup_id"])
        if not soup:
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content="要删除的海龟汤已不存在",
                user=msg.user,
                group=msg.group,
            )
            return

    # 进入二次确认状态
    await data.status_add(msg.user, msg.platform, "海龟汤删除", {
        "soup_id": soup["id"],
        "title": soup["title"] or "",
    })
    title_display = soup["title"] or "(无标题)"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=f"确认删除海龟汤【{title_display}】？\n回复'是'确认删除，其他内容取消",
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/海龟汤_删除_确认")
async def soup_delete_confirm(msg: Msg):
    """二次确认删除"""
    info = await data.status_check(msg.user, msg.platform, "海龟汤删除")
    if not info:
        return
    answer = Msg.content_join(msg.content).strip()
    if answer in ("是", "确认", "yes", "YES"):
        await data.soup_delete_by_id(info["soup_id"])
        title = info.get("title") or "(无标题)"
        content = f"已删除海龟汤【{title}】"
    else:
        content = "已取消删除"
    await data.status_delete(msg.user, msg.platform, "海龟汤删除")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


# ---- 查询 ----
@monitor_adapter("/海龟汤_查询")
async def soup_query(msg: Msg):
    """按名称或作者查询海龟汤"""
    parts = Msg.content_join(msg.content).split(" ", 1)
    keyword = parts[1].strip() if len(parts) == 2 else ""
    if not keyword:
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content="请输入查询关键字，如 /海龟汤查询 半根火柴",
            user=msg.user,
            group=msg.group,
        )
        return
    rows = await data.soup_search(keyword)
    if not rows:
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content=f"未找到与'{keyword}'相关的海龟汤",
            user=msg.user,
            group=msg.group,
        )
        return
    lines = [f"共找到 {len(rows)} 条："]
    for r in rows:
        title = r["title"] or "(无标题)"
        lines.append(f"[{r['id']}] {title} / {r['author']}")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="\n".join(lines),
        user=msg.user,
        group=msg.group,
    )


# ---- 状态机判断函数（供 yaml function judge 使用）----
async def soup_upload_input_judge(msg: Msg):
    """判断用户是否处于海龟汤上传流程中"""
    status = await data.status_check(msg.user, msg.platform)
    if not status:
        return False
    return any(s.startswith("海龟汤上传") for s in status)


async def soup_delete_confirm_judge(msg: Msg):
    """判断用户是否处于海龟汤删除确认状态"""
    status = await data.status_check(msg.user, msg.platform)
    return bool(status and "海龟汤删除" in status)
