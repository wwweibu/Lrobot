"""小游戏"""

import re
import random
import pandas as pd
from pypinyin import pinyin, Style

from logic import data
from config import path
from message.handler.msg import Msg

async def game_list(msg: Msg):
    """游戏列表"""
    content = ("当前游戏:\n"
               "成语接龙:\n"
               "/成语,[成语]:进行同音接龙\n"
               "/成语,[成语],[数字]:进行任意个数的同音接龙(除qq外数字不宜过大)\n"
               "/成语,[成语],严格:进行同字接龙\n"
               "/成语,[成语],知识:返回对应释义\n"
               "/成语接龙:开始成语接龙(后续输入任意词开始接龙，仅限私聊)\n"
               "/成语接龙严格:开始成语同字接龙\n"
               "/成语接龙结束:结束成语接龙状态\n\n"
               "真心话大冒险:\n"
               "/真心话:随机真心话\n"
               "/大冒险:随机大冒险\n")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


def idiom_prepare():
    """成语预处理"""
    idom_full = pd.read_json(str(path / "storage/file/command/idiom.json"))
    t = idom_full.pinyin.str.split()
    idom_full["first"] = t.str[0]
    idom_full["last"] = t.str[-1]
    idom_index = idom_full.set_index("word")[["first", "last"]].copy()
    idom_index["first_norm"] = idom_index["first"].map(remove_tone)
    return idom_full, idom_index

def remove_tone(pinyin_str):
    """移除音调"""
    tone_map = {
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v',
        'ü': 'v'
    }
    return ''.join(tone_map.get(c, c) for c in pinyin_str)


async def game_idiom_start(msg: Msg):
    """成语接龙开始"""
    await data.status_add(msg.user, "成语", "同音")
    content = "现在你可以输入任意内容，系统将自动进行接龙。输入'/成语接龙结束'退出此状态"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def game_idiom_word_start(msg: Msg):
    """成语同字接龙开始"""
    await data.status_add(msg.user, "成语", "同字")
    content = "现在你可以输入任意内容，系统将自动进行接龙。输入'/成语接龙结束'退出此状态"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def game_idiom_end(msg: Msg):
    """成语接龙退出"""
    await data.status_delete(msg.user, "成语")
    content = "退出成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def game_idiom_chain(msg: Msg):
    """成语接龙"""
    status = await data.status_check(msg.user, "成语")
    idiom = Msg.content_join(msg.content)
    if status == "同字":
        options = [option for option in idiom_index.index if option[0] == idiom[-1] and option != idiom]
        content = random.choice(options) if options else "无匹配成语"
    else:
        last_char = idiom[-1]
        last_pinyin = pinyin(last_char, style=Style.NORMAL)[0][0]
        options = idiom_index[idiom_index["first_norm"] == last_pinyin].index.tolist()
        options = [option for option in options if option != idiom]
        content = random.choice(options) if options else "无匹配成语"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def game_idiom(msg: Msg):
    """成语"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        mod = parts[2]
        idiom = parts[1]
        if mod == "知识":
            row = idiom_full[idiom_full["word"] == idiom]
            if row.empty:
                content = "未找到该成语"
            else:
                r = row.iloc[0]
                content = (
                    f"成语：{r['word']}\n"
                    f"出自：{r.get('derivation', '无')}\n"
                    f"示例：{r.get('example', '无')}\n"
                    f"解释：{r.get('explanation', '无')}"
                )
        elif mod == "严格":
            options = [option for option in idiom_index.index if option[0] == idiom[-1] and option != idiom]
            content = random.choice(options) if options else "无匹配成语"
        else:
            try:
                id = int(mod)
                used = set()
                chain = []
                current_last_char = idiom[-1]
                for _ in range(id):
                    last_pinyin = pinyin(current_last_char, style=Style.NORMAL)[0][0]
                    options = idiom_index[idiom_index["first_norm"] == last_pinyin].index.tolist()
                    options = [option for option in options if option not in used and option != idiom]
                    if not options:
                        break
                    next_idiom = random.choice(options)
                    chain.append(next_idiom)
                    used.add(next_idiom)
                    current_last_char = next_idiom[-1]
                content = ",".join(chain) if chain else "无匹配成语"
            except ValueError:
                content = "指令格式错误"
    elif len(parts) == 2:
        idiom = parts[1]
        last_char = idiom[-1]
        last_pinyin = pinyin(last_char, style=Style.NORMAL)[0][0]
        options = idiom_index[idiom_index["first_norm"] == last_pinyin].index.tolist()
        options = [option for option in options if option != idiom]
        content = random.choice(options) if options else "无匹配成语"
    else:
        content = "格式错误"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


def truth_prepare():
    """真心话大冒险预处理"""
    with open(path / "storage/file/command/truth.txt", "r", encoding="utf-8") as f:
        truths = [line.strip() for line in f if line.strip()]
    with open(path / "storage/file/command/dare.txt", "r", encoding="utf-8") as f:
        dares = [line.strip() for line in f if line.strip()]

    return truths, dares


async def game_truth(msg: Msg):
    """随机真心话"""
    question = random.choice(truth)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=question,
        user=msg.user,
        group=msg.group,
    )


async def game_dare(msg: Msg):
    """随机大冒险"""
    question = random.choice(dare)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=question,
        user=msg.user,
        group=msg.group,
    )


idiom_full, idiom_index = idiom_prepare()
truth, dare = truth_prepare()
