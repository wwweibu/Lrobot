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


@monitor_adapter("/入会_模板")
async def register_first(msg: Msg):
    """入会"""
    content = "档案状态：已入会。"
    identity = await data.user_identify(msg.user, msg.platform)
    if "社员" not in identity:
        content = (
            "阁下，欢迎您申请加入我们的推理殿堂。入会需完成信息登记并缴纳20元会费，且使用本方法入会仍需添加小推。\n"
            "若您对活动形式或会员权益存有疑问，可随时使用'/常见问题'指令查阅。\n"
            "请您复制并完善以下档案信息（至*号结束）："
            "姓名:张三,代号:自取,性别:男,年级:24/25研/26博,专业:计算机科学与技术,学号:2025,电话:137,qq:123,政治面貌:群众/团员/党员,籍贯:湖北武汉*\n"
        )
        await data.status_add(msg.user, msg.platform, "入会1")
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


@monitor_adapter("/入会_信息")
async def register_second(msg: Msg):
    """入会接收信息"""
    content = Msg.content_join(msg.content)
    content = re.sub(r'\s+', '', content)
    content = content.rstrip('*')
    user_data = {}
    for key, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, content, re.IGNORECASE)
        field_name = PATTERN_KEY[key]
        if not match:
            content_msg = f"阁下，您当前的信息字段'{field_name}'缺失或格式错误，请确认保留了冒号且位数正确"
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
        content = f"阁下，您当前使用的QQ号已在档案中留有记录，请确认信息无误。\n若遇任何困扰，敬请联络小推为您排忧。"
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
    info = f"阁下，您的档案已初步建立：\nqq:{user_data['qq']},代号:{user_data['codename']},姓名:{user_data['name']},年级:{user_data['grade']},性别:{user_data['gender']},专业:{user_data['major']},学号:{user_data['student_id']},电话:{user_data['phone']},政治面貌:{user_data['political_status']},籍贯:{user_data['hometown']}"
    content = info + "\n\n敬请扫描此二维码，完成20元会费的缴纳。\n请在同平台发送付款截图，完成最终的入会确认手续。"
    content += f"[图片:{path / 'storage/file/command/money.jpg'}]"

    await data.status_delete(msg.user, msg.platform, "入会1")
    await data.status_add(msg.user, msg.platform, "入会2")
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
        user=config["private"]["微部"][1],
        content=info
    )
    return content


@monitor_adapter("/入会_截图")
async def register_third(msg: Msg):
    """入会接收图片"""
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
        content = "阁下，请通过您发送付款截图的同一平台，完成最终的入会确认手续。"
    else:
        await data.user_register(user_data)
        await data.status_delete(msg.user, msg.platform, "入会2")
        content = "恭贺阁下！您已正式成为我会一员。为便于后续联络，请添加群聊：580111434，并发送暗号「玩耍地」（不用姓名+是否入会了）以完成最后的对接。"
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            user=config["private"]["微部"][1],
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


@monitor_adapter("/入会_小推")
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
