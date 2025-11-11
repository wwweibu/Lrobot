"""密码"""

import re

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter


@monitor_adapter("/密码_1")
async def cipher_1(msg: Msg):
    """选择模式"""
    content = "阁下，请选择您要使用的密码：凯撒、维吉尼亚、摩斯、培根或频率分析。"
    await data.status_add(msg.user, msg.platform, "密码1")
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


@monitor_adapter("/密码_2")
async def cipher_2(msg: Msg):
    """设置密文"""
    mode = Msg.content_join(msg.content)
    await data.status_add(msg.user, msg.platform, "密码2", mode)
    content = "请提供您需要处理的密文。"
    if mode in ["凯撒", "维吉尼亚", "频率"]:
        content += "请注意，系统将只处理其中的英文字符。"
    elif mode == "摩斯":
        content += "请提供由英文句点('-')和点('.')组成的密文，以空格或换行分隔，解密后未知字符将返回'？'。若有原文需要加密，请输入'无'。"
    else:
        content += "请提供A和B数量为5的整数倍的密文，解密后未知字符将返回'？'。若有原文需要加密，请输入'无'。"
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


@monitor_adapter("/密码_3")
async def cipher_3(msg: Msg):
    """设置密钥"""
    text = Msg.content_join(msg.content)
    mode = await data.status_check(msg.user, msg.platform, "密码2")
    await data.status_add(msg.user, msg.platform, "密码3", f"{mode}|{text}")
    if mode == "凯撒":
        content = "请提供数字作为密钥；若需尝试所有可能结果，请输入'无'。"
    elif mode == "维吉尼亚":
        content = "请提供密钥，必须仅包含字母。"
    elif mode in ["摩斯", "培根"]:
        content = "若上一步已输入内容，请输入'无'；若需要加密，请输入原文，且确保上一步输入了'无'"
    else:
        content = "请提供仅包含大写字母的频率表，若输入'无'，则使用默认频率表'ETAOINSHRDLCUMWFGYPBVKJXQZ'"
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


@monitor_adapter("/密码_4")
async def cipher_4(msg: Msg):
    """处理结果"""
    key = Msg.content_join(msg.content)
    info = await data.status_check(msg.user, msg.platform, "密码3")
    mode, text = info.split("|", 1)
    if mode == "凯撒":
        if key == "无":
            results = []
            for shift in range(1, 26):
                decoded = "".join(
                    caesar_shift(ch, shift)
                    for ch in text
                )
                results.append(f"解密 {shift}: {decoded}")

            content = "\n".join(results)
            await data.status_delete(msg.user, msg.platform, "密码3")
        else:
            try:
                shift = int(key.strip())
            except ValueError:
                content = "请重新输入整数位移"
            else:
                decoded = "".join(
                    caesar_shift(ch, shift)
                    for ch in text
                )
                content = f"解密 {shift}: {decoded}"
                await data.status_delete(msg.user, msg.platform, "密码3")
    elif mode == "维吉尼亚":
        if not re.fullmatch(r"[A-Za-z]+", key):
            content = "密钥必须仅包含字母，请重新输入"
        else:
            encrypted = vigenere_transform(text, key, encrypt=True)
            decrypted = vigenere_transform(text, key, encrypt=False)

            content = (
                f"密钥: {key}\n\n"
                f"加密结果: {encrypted}\n\n"
                f"解密结果: {decrypted}"
            )
            await data.status_delete(msg.user, msg.platform, "密码3")
    elif mode == "摩斯":
        if text == "无":
            result = morse_encode(key)
            content = f"摩斯加密结果: {result}"
            await data.status_delete(msg.user, msg.platform, "密码3")
        else:
            result = morse_decode(text)
            content = f"摩斯解密结果: {result}"
            await data.status_delete(msg.user, msg.platform, "密码3")
    elif mode == "培根":
        if text == "无":
            result = bacon_encode(key)
            content = f"培根加密结果: {result}"
            await data.status_delete(msg.user, msg.platform, "密码3")
        else:
            result = bacon_decode(text)
            content = f"培根解密结果: {result}"
            await data.status_delete(msg.user, msg.platform, "密码3")
    else:
        if key == "无":
            freq_table = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
        # 只保留 A-Z
        freq_table = "".join(sorted(set([c for c in freq_table if c.isalpha()]),
                                    key=freq_table.index))
        if not freq_table:
            content = "请重新输入仅包含大写字母的频率表"
        else:
            result = frequency_decrypt(text, freq_table)
            content = f"频率分析解密结果: {result}"
            await data.status_delete(msg.user, msg.platform, "密码3")
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


