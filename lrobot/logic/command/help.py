"""帮助与转发"""

import re
from datetime import datetime

from logic import data
from message.handler.msg import Msg
from config import config, path, temp_key, monitor_adapter

txt_path = path / "storage/file/command/help.txt"
command_groups = ["帮助", "基础", "入会", "收集表", "工具", "游戏", "密码", "订阅", "活动"]

def help_txt_load():
    """读取 help.txt 并转换为字典"""
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    blocks = [b.strip() for b in content.split("#") if b.strip()]
    docs = {}

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        func_name = lines[0]
        item = {"用法": []}
        for line in lines[1:]:
            line = line.replace("\\n", "\n")
            if line.startswith("用法:"):
                u_e = line[len("用法:"):].strip()
                item["用法"].append(u_e)
            elif ":" in line:
                key, val = line.split(":", 1)
                item[key.strip()] = val.strip()
            else:
                item.setdefault("lines", []).append(line.strip())
        docs[func_name] = item
    return docs


def docs_merge(mode="wiki", platform=None, func_text=None, filter_set=None):
    """将 command.yml 与 help.txt 信息合并"""
    docs = help_txt_load()
    wiki_text, help_member, help_manager = {}, [], []
    for func_name, base in docs.items():
        cmd = next((c for c in config["commands"] if c["function"] == func_name), None)

        group_set = base.get("分组", cmd["set"] if cmd else None)
        if mode not in ("help", "help_find") and group_set != filter_set:
            continue

        attention = base.get('注意', '')
        test = base.get('测试', '')
        order = base.get('优先级', cmd["order"] if cmd else None)
        platforms = base.get("平台", cmd["platforms"] if cmd else [])
        status = base.get("状态", ",".join(cmd["state"]) if cmd else None)
        manager_text = base.get("管理", '是' if cmd and cmd["users"] else '否')
        is_manager = manager_text == "是"

        if mode == "wiki":
            title_parts = [usage for usage in base.get("用法", [])]
            other_lines = []
            if platforms:
                other_lines.append(f"平台: {','.join(platforms)}")
            if order:
                other_lines.append(f"优先级: {order}")
            if status:
                other_lines.append(f"状态: {status}")
            if attention:
                other_lines.append(f"注意: {attention}")
            if test:
                other_lines.append(f"测试: {test}")
            other_lines.extend(base.get("lines", []))  # 无标题行
            wiki_text[func_name] = {
                "title": "\n".join(title_parts),  # 用法作为title
                "lines": other_lines  # 其他信息行
            }
        if platform not in platforms:
            continue
        for usage in base["用法"]:
            if mode == "help":
                if "[" not in usage and "]" not in usage:
                    usage = usage.split(":", 1)[0]
                    if is_manager:
                        help_manager.append(usage)
                    else:
                        help_member.append(usage)
            elif mode == "help_find":
                if "[" not in usage and "]" not in usage:
                    usages = usage.split(":", 1)
                    if func_text.lstrip("/") == usages[0].lstrip("/"):
                        return usages[1]
            else:  # help_pro
                if "[" in usage and "]" in usage:
                    if is_manager:
                        help_manager.append(usage)
                    else:
                        help_member.append(usage)

    if mode == "wiki":
        return wiki_text
    elif mode == "help_find":
        return "容我禀告，阁下所指的指令，目前还未收录在我的档案库中。您不妨通过 /帮助 指令，重新查阅可用的指令列表。"
    else:
        return help_member, help_manager


def caesar_encrypt(text, shift):
    """凯撒加密"""
    encrypted = []
    for char in text:
        if char.isalpha():  # 只对字母进行加密
            start = ord("A") if char.isupper() else ord("a")
            encrypted.append(chr(start + (ord(char) - start + shift) % 26))
        else:
            encrypted.append(char)  # 其他字符不变
    return "".join(encrypted)


@monitor_adapter("/帮助_帮助")
async def help_help(msg: Msg):
    """帮助说明"""
    help_content = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    isCab = False
    if msg.group:
        isCab = True
    else:
        user_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" in user_list:
            isCab = True
    if len(help_content) == 2:
        help_content = help_content[1]

        if help_content == "帮助":
            current_hour = datetime.now().hour
            # 使用当前小时数作为偏移量加密文本
            bonus_scene = caesar_encrypt("bonus scene", current_hour)
            content = (
                "阁下若有任何疑问或高见，谨此邀请您将其记录在日志之中\n"
                "您只需使用'/留言[内容]'即可\n\n"
                f"此外，为您献上：zeroth {bonus_scene}"
            )
        else:
            content = docs_merge(mode="help_find", platform=msg.platform, func_text=help_content)

    else:
        cab_web = f"内阁页：https://whumystery.cn/{'cab' if msg.platform == 'LR232' else temp_key['uuid']}\n"
        member_text, cab_text = docs_merge(mode="help", platform=msg.platform)
        cab_text = f"以下每个均为可用的管理指令\n{','.join(cab_text)}\n" if isCab and cab_text else ""
        platforms = {
            "LR232": "QQ，群管理下方添加\n",
            "LR5921": "QQ，群管理中添加（3502644244）\n",
            "BILI": "B站，武大推协\n",
            "WECHAT": "微信公众号，武大推协\n"
        }
        platform_text = "".join(
            f"{platform}：{desc}"
            for platform, desc in platforms.items()
            if platform != msg.platform
        )
        cab_prompt = f"\n在帮助和进阶中，下方用换行隔开的是管理指令，可以在私聊及公测群中使用"
        member_text = '\n'.join(member_text)
        content = (
            "我亲爱的搭档，这是我能为您提供的所有协助：\n"
            "私聊中使用'/指令'即可触发，如需引导，请使用'/帮助,指令'（如：/帮助,航海日记）\n"
            "<指令一览>\n"
            "以下每行为一个可用指令\n"
            f"{member_text}\n"
            f"{cab_text}"
            "<联络站>\n"
            f"{platform_text}"
            "网站：https://whumystery.cn/home\n"
            f"{cab_web if isCab and msg.group != config['public']['公测群'][0] else ''}"
            "<温馨提示>\n"
            "指令格式为 /指令，需要携带 /，如： /入会\n"
            "指令提示里有时会携带引号（如：输入'/常见问题'），需要忽略引号，只需要输入： /常见问题\n"
            "回答时，根据提示回答，如接收到常见问题列表后，回复 2\n"
            "'/进阶'可获取指令的便捷用法\n"
            "指令中的逗号中英文通用\n"
            "在LR232，输入'/'或点击机器人图标，均可唤出指令面板"
            f"{cab_prompt if isCab else ''}"
        )
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


