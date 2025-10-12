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
                content = "序号错误"
        except ValueError:
            content = "序号错误，请输入'/收集表,1'类似格式"
    else:
        feed_list = await data.feedback_list()
        content = "当前收集表:\n" + feed_list
        content += "\n\n输入'/收集表,[序号]'可填写反馈"
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
    question = await data.feedback_write(id, num, user_name, answer)
    if question:
        content = question
        await data.status_add(msg.user, msg.platform, "收集", f"{id}_{num + 1}")
    else:
        content = "填写完成！感谢您的支持！"
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
    """设置收集表"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=3)
    if len(parts) < 4:
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
    period = datetime.strptime(date_str.strip(), "%Y.%m.%d") + timedelta(days=1)

    matches = re.split("\n", questions_str.strip())
    questions = []
    for idx, text in enumerate(matches, start=1):
        questions.append({"id": idx, "text": text})
    await data.feedback_set(name, period, questions)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="设置成功！",
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
        content += "\n输入'/收集表结果,[序号]'获取对应结果"
    else:
        id = parts[1].strip()
        try:
            id = int(id)
            content = await data.feedback_export(id)
            if not content:
                content = "无结果"
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


@monitor_adapter("/收集表_删除")
async def feedback_delete(msg: Msg):
    """删除收集表"""
    id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(id) == 2:
        id = id[1].strip()
        try:
            id = int(id)
            await data.feedback_delete(id)
            content = "删除成功"
        except ValueError:
            content = "序号错误，请输入'/收集表删除,1'类似格式"
    else:
        content = "格式错误，请输入'/收集表删除,1'类似格式"
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