@monitor_adapter("/密码_凯撒")
async def cipher_caesar(msg: Msg):
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
            content = "位移应为整数,请使用 /凯撒,abc , /凯撒,abc,3 类似格式"
        else:
            decoded = "".join(
                caesar_shift(ch, shift)
                for ch in text
            )
            content = f"解密 {shift}: {decoded}"
    else:
        content = "请使用: /凯撒,abc 或 /凯撒,abc,3 类似格式"

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
        k = ord(key[key_index % key_len]) - ord('A')
        if not encrypt:
            k = -k  # 解密时反向位移

        if 'A' <= ch <= 'Z':
            base = ord('A')
            result.append(chr((ord(ch) - base + k) % 26 + base))
            key_index += 1  # 移动密钥指针
        elif 'a' <= ch <= 'z':
            base = ord('a')
            result.append(chr((ord(ch) - base + k) % 26 + base))
            key_index += 1
        else:
            result.append(ch)

    return ''.join(result)


@monitor_adapter("/密码_维吉尼亚")
async def cipher_vigenere(msg: Msg):
    """维吉尼亚加密/解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)

    if len(parts) != 3:
        content = "格式错误,请使用 /维吉尼亚,abc,abcedf 的格式(密钥,密文)"
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

    result = []
    for p in parts:
        if p == '' or p == '/':  # 空或斜杠 -> 空格
            result.append(' ')
        elif p in reverse_dict:
            result.append(reverse_dict[p])
        else:
            result.append('?')  # 无法识别
    return ' / '.join(result).replace('  ', ' ')  # 合并多余空格


@monitor_adapter("/密码_摩斯_加密")
async def cipher_morse_encrypt(msg: Msg):
    """摩斯密码加密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用 /摩斯加密,ab 类似格式\n\n{table}"
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


@monitor_adapter("/密码_摩斯_解密")
async def cipher_morse_decrypt(msg: Msg):
    """摩斯密码解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(MORSE_CODE_DICT.items())
        )
        content = f"请使用 /摩斯解密,-.- 类似格式，请提供由英文句点('-')和点('.')组成的原文，以空格或换行分隔\n\n{table}"
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
        else:
            result.append('?')
    return " / ".join(result) if result else "无可加密字母"


def bacon_decode(code):
    """培根解密"""
    filtered = re.sub(r"[^ABab]", "", code.upper())
    if len(filtered) % 5 != 0:
        return "密文长度不是5的倍数，无法解密"

    result = []
    for i in range(0, len(filtered), 5):
        group = filtered[i:i + 5]
        result.append(REVERSE_BACON_FULL.get(group, '?'))
    return ' / '.join(result)


@monitor_adapter("/密码_培根_加密")
async def cipher_bacon_encrypt(msg: Msg):
    """培根密码加密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(BACON_FULL.items())
        )
        content = f"请使用 /培根加密,ab \n\n{table}"
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


@monitor_adapter("/密码_培根_解密")
async def cipher_bacon_decrypt(msg: Msg):
    """培根密码解密"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)

    if len(parts) != 2:
        table = "\n".join(
            f"{k} → {v}" for k, v in sorted(BACON_FULL.items())
        )
        content = f"请使用 /培根解密,AAAAABAAAA 类似格式\n\n{table}"
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
    filtered = [c for c in ciphertext.upper() if 'A' <= c <= 'Z']
    if not filtered:
        return "密文中无字母，无法进行频率分析"

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
    return f"{''.join(result)}\n\n推测映射: {mapping_str}"


@monitor_adapter("/密码_频率_解密")
async def cipher_freq_decrypt(msg: Msg):
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
        content = "格式错误，请使用 /频率解密,密文 或 /频率解密,频率表,密文 \n\n默认频率表:ETAOINSHRDLCUMWFGYPBVKJXQZ"
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
    content = f"频率分析解密结果: {result}"

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
