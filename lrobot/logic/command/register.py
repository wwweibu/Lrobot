"""入会相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import path, storage, monitor_adapter, future, config

FIELD_PATTERNS = {
    "name": r"姓名[：:]?(?P<name>[^，,]+)",
    "codename": r"代号[：:]?(?P<codename>[^，,]+)",
    "gender": r"性别[：:]?(?P<gender>男|女)",
    "grade": r"年级[：:]?(?P<grade>\d{2}(研|博)?)",
    "major": r"专业[：:]?(?P<major>[^，,]+)",
    "student_id": r"学号[：:]?(?P<student_id>20\d{11})",
    "phone": r"电话[：:]?(?P<phone>1\d{10})",
    "qq": r"qq[：:]?(?P<qq>\d{5,12})",
    "political_status": r"政治面貌[：:]?(?P<political_status>群众|团员|党员)",
    "hometown": r"籍贯[：:]?(?P<hometown>[\u4e00-\u9fff]{2,})",
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


@monitor_adapter("/入会_发送模板")
async def register_first(msg: Msg):
    """入会"""
    content = "已入会"
    identity = await data.user_identify(msg.user, msg.platform)
    if "社员" not in identity:
        content = (
            "入会需要填写信息并缴纳会费20元，如有活动形式、入会权益等需要了解请发送'/常见问题'\n"
            "信息将发送至管理员审核，且使用此方法入会仍需添加小推\n"
            "复制并编辑以下内容(到*结束):\n"
            "姓名:张三,代号:自己取,性别:男,年级:25/25研/25博,专业:计算机科学与技术,学号:2025,电话:137,qq:123,政治面貌:群众/团员/党员,籍贯:湖北武汉*\n"
        )
        await data.status_add(msg.user, msg.platform, "入会", 1)
    if msg.platform == "WECHAT":
        content = content.replace("\n", "...")
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=content,
        user=msg.user
    )
    return content


@monitor_adapter("/入会_填写信息")
async def register_second(msg: Msg):
    """入会接收信息"""
    info = await data.status_check(msg.user, msg.platform, "入会")
    if str(info) != "1":
        content = "您已填写过信息，请发送截图。如有问题请联系小推"
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content=content
        )
        return content
    content = Msg.content_join(msg.content)
    content = re.sub(r'\s+', '', content)
    content = content.rstrip('*')
    user_data = {}
    for key, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, content, re.IGNORECASE)
        field_name = PATTERN_KEY[key]
        if not match:
            content_msg = f"信息缺少或格式错误: {field_name}"
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                content=content_msg,
                user=msg.user,
            )
            return content_msg

        value = match.group(key).strip()
        user_data[key] = value

    result = await data.user_member_judge(user_data["qq"])
    if result:
        content = f"当前qq已注册，请确认输入正确\n如有问题请联系小推"
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content=content
        )
        return content
    register_list[msg.user] = user_data
    info = f"已录入数据: qq:{user_data['qq']},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},电话:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    content = info + "\n\n现在请扫描二维码缴纳20会费\n请在同平台发送付款截图\n截图将由管理员核对"
    content += f"[图片:{path / 'storage/file/command/money.jpg'}]"

    await data.status_add(msg.user, msg.platform, "入会", 2)
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
        user=config["private"]["微部"][0],
        content=info
    )
    return content


@monitor_adapter("/入会_接收付款截图")
async def register_third(msg: Msg):
    """入会接收图片"""
    info = await data.status_check(msg.user, msg.platform, "入会")
    if str(info) != "2":
        return "未进入第三阶段"
    file_path = path / f"storage/file/user/{msg.user}/{msg.content[0]['data']['file']}"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, file_url)
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        msg1 = Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
        await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
    user_data = register_list.get(msg.user, "")
    if not user_data:
        content = "请使用发送付款截图的平台进行入会"
    else:
        await data.user_register(user_data)
        await data.status_delete(msg.user, msg.platform, "入会")
        content = "入会成功，请添加小推qq'1326016706'，发送暗号'玩耍地'"
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            user=config["private"]["微部"][0],
            content=f"[图片:{file_path}]"
        )
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
    )
    return content


@monitor_adapter("/入会_小推填写")
async def register_official(msg: Msg):
    """小推入会"""
    content = Msg.content_join(msg.content)
    content = re.sub(r'\s+', '', content)
    content = content.rstrip('*')
    user_data = {}

    for key, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, content, re.IGNORECASE)
        field_name = PATTERN_KEY[key]
        if not match:
            content_msg = f"信息缺少或格式错误: {field_name}"
            Msg(
                platform=msg.platform,
                event="发送",
                kind="私聊发送",
                seq=msg.seq,
                content=content_msg,
                user=msg.user,
            )
            return content_msg

        value = match.group(key).strip()
        user_data[key] = value

    result = await data.user_member_judge(user_data["qq"])
    if result:
        content = f"当前qq已注册，请确认输入正确"
        Msg(
            platform=msg.platform,
            event="发送",
            kind="私聊发送",
            seq=msg.seq,
            user=msg.user,
            content=content
        )
        return content
    content = f"已录入数据: qq:{user_data['qq']},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},手机:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    Msg(
        platform=msg.platform,
        event="发送",
        kind="私聊发送",
        seq=msg.seq,
        content=content,
        user=msg.user,

    )
    await data.user_register(user_data)
    return content
