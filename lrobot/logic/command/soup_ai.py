"""海龟汤 AI 主持人"""

import asyncio
import datetime
import time
import uuid
from collections import OrderedDict

from logic import data
from logic.data.soup_llm import llm_end_session, llm_judge_question
from message.handler.msg import Msg
from config import monitor_adapter


# 对话缓存使用 LRU + TTL + 数量上限，避免异常退出的对局永久留存。
_ai_history_cache = OrderedDict()
_MAX_HISTORY_ROUNDS = 20
_MAX_HISTORY_CHARS = 12000
_MAX_HISTORY_SESSIONS = 100
_HISTORY_TTL = 6 * 60 * 60
_MAX_QUESTION_CHARS = 2000
_MAX_PENDING = 8
_AI_CONCURRENCY = 2
_ai_semaphore = asyncio.Semaphore(_AI_CONCURRENCY)
_ai_pending = 0


def _state_key(msg):
    """获取状态 key（群聊用群号，私聊用用户）"""
    return msg.group or msg.user


def _send(msg, content):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


def _purge_history_cache():
    cutoff = time.monotonic() - _HISTORY_TTL
    for key in list(_ai_history_cache):
        if _ai_history_cache[key]["updated_at"] >= cutoff:
            continue
        _ai_history_cache.pop(key, None)
    while len(_ai_history_cache) > _MAX_HISTORY_SESSIONS:
        _ai_history_cache.popitem(last=False)


def _history_entry(state_key, *, reset=False):
    _purge_history_cache()
    if reset or state_key not in _ai_history_cache:
        _ai_history_cache[state_key] = {
            "messages": [],
            "lock": asyncio.Lock(),
            "updated_at": time.monotonic(),
        }
    entry = _ai_history_cache[state_key]
    entry["updated_at"] = time.monotonic()
    _ai_history_cache.move_to_end(state_key)
    _purge_history_cache()
    return entry


def _append_history(entry, question, answer):
    messages = entry["messages"]
    messages.append({"role": "user", "content": question})
    messages.append({"role": "assistant", "content": answer})
    del messages[:max(0, len(messages) - _MAX_HISTORY_ROUNDS * 2)]
    while messages and sum(len(item.get("content", "")) for item in messages) > _MAX_HISTORY_CHARS:
        del messages[:min(2, len(messages))]
    entry["updated_at"] = time.monotonic()


async def soup_ai_reset(state_key, session_id=None):
    """新开一局或结束时回收 AI 局内缓存。"""
    _ai_history_cache.pop(state_key, None)
    await llm_end_session(session_id)


