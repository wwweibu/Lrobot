"""工具"""

import re
import time
import jionlp as jio
from datetime import datetime

from logic import data
from message.handler.msg import Msg
from config import database_update, monitor_adapter, path, future


@monitor_adapter("/工具_设置待办")
async def tool_pending(msg: Msg):
    """设置待办"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "用户错误，必须为 LR5921 或者使用绑定了 LR5921 的平台"
    else:
        parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
        content = "格式错误，请使用'/待办，明天晚六点，吃饭'类似格式"
        if len(parts) == 3:
            try:
                pending_time = jio.parse_time(parts[1].strip(), time_base=time.time(), time_type="time_point")
                if pending_time["type"] == "time_point" or pending_time["type"] == "time_span":
                    pending_time = pending_time["time"][0]
                    target_time = datetime.strptime(pending_time, "%Y-%m-%d %H:%M:%S")
                    content = f"设置成功，将在 {pending_time} 提醒您 {parts[2].strip()}"
                    Msg(
                        platform=msg.platform,
                        event="发送",
                        kind=f"{msg.kind[:2]}发送",
                        seq=msg.seq,
                        content=content,
                        user=msg.user,
                        group=msg.group,
                    )
                    sql = "INSERT INTO system_remind (time, content, user) VALUES (%s, %s, %s)"
                    id = await database_update(sql, (target_time, parts[2].strip(), user))
                    await data.remind_send(id, target_time, parts[2].strip(), user)
                    return
                else:
                    content = "时间格式错误，请不要用7.1表示日期，用h、m、s表示时分秒"
            except Exception:
                content = "时间格式错误，请不要用7.1表示日期，用h、m、s表示时分秒"
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


def caesar_shift(ch, shift):
    """对单个字符执行凯撒解密"""
    if 'a' <= ch <= 'z':
        return chr((ord(ch) - ord('a') - shift) % 26 + ord('a'))
    elif 'A' <= ch <= 'Z':
        return chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
    else:
        return ch


@monitor_adapter("/工具_凯撒")
async def tool_caesar(msg: Msg):
    """凯撒加解密工具"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)

    if len(parts) == 2:
        text = parts[1].strip()
        results = []
        for shift in range(1, 26):
            decoded = "".join(
                caesar_shift(ch, shift)
                for ch in text
            )
            results.append(f"解密 {shift}: {decoded}")

        content = "\n".join(results)

    elif len(parts) == 3:
        text = parts[1].strip()
        try:
            shift = int(parts[2].strip())
        except ValueError:
            content = "位移应为整数,请使用'/凯撒,abc','/凯撒,abc,3'类似格式"
        else:
            decoded = "".join(
                caesar_shift(ch, shift)
                for ch in text
            )
            content = f"解密 {shift}: {decoded}"
    else:
        content = "请使用:'/凯撒,abc'或'/凯撒,abc,3'类似格式"

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


def vigenere_transform(text, key, encrypt=True):
    """维吉尼亚加/解密"""
    result = []
    key = key.upper()
    key_index = 0
    key_len = len(key)

    for ch in text:
        if ch.isalpha():
            k = ord(key[key_index % key_len]) - ord('A')
            if not encrypt:
                k = -k  # 解密时反向位移

            if 'A' <= ch <= 'Z':
                base = ord('A')
                result.append(chr((ord(ch) - base + k) % 26 + base))
            elif 'a' <= ch <= 'z':
                base = ord('a')
                result.append(chr((ord(ch) - base + k) % 26 + base))

            key_index += 1  # 移动密钥指针
        else:
            result.append(ch)  # 空格/标点保持原样

    return ''.join(result)