@monitor_adapter("/帮助_进阶")
async def help_advance(msg: Msg):
    """帮助说明"""
    help_content = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    isCab = False
    if msg.group:
        isCab = True
    else:
        user_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" in user_list:
            isCab = True
    if len(help_content) == 2:
        help_content = help_content[1]

        if help_content in command_groups:
            member_text, cab_text = docs_merge(mode="help_pro", platform=msg.platform, filter_set=help_content)
            content = "\n".join(member_text) if member_text else "此分组暂无进阶指令"
            if isCab and cab_text:
                content = content + "\n\n" + "\n".join(cab_text)
        else:
            content = "阁下，指令未能识别——您可通过'/进阶'重新校准分组。"
    else:
        content = (
            "<进阶说明>\n"
            "阁下，关于指令系统，容我为您提供一个更为高效之道:\n"
            "常规的分步指令('/a',输入b,输入c)在批量处理时略显繁琐\n"
            "进阶指令采用'/a,b,c'一步实现的方法\n"
            "为此，您可直接使用'/进阶,[分组]'来获取完整指令集\n"
            f"分组列表如下：{','.join(command_groups)}\n"
            "列表将呈现'指令: 用法'格式，其中'[]'内即为需要您替换的核心参数"
        )
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


@monitor_adapter("/帮助_问题")
async def help_question(msg: Msg):
    "常见问题"
    question_file = path / "storage/file/command/question.txt"
    text = question_file.read_text(encoding="utf-8")
    qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", text, re.S)

    question = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(question) == 1:
        question_list = "\n".join([f"{i + 1}. {q.strip()}" for i, (q, a) in enumerate(qa_pairs)])
        content = (
                "尊敬的侦探阁下,您希望查阅哪个问题?\n"
                "请直接告知我对应的序号即可\n" + question_list
        )
        await data.status_add(msg.user, msg.platform, "常见问题")
    else:
        num = question[1].strip()
        try:
            idx = int(num) - 1
            if 0 <= idx < len(qa_pairs):
                q, a = qa_pairs[idx]
                content = f"问：{q.strip()}\n\n答：{a.strip()}"
            else:
                content = f"序号 {num} 并未收录在案\n请从 1 至 {len(qa_pairs)} 之间选择一个合适的数字"
        except ValueError:
            content = "格式似乎有误，阁下。正确的形式应为'/常见问题,1'这样的格式，烦请您再试一次。"
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


async def help_question_judge(msg: Msg):
    """常见问题序号判断"""
    question_file = path / "storage/file/command/question.txt"
    text = question_file.read_text(encoding="utf-8")
    qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", text, re.S)
    num = Msg.content_join(msg.content)
    try:
        idx = int(num) - 1
        if 0 <= idx < len(qa_pairs):
            return True
    except ValueError:
        pass
    return False


@monitor_adapter("/帮助_回答")
async def help_answer(msg: Msg):
    """常见问题回答"""
    question_file = path / "storage/file/command/question.txt"
    text = question_file.read_text(encoding="utf-8")
    qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", text, re.S)
    num = Msg.content_join(msg.content)
    idx = int(num) - 1
    q, a = qa_pairs[idx]
    content = f"问：{q.strip()}\n\n答：{a.strip()}"
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


@monitor_adapter("/帮助_欢迎")
async def help_welcome(msg: Msg):
    """欢迎内容"""
    current_hour = datetime.now().hour
    content = (
        f"亲爱的侦探同好，{'日安' if 5 <= current_hour < 19 else '谨致问候'}\n"
        "在下是您的助手小推，谨代表武汉大学逻辑推理协会欢迎您的到来\n"
        "协会的最新动态将于各社交平台呈现，诚邀您关注\n"
        "若您有意加入我们，请移步至QQ招新群：708346432\n"
        "成为会员后，更有诸多谜题游戏在活动群中静候您的光临\n"
        "最后，不妨一试'/帮助'指令（/，帮，助），或许能带来些许惊喜"
    )
    Msg(
        platform=msg.platform,
        kind=f"{msg.kind[:2]}添加发送",
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    return content
