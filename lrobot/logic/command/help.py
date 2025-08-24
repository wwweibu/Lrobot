"""帮助与转发"""

import re
import datetime

from message.handler.msg import Msg


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


async def help_show(msg: Msg):
    """帮助说明"""
    kind = msg.kind[:2]
    help_content = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    content = (
        "《LRobot用户指南》\n"
        "<使用>\n"
        "使用范围: QQ 平台\n"  # "使用范围: QQ、微信公众号、B 站三个平台
        "LR232:QQ 机器人，在群内管理员下方添加\n"  # "LR5921:QQ机器人，在群管理中添加\n" "BILI:B站搜索'武大推协'\n" "WECHAT:微信搜索公众号'武大推协   #"网站:社团官网 whumystery.cn\n\n"
        "<功能>\n"
        "[指令]\n"
        "格式:以'/xx,xxx'的方式发送指令,其中中英文逗号通用\n"
        "私聊:直接发送\n"
        "群聊:@机器人并发送\n"
        "指令查询:输入'/帮助'可查看指令列表，输入'/帮助,xxx（指令）'可获取详情，如'/帮助,入会'\n"
        "指令面板:LR232 在私聊和群聊中输入'/'或者点击机器人图标均可唤出指令面板\n\n"
        "[指令列表]\n"
        "帮助:系统说明与指令列表\n"
        "常见问题:常见问题列表\n"
        "入会:加入武汉大学逻辑推理协会\n"
        "订阅:订阅及查看订阅\n"  # "绑定:绑定其他平台，实现状态、身份统一\n"
        "小游戏:小游戏列表\n"
        "当前活动:当前活动\n"
        "工具:工具列表\n"
        "书单:推荐书单\n"
        "反馈:活动反馈与系统反馈\n"
        "分享:谜题分享\n"
    )

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
        elif help_content == "常见问题":
            content = "获取常见问题列表。输入'/常见问题，序号'即可获取回答"
        elif help_content == "入会":
            content = "输入'/入会，代号，电话'即可加入协会"
        elif help_content == "订阅":
            content = "输入'/订阅'查看当前订阅；输入'/订阅，天气'订阅天气，之后在每日问好时可以获取今日天气"
        elif help_content == "小游戏":
            content = "输入'/小游戏'查看当前小游戏列表；输入对应游戏指令进行游戏"
        elif help_content == "当前活动":
            content = "输入'/当前活动'查看当前正在进行的活动"
        elif help_content == "工具":
            content = "输入'/工具'查看当前工具列表，输入对应工具指令使用工具"
        elif help_content == "书单":
            content = "输入'/书单'获取推荐书单"
        elif help_content == "反馈":
            content = "输入'/反馈，xxx'提供反馈"
        elif help_content == "分享":
            content = "输入'/分享，xxx'进行分享"
        else:
            return

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{kind}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_question(msg: Msg):
    "常见问题"
    kind = msg.kind[:2]
    content = "协会相关:\n1.入会是什么？\n2.有哪些活动？\n\n系统相关:\n3.订阅能干什么？\n"
    question = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(question) == 2:
        question = question[1].strip()
        if question.isdigit():
            if question == "1":
                content = "加入协会可以享受更多精彩的活动。\n只需要输入'/入会,代号，手机即可'"
            elif question == "2":
                content = "包括海龟汤、血字、文字博弈等多个活动"
            elif question == "3":
                content = "订阅能调用相关的服务"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{kind}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_activities(msg: Msg):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="当前活动：侦探扮演，水群参加，时间：8.25-27",
        user=msg.user,
        group=msg.group,
    )


async def help_book(msg: Msg):
    content = "《莫格街凶杀案》\n《月亮宝石》\n《福尔摩斯探案全集》\n《布朗神父探案集》\n《三口棺材》\n《尼罗河上的惨案》\n《X的悲剧》\n《点与线》\n《十角馆杀人预告》\n《怪人二十面相》"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

async def help_unknown(msg: Msg):
    """兜底指令"""
    kind = msg.kind[:2]
    if Msg.content_join(msg.content).startswith("/"):
        Msg(
            platform=msg.platform,
            kind=f"{kind}发送",
            event="发送",
            user=msg.user,
            seq=msg.seq,
            content="无效的指令，请使用 /帮助",
            group=msg.group,
        )
    if msg.platform in ["LR232", "WECHAT", "BILI"]:
        Msg(
            platform="LR5921",
            kind="私聊发送",
            event="发送",
            user="663748426",
            seq=msg.seq,
            content=Msg.content_disjoin("来自" + msg.user + "的消息" + Msg.content_join(msg.content)),
            group=msg.group,
        )
