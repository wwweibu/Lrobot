import re
from logic import data
from message.handler.msg import Msg
from config import path,update_database


pattern = {
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

pattern_key = {
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

async def register_first(msg: Msg):
    """入会"""
    msg_kind = msg.kind[:2]
    content = "已入会"
    files = []
    kind = f"{msg_kind}发送文字"
    identity = await data.identify_user(msg.source,msg.robot)
    if "社员" not in identity:
        content = "入会需要提交信息以及缴纳会费，如有活动形式、入会权益等需要了解请发送/帮助\n" \
                  "入会信息需要复制并编辑以下内容（到*结束）：\n" \
                  "姓名:张三 代号:自己取 性别:男 年级:25/25研/25博 专业:计算机科学与技术 学号:2025 电话:137 qq:123 政治面貌:群众/团员/党员 籍贯:湖北武汉 *\n" \
                  "同时扫描以下二维码缴纳20会费"
        files = [("qrcode.png", path / "storage/file/firefly/firefly.png")]
        kind = f"{msg_kind}发送图文"
        await data.add_status(msg.source, "待入会")
    Msg(
        robot=msg.robot,
        kind=kind,
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        files=files,
        group=msg.group,
    )


async def register_second(msg: Msg):
    kind = msg.kind[:2]
    content="已收到付款截图并发送给管理员核对"
    status = await data.check_status(msg.source)
    if "待入会" in status:
        await data.add_status(msg.source,"入会状态2")
        await data.delete_status(msg.source, "待入会")
    else:
        content = "入会成功，" + content
        await data.delete_status(msg.source,"入会状态1")
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    file_path = path / f"storage/file/users/{msg.source}/{msg.files[0][0]}"
    await data.download_file(file_path,msg.files[0][1])
    Msg(
        robot="LR5921",
        kind="私聊发送文件",
        event="发送",
        source="663748426",
        seq=msg.seq,
        content="",
        files=[(msg.files[0][0],file_path)],
        group=msg.group,
    )


async def register_third(msg: Msg):
    kind = msg.kind[:2]
    content = msg.content.strip().rstrip("*").strip()
    data = dict()
    for key, pat in pattern.items():
        match = re.search(pat, content)
        if not match:
            content = f"格式错误：缺少或格式错误字段 '{pattern_key.get(key, key)}'"
            Msg(
                robot=msg.robot,
                kind=f"{kind}发送文字",
                event="发送",
                source=msg.source,
                seq=msg.seq,
                content=content,
                group=msg.group,
            )
            return
        data[key] = match.group(1).strip()
    nickname = await data.get_user_nickname(data["qq"])
    await update_database(
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
            data["qq"],
            nickname,
            data["codename"],
            data["name"],
            data["grade"],
            data["gender"],
            data["major"],
            data["student_id"],
            data["phone"],
            data["political_status"],
            data["hometown"],
        )
    )
    content = f"已录入数据: qq:{data['qq']},昵称:{nickname},代号:{data['codename']},姓名:{data['name']},年级:{data['grade']},性别:{data['gender']},专业:{data['major']},学号:{data['student_id']},手机:{data['phone']},政治面貌:{data['political_status']},籍贯:{data['hometown']}"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    Msg(
        robot="LR5921",
        kind="私聊发送文字",
        event="发送",
        source="663748426",
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    status = await data.check_status(msg.source)
    if "待入会" in status:
        await data.add_status(msg.source, "入会状态1")
        await data.delete_status(msg.source, "待入会")
    else:
        content += "入会成功"
        await data.delete_status(msg.source, "入会状态2")
