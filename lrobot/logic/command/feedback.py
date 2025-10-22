"""留言及反馈"""

import re
from datetime import datetime, timedelta

from logic import data
from config import monitor_adapter
from message.handler.msg import Msg


@monitor_adapter("/收集表_列表")
async def feedback_list(msg: Msg):
    """获取收集表"""
    id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(id) == 2:
        id = id[1].strip()
        try:
            id = int(id)
            question = await data.feedback_start(id)
            if question:
                content = question
                await data.status_add(msg.user, msg.platform, "收集", f"{id}_1")
            else:
                content = "阁下，您所指的序号似乎超出了当前档案的范围。烦请您核对后，从列表中选择一个有效的序号。"
        except ValueError:
            content = "格式似乎有误，阁下。正确的形式应为'/收集表,1'这样的格式，请您再试一次。"
    else:
        feed_list = await data.feedback_list()
        content = "阁下，当前开放的档案收集表如下：\n" + feed_list
        content += "\n\n若您有意填写，请输入对应序号。"
        await data.status_add(msg.user, msg.platform, "收集列表")
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


async def feedback_list_judge(msg: Msg):
    """收集表序号判断"""
    num = Msg.content_join(msg.content)
    try:
        id = int(num)
        question = await data.feedback_start(id)
        if question:
            return True
    except ValueError:
        pass
    return False


@monitor_adapter("/收集表_列表_回答")
async def feedback_list_answer(msg: Msg):
    """收集表开始填写"""
    num = Msg.content_join(msg.content)
    id = int(num)
    question = await data.feedback_start(id)
    content = question
    await data.status_delete(msg.user, msg.platform, "收集列表")
    await data.status_add(msg.user, msg.platform, "收集", f"{id}_1")
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


@monitor_adapter("/收集表_填写")
async def feedback_write(msg: Msg):
    """收集表填写"""
    answer = Msg.content_join(msg.content)
    info = await data.status_check(msg.user, msg.platform, "收集")
    id, num = map(int, info.split("_"))
    user_name = await data.user_name(msg.user, msg.platform)
    question = await data.feedback_write(id, num, user_name, answer.replace('[', '').replace(']', ''))

    if question:
        content = question
        await data.status_add(msg.user, msg.platform, "收集", f"{id}_{num + 1}")
    else:
        content = "档案已妥善收录！感谢阁下为此事付出的心力，您的贡献将为我们的推理事业添砖加瓦。"
        await data.status_delete(msg.user, msg.platform, "收集")
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


@monitor_adapter("/收集表_新建")
async def feedback_set(msg: Msg):
    """新建收集表"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=3)
    if len(parts) == 1:
        content = "请输入名称"
        await data.status_add(msg.user, msg.platform, "收集新建1")
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
    elif len(parts) < 4:
        content = "格式错误！请使用：/收集表设置,名称,日期(YYYY.MM.DD),问题1\n问题2..."
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

    _, name, date_str, questions_str = parts
    try:
        period = datetime.strptime(date_str.strip(), "%Y.%m.%d") + timedelta(days=1)
    except ValueError:
        content = "日期格式错误！请使用 YYYY.MM.DD 格式（如 2023.10.10）"
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
    matches = re.split("\n", questions_str.strip())
    questions = []
    for idx, text in enumerate(matches, start=1):
        questions.append({"id": idx, "text": text})
    await data.feedback_set(name, period, questions)
    content = "设置成功！"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return f"{name}|{period}|{questions}"


@monitor_adapter("/收集表_新建_名称")
async def feedback_set_1(msg: Msg):
    """设置收集表名称"""
    name = Msg.content_join(msg.content)
    await data.status_delete(msg.user, msg.platform, "收集新建1")
    await data.status_add(msg.user, msg.platform, "收集新建2", name)
    content = "请设置截止日期，格式为YYYY.MM.DD"
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


async def feedback_set_2_judge(msg: Msg):
    """收集表日期设置判断"""
    date_str = Msg.content_join(msg.content)
    try:
        datetime.strptime(date_str.strip(), "%Y.%m.%d") + timedelta(days=1)
        return True
    except ValueError:
        return False


@monitor_adapter("/收集表_新建_日期")
async def feedback_set_2(msg: Msg):
    """设置收集表日期"""
    date_str = Msg.content_join(msg.content)
    period = datetime.strptime(date_str.strip(), "%Y.%m.%d") + timedelta(days=1)
    name = await data.status_check(msg.user, msg.platform, "收集新建2")
    await data.status_delete(msg.user, msg.platform, "收集新建2")
    await data.status_add(msg.user, msg.platform, "收集新建3", f"{name}|{period}")
    content = "请设置问题，使用回车分割，不需要序号。"
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


@monitor_adapter("/收集表_新建_问题")
async def feedback_set_3(msg: Msg):
    """设置收集表问题"""
    matches = re.split("\n", Msg.content_join(msg.content).strip())
    questions = []
    for idx, text in enumerate(matches, start=1):
        questions.append({"id": idx, "text": text})
    info = await data.status_check(msg.user, msg.platform, "收集新建3")
    name, period = info.split("|", 1)
    await data.feedback_set(name, period, questions)
    await data.status_delete(msg.user, msg.platform, "收集新建3")
    content = "设置成功！"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return f"{name}|{period}|{questions}"


@monitor_adapter("/收集表_结果")
async def feedback_result(msg: Msg):
    """查询结果"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 1:
        content = await data.feedback_list(True)
        content += "\n回复序号获取对应结果"
        await data.status_add(msg.user, msg.platform, "收集结果")
    else:
        id = parts[1].strip()
        try:
            id = int(id)
            content = await data.feedback_export(id)
            if not content:
                content = "序号超出范围，请输入'/收集表结果'获取到的序号"
        except ValueError:
            content = "序号错误,请输入'/收集表结果,1'类似格式"
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


async def feedback_result_judge(msg: Msg):
    """收集表结果判断"""
    num = Msg.content_join(msg.content)
    try:
        id = int(num)
        content = await data.feedback_export(id)
        if content:
            return True
    except ValueError:
        pass
    return False


@monitor_adapter("/收集表_结果_回答")
async def feedback_result_answer(msg: Msg):
    """收集表结果"""
    num = Msg.content_join(msg.content)
    id = int(num)
    content = await data.feedback_export(id)
    await data.status_delete(msg.user, msg.platform, "收集结果")
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

@monitor_adapter("/收集表_删除")
async def feedback_delete(msg: Msg):
    """删除收集表"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 1:
        content = await data.feedback_list(True)
        content += "\n回复序号删除对应结果"
        await data.status_add(msg.user, msg.platform, "收集删除")
    else:
        id = parts[1].strip()
        try:
            id = int(id)
            result = await data.feedback_delete(id)
            if result:
                content = "删除成功"
            else:
                content = "序号超出范围，请输入'/收集表删除'获取到的序号"
        except ValueError:
            content = "序号错误，请输入'/收集表删除,1'类似格式"
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


@monitor_adapter("/收集表_删除_回答")
async def feedback_delete_answer(msg: Msg):
    """收集表结果"""
    num = Msg.content_join(msg.content)
    id = int(num)
    result = await data.feedback_delete(id)
    if result:
        content = "删除成功"
    else:
        content = "序号超出范围，请输入'/收集表删除'获取到的序号"
    await data.status_delete(msg.user, msg.platform, "收集删除")
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
