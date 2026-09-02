"""海龟汤 AI 主持人"""

import datetime
import uuid

from logic import data
from logic.data.soup_llm import llm_end_session, llm_judge_question
from message.handler.msg import Msg
from config import monitor_adapter


# 对话历史缓存：{state_key: [{"role": "user", "content": "..."}, ...]}
_ai_history_cache = {}

# 最大历史轮数
_MAX_HISTORY_ROUNDS = 20


def _state_key(msg):
    """获取状态 key（群聊用群号，私聊用用户）"""
    return msg.group or msg.user


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

    # 初始化对话历史
    _ai_history_cache[state_key] = []

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
    state_key = _state_key(msg)

    soup_state = await data.soup_state_get(state_key)
    if not soup_state or not soup_state.get("ai_host"):
        return

    question = Msg.content_join(msg.content).strip()
    if not question:
        return

    # 调用 LLM 判断
    history = _ai_history_cache.get(state_key, [])
    session_id = soup_state.get("ai_session_id")
    if not session_id:
        session_id = uuid.uuid4().hex
        soup_state["ai_session_id"] = session_id
        await data.soup_state_set(state_key, soup_state)
    result = await llm_judge_question(
        soup_state["surface"],
        soup_state["bottom"],
        question,
        history,
        session_id,
    )

    answer = result["content"]

    # 记录对话历史
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    if len(history) > _MAX_HISTORY_ROUNDS * 2:
        history = history[-_MAX_HISTORY_ROUNDS * 2:]
    _ai_history_cache[state_key] = history

    # 如果玩家答对了，自动结束 AI 模式
    if result["type"] == "win":
        await _soup_ai_cleanup(state_key, soup_state.get("ai_session_id"))
        soup_state["ai_host"] = False
        await data.soup_state_set(state_key, soup_state)

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=f"[回复:{msg.seq}]{answer}",
        user=msg.user,
        group=msg.group,
    )
    return answer


@monitor_adapter("/海龟汤AI_结束")
async def soup_ai_end(msg: Msg):
    """结束 AI 主持人模式"""
    state_key = _state_key(msg)

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
    _ai_history_cache.pop(state_key, None)
    await llm_end_session(session_id)


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
