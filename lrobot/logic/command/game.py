"""小游戏"""

import random
import pandas as pd
from pypinyin import pinyin, Style

from config import path
from message.handler.msg import Msg


async def game_list(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="当前游戏：成语接龙，输入'/成语，xxxx'以体验。",
        user=msg.user,
        group=msg.group,
    )


chengyu = pd.read_json(str(path / "storage/file/command/idiom.json"))
chengyu.head(2)

t = chengyu.pinyin.str.split()
chengyu["shoupin"] = t.str[0]
chengyu["weipin"] = t.str[-1]
chengyu = chengyu.set_index("word")[["shoupin", "weipin"]]


# 移除音调的函数
def remove_tone(pinyin_str):
    # 将带音调的拼音转换为无音调
    tone_map = {
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v',
        'ü': 'v'
    }
    result = ''
    for char in pinyin_str:
        result += tone_map.get(char, char)
    return result


async def game_chengyu(msg: Msg):
    """成语接龙"""
    # 获取输入成语的尾拼音
    last_char = Msg.content_join(msg.content)[-1]
    weipin = pinyin(last_char, style=Style.NORMAL)[0][0]

    # 查找所有首拼音匹配尾拼音的成语（排除自身）
    next_options = chengyu[(chengyu["shoupin"].apply(remove_tone) == weipin)]

    if next_options.empty:
        content = "无匹配成语"  # 如果没有匹配项，返回None
    else:
        # 随机选择一个成语
        next_idiom = random.choice(next_options.index.tolist())
        content = next_idiom
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
