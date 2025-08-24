"""入会相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import path, database_update

PATTERN = {
    "name": r"姓名:(\S+)",
    "codename": r"代号:(\S+)",
    "gender": r"性别:(男|女)",
    "grade": r"年级:(\d{2}(?:研|博)?)",
    "major": r"专业:(.+?)",
    "student_id": r"学号:(\d{13})",
    "phone": r"电话:(1\d{10})",
    "qq": r"qq:(\d{5,12})",
    "political_status": r"政治面貌:(群众|团员|党员)",
    "hometown": r"籍贯:([\u4e00-\u9fa5]{2,}(?:[\u4e00-\u9fa5]{2,})?)",
}

PATTERN_KEY = {
    "name": "姓名",
    "codename": "代号",
    "gender": "性别",
    "grade": "年级",
    "major": "专业",
    "student_id": "学号",
    "phone": "电话",
    "qq": "QQ",
    "political_status": "政治面貌",
    "hometown": "籍贯",
}


async def register_linshi(msg: Msg):
    register = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(register) != 3:
        content = "入会信息错误，请填写'/入会，代号，电话'"
    else:
        status = await data.status_check(msg.user)
        if "入会成功" in status:
            content = "已入会"
        else:
            await data.status_add(msg.user, "入会成功")
            content = "入会成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

async def register_first(msg: Msg):
    """入会"""
    msg_kind = msg.kind[:2]
    content = "已入会"
    files = []
    kind = f"{msg_kind}发送文字"
    identity = await data.user_identify(msg.user, msg.platform)
    if "社员" not in identity:
        content = (
            "入会需要提交信息以及缴纳会费，如有活动形式、入会权益等需要了解请发送'/常见问题'\n"
            "入会信息需要复制并编辑以下内容（到*结束）：\n"
            "姓名:张三 代号:自己取 性别:男 年级:25/25研/25博 专业:计算机科学与技术 学号:2025 电话:137 qq:123 政治面貌:群众/团员/党员 籍贯:湖北武汉 *\n"
            "同时扫描以下二维码缴纳20会费，发送付款截图（单独发送图片）\n"
            "信息与付款截图将发送至管理员审核"
        )
        files = [("money.jpg", path / "storage/file/command/money.jpg")]
        kind = f"{msg_kind}发送图文"
        await data.status_add(msg.user, "待入会")
    Msg(
        platform=msg.platform,
        kind=kind,
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        files=files,
        group=msg.group,
    )


async def register_second(msg: Msg):
    """入会接收图片"""
    kind = msg.kind[:2]
    content = "已收到付款截图并发送给管理员核对"
    status = await data.status_check(msg.user)
    if "待入会" in status:
        await data.status_add(msg.user, "入会状态2")
        await data.status_delete(msg.user, "待入会")
    else:
        content = "入会成功，" + content
        await data.status_delete(msg.user, "入会状态1")
    Msg(
        platform=msg.platform,
        kind=f"{kind}发送文字",
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    file_path = path / f"storage/file/users/{msg.user}/{msg.files[0][0]}"
    await data.file_download(file_path, msg.files[0][1])
    Msg(
        platform="LR5921",
        kind="私聊发送文件",
        event="发送",
        user="663748426",
        seq=msg.seq,
        content="",
        files=[(msg.files[0][0], file_path)],
        group=msg.group,
    )


async def register_third(msg: Msg):
    """入会接收信息"""
    kind = msg.kind[:2]
    content = msg.content.strip().rstrip("*").strip()
    user_data = dict()
    for key, pat in PATTERN.items():
        match = re.search(pat, content)
        if not match:
            content = f"信息'{PATTERN_KEY.get(key, key)}'缺少或格式错误"
            Msg(
                platform=msg.platform,
                kind=f"{kind}发送文字",
                event="发送",
                user=msg.user,
                seq=msg.seq,
                content=content,
                group=msg.group,
            )
            return
        user_data[key] = match.group(1).strip()
    nickname = await data.user_nickname_get(user_data["qq"])
    await database_update(
        """
        INSERT INTO user_information (
            qq, nickname, codename, name, grade, gender,
            major, student_id, phone, political_status, hometown
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            nickname = VALUES(nickname),
            codename = VALUES(codename),
            name = VALUES(name),
            grade = VALUES(grade),
            gender = VALUES(gender),
            major = VALUES(major),
            student_id = VALUES(student_id),
            phone = VALUES(phone),
            political_status = VALUES(political_status),
            hometown = VALUES(hometown)
        """,
        (
            user_data["qq"],
            nickname,
            user_data["codename"],
            user_data["name"],
            user_data["grade"],
            user_data["gender"],
            user_data["major"],
            user_data["student_id"],
            user_data["phone"],
            user_data["political_status"],
            user_data["hometown"],
        ),
    )
    content = f"已录入数据: qq:{user_data['qq']},昵称:{nickname},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},手机:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    Msg(
        platform=msg.platform,
        kind=f"{kind}发送文字",
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    Msg(
        platform="LR5921",
        kind="私聊发送文字",
        event="发送",
        user="663748426",
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    status = await data.status_check(msg.user)
    if "待入会" in status:
        await data.status_add(msg.user, "入会状态1")
        await data.status_delete(msg.user, "待入会")
    else:
        content += "入会成功"
        await data.status_delete(msg.user, "入会状态2")
