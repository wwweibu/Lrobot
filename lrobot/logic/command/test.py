import asyncio
from config import path
from message.handler.msg import Msg


async def test_WECHAT(msg: Msg):
    # 测试微信
    await asyncio.sleep(4)
    Msg(
        robot=msg.robot,
        kind=f"私聊发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content="11111",
        group=msg.group,
    )


async def test_LR(msg: Msg):
    # LR232与LR5921 测试，连续回复，发送文件
    kind = msg.kind[:2]
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content="11111",
        group=msg.group,
    )
    # await asyncio.sleep(5)
    # Msg(
    #     robot=msg.robot,
    #     kind=f"{kind}发送文本",
    #     event="发送*2",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content="12345",
    #     group=msg.group,
    # )
    # await asyncio.sleep(5)
    # Msg(
    #     robot=msg.robot,
    #     kind=f"{kind}发送文件",
    #     event="发送*3",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content="111",
    #     files=[
    #         ("firefly.png", path / "storage/file/firefly/firefly.png")
    #     ],  # firefly.png 1.mp4 1.silk
    #     group=msg.group,
    # )


async def test_LR5921(msg: Msg):
    if msg.kind.startswith("私聊"):
        kind = "私聊"
    else:
        kind = "群聊"
    # LR5921 未测试
    # 获取好友分组列表、设置头像、点赞、创建收藏、处理好友请求、设置个性签名，获取好友列表，获取点赞列表，获取收藏表情，上传私聊文件（？），删除好友，获取单向好友列表
    # 设置自定义状态，获取小程序图片，获取私聊文件链接

    # LR5921 测试，获取账号状态
    # Msg(
    #     robot=msg.robot,
    #     kind="私聊获取状态",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content=msg.source,
    #     group=msg.group,
    # )

    # LR5921 测试，获取账号信息
    # Msg(
    #     robot=msg.robot,
    #     kind="私聊获取信息",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content=msg.source,
    #     group=msg.group,
    # )

    # LR5921 测试，设置签名
    # Msg(
    #     robot=msg.robot,
    #     kind="私聊设置状态",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content="好运锦鲤|59",
    #     group=msg.group,
    # )

    # LR5921 测试，分享名片
    # Msg(
    #     robot=msg.robot,
    #     kind=kind + "分享名片",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content="1324567",
    #     group=msg.group,
    # )

    # LR5921 测试，设置签名
    # Msg(
    #     robot=msg.robot,
    #     kind="私聊设置签名",
    #     event="发送",
    #     source=msg.source,
    #     seq=msg.seq,
    #     content="LR5922|你好你好，我是花火|其他",
    #     group=msg.group,
    # )


async def test_LR232(msg: Msg):
    # LR232 测试，撤回
    if msg.kind.startswith("私聊"):
        kind = "私聊"
    else:
        kind = "群聊"
    Msg(
        robot=msg.robot,
        kind=f"{kind}撤回",
        event="发送",
        source=msg.source,
        seq="ROBOT1.0_sApVLJHyaAuFyBL93jYTegTVzd6A87jYtGsI5D6crJmy3ho9qScJ8sYKz-gbVg3RplyYnFq4rryisB-jn8Uysg!!",
        group=msg.group,
    )


# TODO,下面都是测试功能
async def export(msg: Msg):
    excel_file = "output.xlsx"
    await excel_export(excel_file)
    msg.file_name = excel_file
    msg.file_url = os.path.abspath(excel_file)
    msg.content = ""
    await msg_send(msg)


async def excel_change(msg: Msg):
    file_path = await download_files(msg)
    msg.file_name = ""
    if file_path:
        textwrap = await excel_to_database_show(file_path)
        msg.content = textwrap
        await msg_send(msg)


async def excel_submit(msg: Msg):
    msg.content = "数据库更新成功"
    await msg_send(msg)
    # user_response = "110111100011"
    # await excel_to_database_deal(textwrap, user_response)


async def draw(msg: Msg):
    text_content = (
        "《LRobot用户指南》\n"
        "LR232: 232号机器人\n"
        "LR5921: 5921号机器人\n\n"
        "===========使用===========\n"
        "使用范围: 群聊、私聊\n"
        "使用方式: 群内@+消息,私聊消息\n"
        "激活方式: 群内@LR232发送消息\n"
        "\n===========帮助===========\n"
        "详细帮助: '/帮助,子标题'获取详情\n"
        "如:输入'/帮助,使用方式'\n\n"
        "其他说明:进一步了解细其他节\n"
        "指令格式:指令输入'指令+参数'\n\n"
        "以下均为指令且省略'/':\n"
        "===========物资===========\n"
        "物资租借: 发送指令获取物资租借小程序\n"
        "===========活动===========\n"
        "活动添加:名称,时间,时长,地点,简介\n"
        "活动修改: 根据提示复制后发送\n"
        "活动参与: \n"
        "活动类型查询:\n\n"
        "===========积分===========\n"
        "每日发言: \n"
    )

    # 图片设置
    width, height = 600, 800  # 图片宽度和高度
    background_color = (255, 255, 255)  # 背景颜色为白色
    text_color = (0, 0, 0)  # 文本颜色为黑色

    # 创建图片
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 加载字体，指定大小
    font = ImageFont.truetype("arial.ttf", 16)

    # 设置文本位置和行间距
    lines = text_content.split("\n")
    line_height = font.getbbox("A")[3] + 5  # 使用 getbbox 获取行高
    padding_top = 20  # 上边距

    # 绘制文本
    y = padding_top
    for line in lines:
        draw.text((20, y), line, fill=text_color, font=font)  # 在图片的左上角绘制文本
        y += line_height

    # 保存图片
    image.save("LRobot_User_Guide.png")
    print("图片已保存为 'LRobot_User_Guide.png'")


