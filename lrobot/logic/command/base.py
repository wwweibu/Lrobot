"""基础功能"""

import re

from logic import data
from message.handler.msg import Msg
from .activity import activity_diary_answer
from config import path, temp_key, monitor_adapter, config


@monitor_adapter("/基础_问题")
async def base_question(msg: Msg):
    "常见问题"
    question_file = path / "storage/file/command/question.txt"
    text = question_file.read_text(encoding="utf-8")
    qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", text, re.S)

    question = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(question) == 1:
        question_list = "\n".join([f"{i + 1}. {q.strip()}" for i, (q, a) in enumerate(qa_pairs)])
        content = "输入'/常见问题,[序号]'获取回答\n" + question_list
    else:
        num = question[1].strip()
        try:
            idx = int(num) - 1
            if 0 <= idx < len(qa_pairs):
                q, a = qa_pairs[idx]
                content = f"Q: {q.strip()}\n\nA: {a.strip()}"
            else:
                content = f"未找到序号 {num} 对应的问题，请输入 1~{len(qa_pairs)} 之间的数字。"
        except ValueError:
            content = "格式错误，请输入'/常见问题,1'类似格式"
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


@monitor_adapter("/基础_欢迎")
async def base_welcome(msg: Msg):
    """欢迎内容"""
    content = ("锵锵！我是各位福尔摩斯的华生，各位侦探的小助手，武汉大学逻辑推理协会的小推:0\n"
               "QQ、微信公众号、B站、豆瓣、小红书会持续更新我们的活动及作品分享\n"
               "今年的招新群是708346432\n"
               "成为尊贵的会员后可以加入活动群，有很多谜题游戏等你来玩哦（￣︶￣）\n"
               # "悄悄告诉你，'/帮助'有神奇的效果哦"
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


@monitor_adapter("/基础_活动")
async def base_activity(msg: Msg):
    """活动"""
    content = await data.system_get("activity")
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


@monitor_adapter("/基础_活动修改")
async def base_activity_change(msg: Msg):
    """修改活动"""
    content = Msg.content_join(msg.content)
    parts = re.split(r"[，,]", content, maxsplit=1)
    await data.system_edit("activity", parts[1].strip())
    await data.subscribe_activity()
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="修改成功",
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/基础_书单")
async def base_book(msg: Msg):
    """推荐书单"""
    content = await data.system_get("book")
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


@monitor_adapter("/基础_修改书单")
async def base_book_change(msg: Msg):
    """修改当前书单"""
    content = Msg.content_join(msg.content)
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    await data.system_edit("book", parts[1].strip())
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="修改成功",
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/基础_留言")
async def base_word(msg: Msg):
    """留言"""
    content = ("来自" + msg.user + "的留言--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        content=content,
        user=config["微部"][0],
    )
    return content


@monitor_adapter("/基础_网址")
async def base_web(msg: Msg):
    """获取网址"""
    content = ("临时网址(有效期10分钟):\n"
               f"主页: whumystery.cn/{temp_key['uuid']}\n"
               f"wiki页: whumystery.cn/{temp_key['uuid']}/wiki\n"
               f"功能页: whumystery.cn/{temp_key['uuid']}/firefly\n"
               f"网盘页: whumystery.cn/{temp_key['uuid']}/file\n"
               f"时间轴页: whumystery.cn/{temp_key['uuid']}/timeline\n"
               "长期使用:"
               "1.添加LR5921\n"
               "2.访问 whumystery.cn/cmd,输入代号\n"
               "3.输入对应验证码，等待跳转\n"
               "4.下次可直接访问 whumystery.cn/cab\n"
               "QQ上只能用临时网址,微信上可以登录"
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


@monitor_adapter("/基础_转发")
async def base_unknown(msg: Msg):
    """兜底指令"""
    content = ""
    result = await activity_diary_answer(msg)
    if result:
        return
    if Msg.content_join(msg.content).startswith("/"):
        Msg(
            platform=msg.platform,
            kind=f"{msg.kind[:2]}发送",
            event="发送",
            user=msg.user,
            seq=msg.seq,
            content="无效的指令，请使用'/帮助'",
            group=msg.group,
        )
    if msg.platform in ["LR232", "WECHAT", "BILI"]:
        content = ("来自" + msg.user + "的消息--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            user=config["微部"][0],
            content=content
        )
    return content
