"""留言及反馈"""

import re
from datetime import datetime, timedelta

from logic import data
from message.handler.msg import Msg


async def feedback_list(msg: Msg):
    """获取当前收集表"""
    feed_list = await data.feedback_list()
    content = "当前收集表:\n" + feed_list
    content += "\n\n输入'/反馈,0'对应序号可填写反馈"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def feedback_start(msg: Msg):
    """开始填写"""
    id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(id) == 2:
        id = id[1].strip()
        try:
            id = int(id)
            question = await data.feedback_start(id)
            if question:
                content = question
                await data.status_add(msg.user, "收集", f"{id}_1")
            else:
                content = "序号错误"
        except ValueError:
            content = "序号错误"
    else:
        content = "格式错误"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def feedback_set(msg: Msg):
    """设置收集表"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=3)
    _, name, date_str, questions_str = parts
    period = datetime.strptime(date_str, "%Y.%m.%d") + timedelta(days=1)

    matches = re.split(r"(\d+)", questions_str)
    questions = []
    for i in range(1, len(matches), 2):
        qid = int(matches[i])
        text = matches[i + 1].strip()
        questions.append({"id": qid, "text": text})
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


async def feedback_write(msg: Msg):
    """收集表填写"""
    answer = Msg.content_join(msg.content)
    info = await data.status_check(msg.user, "收集")
    id, num = map(int, info.split("_"))
    question = await data.feedback_write(id, num, msg.user, answer)
    if question:
        content = question
        await data.status_add(msg.user, "收集", f"{id}_{num + 1}")
    else:
        content = "填写完成！感谢您的支持！"
        await data.status_delete(msg.user, "收集")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def feedback_result(msg: Msg):
    """查询结果"""
    content = Msg.content_join(msg.content)
    if content == "/反馈结果":
        content = await data.feedback_list(True)
        content += "\n输入'/反馈结果,序号'获取对应结果"
    else:
        id = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
        if len(id) == 2:
            id = id[1].strip()
            try:
                id = int(id)
                content = await data.feedback_export(id)
                if not content:
                    content = "无结果"
            except ValueError:
                content = "序号错误"
        else:
            content = "格式错误"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
