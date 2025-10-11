"""帮助与转发"""

import re
import datetime

from logic import data
from message.handler.msg import Msg
from config import config, path, temp_key, monitor_adapter

txt_path = path / "storage/file/command/help.txt"


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
            if line.startswith("用法:"):
                u_e = line[len("用法:"):].strip().replace("\\n", "\n")
                item["用法"].append(u_e)
            elif ":" in line:
                key, val = line.split(":", 1)
                item[key.strip()] = val.strip().replace("\\n", "\n")
            else:
                item.setdefault("lines", []).append(line.replace("\\n", "\n"))
        docs[func_name] = item
    return docs


def platform_short(platforms):
    """平台缩写转换"""
    s = set(platforms)
    short = set()
    if "LR232" in s and "LR5921" in s:
        short.add("LR")
    else:
        if "LR232" in s:
            short.add("232")
        if "LR5921" in s:
            short.add("5921")
    if "WECHAT" in s:
        short.add("W")
    if "BILI" in s:
        short.add("B")
    # 若四个平台都有，则简写为“全”
    if len(short) >= 3 and "LR" in short:
        return "全"
    return ",".join(sorted(short))


def users_short(users, kinds):
    """用户转换"""
    if not users and "私聊接收" in kinds:
        return "私"
    return ",".join(users)


def groups_short(groups):
    """群聊简称转换"""
    if {"公测群", "水群", "内阁"}.issubset(groups):
        return "群"
    filtered = [g for g in groups if g != "内测群"]
    short = ["公测" if g == "公测群" else g for g in filtered]
    return ",".join(sorted(short))


def docs_merge(filter_set, help_mode=True):
    """将 command.yml 与 help.txt 信息合并"""
    docs = help_txt_load()
    text1, text2, text3 = {}, [], []
    for func_name, base in docs.items():
        if func_name == "check_restart" and not config["SERVER_IP"]:
            continue  # 非容器环境跳过此命令
        cmd = next((c for c in config["commands"] if c["function"] == func_name), None)

        group_set = base.get("分组", cmd["set"] if cmd else None)
        if group_set != filter_set:
            continue
        attention = base.get('注意', '')
        test = base.get('测试', '')
        order = base.get('优先级', cmd["order"] if cmd else None)
        platforms = base.get("平台", platform_short(cmd["platforms"]) if cmd else None)
        status = base.get("状态", ",".join(cmd["state"]) if cmd else None)
        users = base.get("用户", users_short(cmd["users"], cmd["kind"]) if cmd else None)
        groups = base.get("群聊", groups_short(cmd["groups"]) if cmd else None)
        manager = base.get("管理", '是' if cmd and cmd["users"] else '否')

        if not help_mode:
            title_parts = []
            for usage in base["用法"]:
                title_parts.append(usage)
            other_lines = []
            p_line = ""
            if platforms:
                p_line += f"平台: {platforms};"
            if users:
                p_line += f"用户: {users};"
            if groups:
                p_line += f"群聊: {groups};"
            if p_line:
                other_lines.append(p_line)
            if order:
                other_lines.append(f"优先级: {order}")
            if status:
                other_lines.append(f"状态: {status}")
            if attention:
                other_lines.append(f"注意: {attention}")
            if test:
                other_lines.append(f"测试: {test}")
            other_lines.extend(base.get("lines", []))  # 无标题行
            text1[func_name] = {
                "title": "\n".join(title_parts),  # 用法作为title
                "lines": other_lines  # 其他信息行
            }

            continue  # 跳过下面赋值

        for ue in base["用法"]:
            if manager == "是":
                t2 = ue
                t2 += f" ({platforms})"
                if users:
                    t2 += f"({users})"
                if groups:
                    t2 += f"({groups})"
                text2.append(t2)
            else:
                label_kinds = []
                if users:
                    label_kinds.append("私")
                if groups:
                    label_kinds.append("群")
                label = f"({platforms})" + "".join(f"({k})" for k in label_kinds)
                t3 = f"{ue} {label}"
                text3.append(t3)

    if help_mode:
        return text2, text3
    else:
        return text1


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


@monitor_adapter("/基础_帮助")
async def help_show(msg: Msg):
    """帮助说明"""
    help_content = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    isCab = False
    if msg.group:
        if any(msg.group in group_list for group_list in
               [config["public"]["公测群"], config["public"]["内测群"], config["public"]["内阁"]]):
            isCab = True
    else:
        user_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" in user_list:
            isCab = True
    if len(help_content) == 2:
        help_content = help_content[1]

        if help_content == "帮助":
            current_hour = datetime.datetime.now().hour
            # 使用当前小时数作为偏移量加密文本
            bonus_scene = caesar_encrypt("bonus scene", current_hour)
            content = (
                "有任何问题或建议可进行留言\n"
                "输入'/留言xxx'\n\n"
                f"Here is the zeroth {bonus_scene}"
            )
        elif help_content in ["基础", "入会", "收集表", "游戏", "工具", "订阅", "活动", "系统"]:
            text2, text3 = docs_merge(help_content)
            content = "\n".join(text3)
            if isCab and text2:
                text2 = '\n'.join(text2)
                content += f"\n\n{text2}"
        else:
            content = f"请输入'/帮助,基础'类似格式(系统，入会，收集表，游戏，工具，订阅，活动)"
    else:
        cab_web = f"\n内阁页: https://whumystery.cn/{'cab' if msg.platform == 'LR232' else temp_key['uuid']}"
        cab_prompt = '下方为管理指令,括号中分别是平台、私聊、群聊的可用范围\n' if isCab else ''
        content = (
            "<指令列表>\n"
            "输入'/帮助,基础'等获取指令组详细指令\n"
            f"指令组包括基础、入会、收集表、游戏、工具、订阅、活动、系统\n"
            "你将看到:'/常见问题,[序号]: 获取对应问题回答 (全)(私)(群)'类似的回答\n"
            "其中[]里的内容需要替换,例如,此指令为'/常见问题,1'\n"
            "冒号后面的为解释\n"
            "第一个括号是平台,全代表四个平台,LR代表两个QQ,232代表LR232,5921代表LR5921,W代表微信,B代表B站\n"
            "括号存在'私'则私聊可用；存在'群'则群聊可用\n"
            f"{cab_prompt}"
            "<其他>\n"
            "任何指令中英文逗号均通用\n"
            "LR232可输入'/'或点击机器人图标唤出指令面板\n"
            "LR232在群聊中使用需要先@\n"
            "<平台>\n"
            "LR232:QQ,群管理下方添加\n"
            "LR5921:QQ,群管理中添加(3502644244)\n"
            "BILI:B站,武大推协\n"
            "WECHAT:微信公众号,武大推协\n"
            "网站: https://whumystery.cn/home"
            f"{cab_web if isCab else ''}"
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
