"""小游戏"""

import re
import random
import pandas as pd
from pypinyin import pinyin, Style

from logic import data
from message.handler.msg import Msg
from config import path, monitor_adapter


def idiom_prepare():
    """成语预处理"""
    idom_full = pd.read_json(str(path / "storage/file/command/idiom.json"))
    new_idiom = {
        "derivation": "夏洛克·福尔摩斯，英国作家阿瑟·柯南·道尔所著长篇推理小说《福尔摩斯探案集》中的人物，外貌特征参考插画师沃尔特·帕吉特的创作。该人物首次登场于《血字的研究》，常居伦敦贝克街221号B公寓，凭借敏锐观察与演绎推理法破解案件，搭档约翰·H·华生以第一人称记录其多数探案经历",
        "example": "福尔摩斯——他的知识程度(1)文学知识——无(2)哲学知识——无(3)天文学知识——无(4)政治知识——弱(5)植物学知识——不定，对莨菪、鸦片及一般毒物知识丰富，对实用园艺植物一无所知(6)地质学知识——实用，但有限，可以在一瞥之下就识别不同的泥土(7)化学知识——深厚(8)解剖学知识——正确，但无系统(9)罪案记载——极渊博，他似乎知道本世纪每一个可怕刑案的细节(10)小提琴拉得很好(11)精于棍棒、拳击及剑术(12)对英国法律有很好的实用知识",
        "explanation": "Once you eliminate the impossible, whatever remains, no matter how improbable, must be the truth.",
        "pinyin": "fú ěr mó sī", "word": "福尔摩斯", "abbreviation": "fems"}
    idom_full = pd.concat([idom_full, pd.DataFrame([new_idiom])], ignore_index=True)
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