@monitor_adapter("/海龟汤AI_开始")
async def soup_ai_start(msg: Msg):
    """开启 AI 主持人模式"""
    state_key = _state_key(msg)

    # 检查是否有对局
    soup_state = await data.soup_state_get(state_key)
    if not soup_state:
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

    # 检查是否已开启 AI 模式
    if soup_state.get("ai_host"):
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content="AI 主持人模式已在本局开启",
            user=msg.user,
            group=msg.group,
        )
        return

    # 设置 AI 主持人状态
    soup_state["ai_host"] = True
    soup_state["ai_started_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    soup_state["ai_session_id"] = uuid.uuid4().hex
    await data.soup_state_set(state_key, soup_state)

    # 初始化对话历史和同局串行锁
    _history_entry(state_key, reset=True)

    content = (
        "【AI 主持人模式已开启】\n"
        "现在由 AI 担任本局海龟汤主持人！\n"
        "以「问」开头提问，AI 会回答「是/否/是或不是/无关」\n"
        "仍以「问」开头描述你还原的真相，覆盖核心真相后会自动判定答对\n"
        "发送 /海龟汤AI结束 退出 AI 模式"
    )
    # 人类主持人已存在时，补充提示
    if soup_state.get("host_qq"):
        content += "\n（本局已有人类主持人，汤底已私信发送给主持人）"
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


@monitor_adapter("/海龟汤AI_回答")
async def soup_ai_answer(msg: Msg):
    """AI 主持人回答玩家问题"""
    global _ai_pending
    state_key = _state_key(msg)

    soup_state = await data.soup_state_get(state_key)
    if not soup_state or not soup_state.get("ai_host"):
        return

    question = Msg.content_join(msg.content).strip()
    if not question:
        return
    if len(question) > _MAX_QUESTION_CHARS:
        _send(msg, f"[回复:{msg.seq}]问题过长，请限制在 {_MAX_QUESTION_CHARS} 字以内")
        return
    if _ai_pending >= _MAX_PENDING:
        _send(msg, f"[回复:{msg.seq}]AI 主持人当前繁忙，请稍后重试")
        return

    _ai_pending += 1
    entry = _history_entry(state_key)
    try:
        async with _ai_semaphore:
            async with entry["lock"]:
                # 等待期间可能已结束/更换对局，必须重新校验。
                soup_state = await data.soup_state_get(state_key)
                if not soup_state or not soup_state.get("ai_host"):
                    return
                if _ai_history_cache.get(state_key) is not entry:
                    return

                session_id = soup_state.get("ai_session_id")
                if not session_id:
                    session_id = uuid.uuid4().hex
                    soup_state["ai_session_id"] = session_id
                    await data.soup_state_set(state_key, soup_state)

                result = await llm_judge_question(
                    soup_state["surface"],
                    soup_state["bottom"],
                    question,
                    list(entry["messages"]),
                    session_id,
                )
                # LLM 等待期间可能结束/更换对局，或者有人类主持人更新状态。
                # 丢弃旧回答；需要落库时使用最新状态，避免覆盖并发更新。
                latest_state = await data.soup_state_get(state_key)
                if (
                    _ai_history_cache.get(state_key) is not entry
                    or not latest_state
                    or not latest_state.get("ai_host")
                    or latest_state.get("ai_session_id") != session_id
                ):
                    return
                answer = result["content"]
                _append_history(entry, question, answer)

                if result["type"] == "win":
                    await soup_ai_reset(state_key, session_id)
                    latest_state["ai_host"] = False
                    latest_state.pop("ai_session_id", None)
                    await data.soup_state_set(state_key, latest_state)

        _send(msg, f"[回复:{msg.seq}]{answer}")
        return answer
    finally:
        _ai_pending -= 1


@monitor_adapter("/海龟汤AI_结束")
async def soup_ai_end(msg: Msg):
    """结束 AI 主持人模式"""
    state_key = _state_key(msg)
    entry = _history_entry(state_key)
    async with entry["lock"]:
        soup_state = await data.soup_state_get(state_key)
        if not soup_state or not soup_state.get("ai_host"):
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content="当前没有 AI 主持的海龟汤对局",
                user=msg.user,
                group=msg.group,
            )
            return

        await _soup_ai_cleanup(state_key, soup_state.get("ai_session_id"))
        soup_state["ai_host"] = False
        soup_state.pop("ai_session_id", None)
        await data.soup_state_set(state_key, soup_state)

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="AI 主持人模式已结束，可发送 /海龟汤 抽取新题目",
        user=msg.user,
        group=msg.group,
    )


async def _soup_ai_cleanup(state_key, session_id=None):
    """清理 AI 主持人相关状态"""
    await soup_ai_reset(state_key, session_id)


# ---- Judge 函数 ----

async def soup_ai_judge(msg: Msg):
    """判断是否拦截群消息（以"问"开头且在 AI 模式下）"""
    if not msg.group:
        return False

    text = Msg.content_join(msg.content).strip()
    if not text.startswith("问"):
        return False

    soup_state = await data.soup_state_get(msg.group)
    if not soup_state or not soup_state.get("ai_host"):
        return False

    return True


async def soup_ai_end_judge(msg: Msg):
    """判断是否为 /海龟汤AI结束"""
    text = Msg.content_join(msg.content).strip()
    if text != "/海龟汤AI结束":
        return False
    if not msg.group:
        return False
    soup_state = await data.soup_state_get(msg.group)
    return bool(soup_state and soup_state.get("ai_host"))
