"""入会相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import path, database_update, storage

PATTERN = re.compile(
    r"姓名:(?P<name>[^，,]+)[，,]"
    r"代号:(?P<codename>[^，,]+)[，,]"
    r"性别:(?P<gender>[^，,]+)[，,]"
    r"年级:(?P<grade>[^，,]+)[，,]"
    r"专业:(?P<major>[^，,]+)[，,]"
    r"学号:(?P<student_id>[^，,]+)[，,]"
    r"电话:(?P<phone>[^，,]+)[，,]"
    r"qq:(?P<qq>[^，,]+)[，,]"
    r"政治面貌:(?P<political_status>[^，,]+)[，,]"
    r"籍贯:(?P<hometown>[^，,]+)$"
)

VALIDATION = {
    "gender": lambda v: v in ("男", "女"),
    "grade": lambda v: re.fullmatch(r"\d{2}(研|博)?", v),
    "student_id": lambda v: re.fullmatch(r"\d{13}", v),
    "phone": lambda v: re.fullmatch(r"1\d{10}", v),
    "qq": lambda v: re.fullmatch(r"\d{5,12}", v),
    "political_status": lambda v: v in ("群众", "团员", "党员"),
    "hometown": lambda v: len(v) >= 2 and all("\u4e00" <= ch <= "\u9fff" for ch in v.strip()),
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

register_list = storage.setdefault("register_list", {})

async def register_first(msg: Msg):
    """入会"""
    content = "已入会"
    identity = await data.user_identify(msg.user, msg.platform)
    if "社员" not in identity:
        content = (
            "入会需要填写信息并缴纳会费20元，如有活动形式、入会权益等需要了解请发送'/常见问题'\n"
            "首先复制并编辑以下内容（到*结束）：\n"
            "姓名:张三,代号:自己取,性别:男,年级:25/25研/25博,专业:计算机科学与技术,学号:2025,电话:137,qq:123,政治面貌:群众/团员/党员,籍贯:湖北武汉*\n"
            "信息将发送至管理员审核，且使用此方法入会仍需添加小推\n"
        )
        await data.status_add(msg.user, "入会", "1")
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=content,
        user=msg.user
    )


async def register_second(msg: Msg):
    """入会接收信息"""
    info = await data.status_check(msg.user, "入会")
    if info != "1":
        return
    content = Msg.content_join(msg.content).rstrip("*")
    match = PATTERN.fullmatch(content)
    if not match:
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content="信息缺少"
        )
        return
    user_data = match.groupdict()
    for field, validator in VALIDATION.items():
        value = user_data.get(field, "")
        if not validator(value):
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                user=msg.user,
                content=f"信息'{PATTERN_KEY[field]}'格式错误"
            )
            return
    result = await data.user_member_judge(user_data["qq"])
    if result:
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content=f"当前qq已注册，请确认输入正确\n如有问题请联系管理员"
        )
        return
    nickname = await data.user_nickname_get(user_data["qq"])
    register_list[msg.user] = [user_data, nickname]
    info = f"已录入数据: qq:{user_data['qq']},昵称:{nickname},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},手机:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    content = info + "\n\n现在请扫描二维码缴纳20会费，发送付款截图\n请在同平台进行发送\n截图将由管理员核对"
    content += f"[图片:{path / 'storage/file/command/money.jpg'}]"
    if msg.platform == "WECHAT":
        content = f"[图片:{path / 'storage/file/command/money.jpg'}]"
    await data.status_add(msg.user, "入会", "2")
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        user=msg.user,
        content=content
    )
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        user="663748426",
        content=info
    )


async def register_third(msg: Msg):
    """入会接收图片"""
    info = await data.status_check(msg.user, "入会")
    if info != "2":
        return
    file_path = path / f"storage/file/user/{msg.user}/{msg.content[0]['data']['file']}"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, msg.content[0]['data']['url'])
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
    user_data, nickname = register_list[msg.user]
    await database_update(
        """
        INSERT INTO user_information (
            qq, nickname, codename, name, grade, gender,
            major, student_id, phone, political_status, hometown
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        ) AS new
        ON DUPLICATE KEY UPDATE
            nickname = new.nickname,
            codename = new.codename,
            name = new.name,
            grade = new.grade,
            gender = new.gender,
            major = new.major,
            student_id = new.student_id,
            phone = new.phone,
            political_status = new.political_status,
            hometown = new.hometown
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
    await data.status_delete(msg.user, "入会")
    content = "入会成功，请添加小推qq'1326016706'，发送暗号'玩耍地'"
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        user=msg.user,
        content=content
    )
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        user="663748426",
        content=f"[图片:{file_path}]"
    )


async def register_offical(msg: Msg):
    """小推入会"""
    content = Msg.content_join(msg.content).rstrip("*")
    match = PATTERN.fullmatch(content)
    if not match:
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content="信息缺少"
        )
        return
    user_data = match.groupdict()
    for field, validator in VALIDATION.items():
        value = user_data.get(field, "")
        if not validator(value):
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                user=msg.user,
                content=f"信息'{PATTERN_KEY[field]}'格式错误"
            )
            return
    result = await data.user_member_judge(user_data["qq"])
    if result:
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content=f"当前qq已注册，请确认输入正确"
        )
        return
    nickname = await data.user_nickname_get(user_data["qq"])
    content = f"已录入数据: qq:{user_data['qq']},昵称:{nickname},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},手机:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        user=msg.user,
        content=content
    )
    await database_update(
        """
        INSERT INTO user_information (
            qq, nickname, codename, name, grade, gender,
            major, student_id, phone, political_status, hometown
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        ) AS new
        ON DUPLICATE KEY UPDATE
            nickname = new.nickname,
            codename = new.codename,
            name = new.name,
            grade = new.grade,
            gender = new.gender,
            major = new.major,
            student_id = new.student_id,
            phone = new.phone,
            political_status = new.political_status,
            hometown = new.hometown
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