@monitor_adapter("/工具_维吉尼亚")
async def tool_vigenere(msg: Msg):
    """维吉尼亚加密/解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)

    if len(parts) != 3:
        content = "格式错误,请使用'/维吉尼亚,abc,abcedf'(密钥,密文)"
    else:
        key = parts[1].strip()
        text = parts[2].strip()

        if not re.fullmatch(r"[A-Za-z]+", key):
            content = "密钥必须仅包含字母"
        else:
            encrypted = vigenere_transform(text, key, encrypt=True)
            decrypted = vigenere_transform(text, key, encrypt=False)

            content = (
                f"密钥: {key}\n\n"
                f"加密结果: {encrypted}\n\n"
                f"解密结果: {decrypted}"
            )

    # 返回消息
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


# 摩斯码映射表
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.'}


def morse_encode(text):
    """摩斯加密"""
    result = []
    for ch in text.upper():
        if ch in MORSE_CODE_DICT:
            result.append(MORSE_CODE_DICT[ch])
        else:
            result.append('?')  # 未知字符
    return " / ".join(result)


def morse_decode(code):
    """摩斯解密"""
    reverse_dict = {v: k for k, v in MORSE_CODE_DICT.items()}

    # 以空格或换行分割单个符号
    parts = re.split(r"[\s\n]+", code.strip())
    print("parts:", parts)

    result = []
    for p in parts:
        if p == '' or p == '/':  # 空或斜杠 -> 空格
            result.append(' ')
        elif p in reverse_dict:
            result.append(reverse_dict[p])
        else:
            result.append('?')  # 无法识别
    return ' / '.join(result).replace('  ', ' ')  # 合并多余空格


@monitor_adapter("/工具_摩斯加密")
async def tool_morse_encrypt(msg: Msg):
    """摩斯密码加密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用'/摩斯加密,ab'类似格式\n\n{table}"
    else:
        text = parts[1].strip()

        result = morse_encode(text)
        content = f"摩斯加密结果: {result}"
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


@monitor_adapter("/工具_摩斯解密")
async def tool_morse_decrypt(msg: Msg):
    """摩斯密码解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用'/摩斯解密,-.-'类似格式，注意是英文句号\n\n{table}"
    else:
        text = parts[1].strip()

        result = morse_decode(text)
        content = f"摩斯解密结果: {result}"
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


# 培根密码表
BACON_FULL = {
    'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
    'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAB',
    'K': 'ABABA', 'L': 'ABABB', 'M': 'ABBAA', 'N': 'ABBAB', 'O': 'ABBBA',
    'P': 'ABBBB', 'Q': 'BAAAA', 'R': 'BAAAB', 'S': 'BAABA', 'T': 'BAABB',
    'U': 'BABAA', 'V': 'BABAB', 'W': 'BABBA', 'X': 'BABBB', 'Y': 'BBAAA',
    'Z': 'BBAAB'
}

REVERSE_BACON_FULL = {v: k for k, v in BACON_FULL.items()}


def bacon_encode(text):
    """培根加密"""
    result = []
    for ch in text.upper():
        if ch in BACON_FULL:
            result.append(BACON_FULL[ch])
    return " / ".join(result) if result else "无可加密字母"


def bacon_decode(code):
    """培根解密"""
    filtered = re.sub(r"[^ABab]", "", code.upper())
    if len(filtered) % 5 != 0:
        return "错误：密文长度不是5的倍数，无法解密"

    result = []
    for i in range(0, len(filtered), 5):
        group = filtered[i:i + 5]
        result.append(REVERSE_BACON_FULL.get(group, '?'))
    return ''.join(result)


@monitor_adapter("/工具_培根加密")
async def tool_bacon_encrypt(msg: Msg):
    """培根密码加密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用'/培根加密,ab'\n\n{table}"
    else:
        text = parts[1].strip()

        result = bacon_encode(text)
        content = f"培根加密结果: {result}"

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