# 以下为测试成功但没有使用的功能


# elif "我不要看子雨了≧ ﹏ ≦" in msg.content and msg.qq != "2243208053":
#     await group_photo(msg)
async def group_photo(msg: Msg):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_dir, "../resources/1.jpg")
    img = Image.open(absolute_path)
    new_img = Image.new("RGB", (img.width, img.height), (255, 255, 255))
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    # 选择字体（可以根据需要调整路径和大小）
    font = ImageFont.truetype("STXINGKA.TTF", 240)
    text = msg.content.replace("我不要看子雨了≧ ﹏ ≦", "").strip()
    # 计算文本位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (img.width - text_width) // 2
    text_y = 100
    # 在图片上添加文本
    draw.text((text_x, text_y), text, fill="white", font=font)
    new_absolute_path = os.path.join(script_dir, "../resources/2.jpg")
    new_img.save(new_absolute_path)

    msg.content = [{"type": "image", "data": {"file": new_absolute_path}}]
    await msg_send(msg)


# if 'test' in msg.content
#     await password_jiemi(msg)
async def password_jiemi(msg: Msg):
    if "test1" in msg.content:
        txt = msg.content.replace("test1", "").strip()
        msg.content = fence_cipher_2(txt)
        msg.content += "\n" + fence_cipher_4(txt)
        await msg_send(msg)
        return

    txt = msg.content.replace("test", "").strip()
    results = []
    for shift in range(1, 26):
        encrypted = ""
        for char in txt:
            if char.isalpha():  # 只加密字母
                shift_base = ord("A") if char.isupper() else ord("a")
                encrypted += chr((ord(char) - shift_base + shift) % 26 + shift_base)
            else:
                encrypted += char  # 非字母字符不变
        results.append(encrypted)
    msg.content = "\n".join(results)  # 合成字符串并以换行符分隔
    await msg_send(msg)


def fence_cipher_2(plain_text):
    # 去掉空格和标点
    plain_text = "".join(plain_text.split())

    # 分组
    groups = [plain_text[i : i + 2] for i in range(0, len(plain_text), 2)]

    # 提取字符
    result = []
    for i in range(2):
        for group in groups:
            if i < len(group):
                result.append(group[i])

    return "".join(result)


def fence_cipher_4(plain_text):
    plain_text = "".join(plain_text.split())

    # 创建四个列表
    list1 = []  # 余1
    list2 = []  # 余2
    list3 = []  # 余3
    list4 = []  # 整除4

    for i, char in enumerate(plain_text):
        if i % 4 == 0:
            list1.append(char)  # 余1
        elif i % 4 == 1:
            list2.append(char)  # 余2
        elif i % 4 == 2:
            list3.append(char)  # 余3
        else:
            list4.append(char)  # 整除4

    # 合并结果
    result = "".join(list1 + list2 + list3 + list4)
    return result


# if msg.kind == 2 and msg.group == config["内阁"] or msg.qq == "663748426":
#     if "记：" in msg.content:
#         await manager(msg, 1)
#         return
#     elif "等：" in msg.content:
#         await manager(msg, 2)
#         return
#     elif "催：" in msg.content:
#         await manager(msg, 3)
#         return
#     elif "示：" in msg.content:
#         await manager(msg, 4)
#         return
#     elif "删：" in msg.content:
#         await manager(msg, 5)
#         return


async def delay_task(time_difference, msg):
    """处理 '示' 类型消息的独立计时任务"""
    await delay(time_difference)
    msg.content = "LR5921提醒待办事项：\n"
    msg.content = msg.content + await manager_send()
    await msg_send(msg)


async def manager(msg: Msg, i: int):
    content_map = {1: "记：", 2: "等：", 3: "催：", 4: "示：", 5: "删："}
    if i in content_map:
        content = msg.content.replace(content_map[i], "").strip()
        if i in [1, 2, 3]:
            await users_status_add(config["LR5921"], content_map[i], content)
        elif i == 4:
            try:
                event_time = jio.parse_time(
                    content, time_base=time.time(), time_type="time_point"
                )
                if (
                    event_time["type"] == "time_point"
                    or event_time["type"] == "time_span"
                ):
                    event_time = event_time["time"][0]
                    event_time = datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S")
                    now = datetime.now()
                    time_difference = int((event_time - now).total_seconds())
                    if time_difference > 0:
                        msg.content = "1"
                        await msg_send(msg)
                        asyncio.create_task(delay_task(time_difference, msg))
                else:
                    return
            except ValueError:
                return
        elif i == 5:
            await users_status_delete(qq_number=config["LR5921"], information=content)


async def manager_send():
    result = await execute_query(
        "SELECT status, information FROM user_status WHERE qq_number = ?",
        (config["LR5921"],),
    )

    # 定义状态的排序字典
    status_order = {"记：": 1, "等：": 2, "催：": 3}

    # 将结果转化为字符串，格式为 "状态: 信息\n"
    if result:
        # 先按状态排序
        sorted_result = sorted(
            result, key=lambda row: status_order.get(row[0], float("inf"))
        )
        status_info_list = [f"{row[0]} {row[1]}" for row in sorted_result]
        return "\n".join(status_info_list)
    else:
        return ""