@monitor_adapter("/游戏_成语")
async def game_idiom(msg: Msg):
    """成语"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        mod = parts[2].strip()
        idiom = parts[1].strip()
        if mod == "知识":
            row = idiom_full[idiom_full["word"] == idiom]
            if row.empty:
                content = "阁下，您所查询的成语未收录在我的辞海之中，或许它使用了某种精妙的伪装？"
            else:
                r = row.iloc[0]
                content = (
                    f"成语：{r['word']}\n"
                    f"出自：{r.get('derivation', '无')}\n"
                    f"示例：{r.get('example', '无')}\n"
                    f"解释：{r.get('explanation', '无')}"
                )
        elif mod == "同字":
            options = [option for option in idiom_index.index if option[0] == idiom[-1] and option != idiom]
            content = random.choice(options) if options else "经过一番侦察，未能发现与之匹配的成语。"
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
                        chain.append("无匹配")
                        break
                    next_idiom = random.choice(options)
                    chain.append(next_idiom)
                    used.add(next_idiom)
                    current_last_char = next_idiom[-1]
                content = ",".join(chain) if chain else "经过一番侦察，未能发现与之匹配的成语。"
            except ValueError:
                content = "指令格式似乎有些蹊跷，阁下。正确的形式应为'/成语,愚公移山,10'这样的格式。"
    elif len(parts) == 2:
        idiom = parts[1].strip()
        last_char = idiom[-1]
        last_pinyin = pinyin(last_char, style=Style.NORMAL)[0][0]
        options = idiom_index[idiom_index["first_norm"] == last_pinyin].index.tolist()
        options = [option for option in options if option != idiom]
        content = random.choice(options) if options else "经过一番侦察，未能发现与之匹配的成语。"
    else:
        content = "请输入成语"
        await data.status_add(msg.user, msg.platform, "成语1")
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


@monitor_adapter("/游戏_成语_成语")
async def game_idiom_1(msg: Msg):
    """成语接龙输入成语"""
    idiom = Msg.content_join(msg.content).strip()
    await data.status_delete(msg.user, msg.platform, "成语1")
    await data.status_add(msg.user, msg.platform, "成语2", idiom)
    content = "请选择模式，输入'同字'代表同字接龙，'同音'代表同音接龙，'严格'代表获取成语的释义，任意数字代表进行连续的同音接龙"
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


async def game_idiom_2_judge(msg: Msg):
    """成语接龙模式判断"""
    content = Msg.content_join(msg.content)
    if content in ["同字", "同音", "知识"]:
        return True
    try:
        id = int(content)
        return 1 <= id <= 100
    except ValueError:
        return False


@monitor_adapter("/游戏_成语_模式")
async def game_idiom_2(msg: Msg):
    """成语接龙模式选择"""
    mod = Msg.content_join(msg.content)
    idiom = await data.status_check(msg.user, msg.platform, "成语2")
    if mod == "知识":
        row = idiom_full[idiom_full["word"] == idiom]
        if row.empty:
            content = "阁下，您所查询的成语未收录在我的辞海之中，或许它使用了某种精妙的伪装？"
        else:
            r = row.iloc[0]
            content = (
                f"成语：{r['word']}\n"
                f"出自：{r.get('derivation', '无')}\n"
                f"示例：{r.get('example', '无')}\n"
                f"解释：{r.get('explanation', '无')}"
            )
    elif mod == "同字":
        options = [option for option in idiom_index.index if option[0] == idiom[-1] and option != idiom]
        content = random.choice(options) if options else "经过一番侦察，未能发现与之匹配的成语。"
    elif mod == "同音":
        last_char = idiom[-1]
        last_pinyin = pinyin(last_char, style=Style.NORMAL)[0][0]
        options = idiom_index[idiom_index["first_norm"] == last_pinyin].index.tolist()
        options = [option for option in options if option != idiom]
        content = random.choice(options) if options else "经过一番侦察，未能发现与之匹配的成语。"
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
                    chain.append("无匹配")
                    break
                next_idiom = random.choice(options)
                chain.append(next_idiom)
                used.add(next_idiom)
                current_last_char = next_idiom[-1]
            content = ",".join(chain) if chain else "经过一番侦察，未能发现与之匹配的成语。"
        except ValueError:
            content = "指令格式似乎有些蹊跷，阁下。请从'/成语'开始，重新尝试一次。"
    await data.status_delete(msg.user, msg.platform, "成语2")
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


@monitor_adapter("/游戏_成语_接龙开始")
async def game_idiom_start(msg: Msg):
    """成语接龙开始"""
    if "严格" in Msg.content_join(msg.content):
        info = "同字"
    else:
        info = "同音"
    await data.status_add(msg.user, msg.platform, "成语接龙", info)
    content = ("接龙游戏现已开始，阁下。\n"
               f"请您随意出题，我将依据{info}模式进行接龙。\n"
               "若要结束这场文字游戏，请使用'/成语接龙退出'指令")
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


@monitor_adapter("/游戏_成语_接龙")
async def game_idiom_chain(msg: Msg):
    """成语接龙"""
    info = await data.status_check(msg.user, msg.platform, "成语接龙")
    idiom = Msg.content_join(msg.content)
    if info == "同字":
        options = [option for option in idiom_index.index if option[0] == idiom[-1] and option != idiom]
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
    return content


@monitor_adapter("/游戏_成语_接龙退出")
async def game_idiom_end(msg: Msg):
    """成语接龙退出"""
    await data.status_delete(msg.user, msg.platform, "成语接龙")
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
    return content

def truth_prepare():
    """真心话大冒险预处理"""
    with open(path / "storage/file/command/truth.txt", "r", encoding="utf-8") as f:
        truths = [line.strip() for line in f if line.strip()]
    with open(path / "storage/file/command/dare.txt", "r", encoding="utf-8") as f:
        dares = [line.strip() for line in f if line.strip()]

    return truths, dares


@monitor_adapter("/游戏_真心话")
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
    return question


@monitor_adapter("/游戏_大冒险")
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
    return question


idiom_full, idiom_index = idiom_prepare()
truth, dare = truth_prepare()