@monitor_adapter("/工具_培根解密")
async def tool_bacon_decrypt(msg: Msg):
    """培根密码解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用'/培根解密,AAAAABAAAA'\n\n{table}"
    else:
        text = parts[1].strip()

        result = bacon_decode(text)
        content = f"培根解密结果: {result}"

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


def frequency_decrypt(ciphertext, freq_table):
    """基于频率分析的单表替换解密"""
    filtered = [c for c in ciphertext.upper() if c.isalpha()]
    if not filtered:
        return "密文中无字母，无法分析"

    # 统计频率
    counts = {}
    for ch in filtered:
        counts[ch] = counts.get(ch, 0) + 1

    sorted_chars = sorted(counts, key=lambda x: counts[x], reverse=True)

    # 建立映射
    mapping = {}
    for i, ch in enumerate(sorted_chars):
        if i < len(freq_table):
            mapping[ch] = freq_table[i]
        else:
            mapping[ch] = '?'

    # 替换
    result = []
    for c in ciphertext.upper():
        if c in mapping:
            result.append(mapping[c])
        else:
            result.append(c)

    mapping_str = ", ".join([f"{k}->{v}" for k, v in mapping.items()])
    return f"{''.join(result)}\n\n推测映射：{mapping_str}"


@monitor_adapter("/工具_频率解密")
async def tool_freq_decrypt(msg: Msg):
    """单表替换密码频率分析解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)

    # 模式判断
    if len(parts) == 2:
        freq_table = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
        ciphertext = parts[1].strip()
    elif len(parts) == 3:
        freq_table = parts[1].strip().upper()
        ciphertext = parts[2].strip()
        # 只保留 A-Z
        freq_table = "".join(sorted(set([c for c in freq_table if c.isalpha()]),
                                    key=freq_table.index))
        if not freq_table:
            freq_table = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    else:
        content = "格式错误，请使用：\n/频率解密,密文\n或\n/频率解密,频率表,密文"
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

    # 调用解密逻辑
    result = frequency_decrypt(ciphertext, freq_table)
    content = f"频率分析解密结果：\n{result}"

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


@monitor_adapter("/工具_直播开启")
async def tool_live_start(msg: Msg):
    """B 站开启直播"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 2:
        msg1 = Msg(
            platform="BILI",
            event="发送",
            kind=f"私聊直播开启",
        )
        addr, code = await future.wait(msg1.num, "[消息]直播推流获取超时")

        await data.status_add(msg.user, msg.platform, "直播", parts[1])
        content = f"推流地址:{addr}\n推流码:{code}\n如需更改直播间封面则直接发送图片,无需更改则回复'否'"
    else:
        content = "格式错误，请使用'/直播,读书会'类似格式"
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


@monitor_adapter("/工具_直播设置")
async def tool_live_set(msg: Msg):
    """B 站设置直播"""
    title = await data.status_check(msg.user, msg.platform, "直播")
    if msg.content[0].get("type") == "text":
        content = title
    else:
        file_path = path / f"storage/file/user/{msg.user}/{msg.content[0]['data']['file']}"
        file_url = msg.content[0]['data'].get('url')
        if file_url:
            await data.file_download(file_path, msg.content[0]['data']['url'])
        else:
            msg.content[0]['data']['file_path'] = str(file_path)
            msg1 = Msg(
                platform="LR5921",
                event="发送",
                kind="文件下载",
                content=msg.content
            )
            await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
        content = f"{title}|{file_path}"
    msg1 = Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播标题",
        content=content
    )

    await future.wait(msg1.num, "[消息]直播标题设置超时")

    await data.status_delete(msg.user, msg.platform, "直播")
    content = "设置成功"
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


@monitor_adapter("/工具_直播关闭")
async def tool_live_close(msg: Msg):
    """B 站关闭直播"""
    Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播关闭",
    )
    content = "关闭成功"
    await data.status_delete(msg.user, msg.platform, "直播")
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


@monitor_adapter("/工具_直播公告")
async def tool_live_notice(msg: Msg):
    """B 站设置直播公告"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 2:
        Msg(
            platform="BILI",
            event="发送",
            kind=f"私聊直播公告",
            content=parts[1].strip()
        )
        content = "设置成功"
    else:
        content = "格式错误，请使用'/直播公告,今晚抽取一本《夜行》'类似格式"
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


@monitor_adapter("/工具_wiki上传")
async def tool_wiki_1(msg: Msg):
    """wiki 上传图片"""
    await data.status_add(msg.user, msg.platform, "wiki")
    content = "请上传图片"
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


@monitor_adapter("/工具_wiki链接")
async def tool_wiki_2(msg: Msg):
    """wiki 生成链接"""
    wiki_dir = path / "storage/file/resource/wiki"
    existing_numbers = []
    for file in wiki_dir.glob("*.png"):
        if file.stem.isdigit():  # 检查文件名是否为纯数字
            existing_numbers.append(int(file.stem))
    next_number = max(existing_numbers, default=0) + 1
    file_path = wiki_dir / f"{next_number}.png"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, msg.content[0]['data']['url'])
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        msg1 = Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
        await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
    content = f"https://whumystery.cn/hjd/static/wiki/{next_number}.png"
    await data.status_delete(msg.user, msg.platform, "wiki")
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
