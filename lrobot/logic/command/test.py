"""测试相关"""

import asyncio
from config import path, future
from message.handler.msg import Msg
from logic import data


async def test_1(msg: Msg):
    """测试函数"""
    kind = msg.kind[:2]
    msg = Msg(
        platform=msg.platform,
        kind=f"{kind}发送",
        event="发送",
        content=f"12[图片:{path}/storage/file/firefly/R.gif]",
        seq=msg.seq,
        user=msg.user,
        group=msg.group
    )

    try:
        _future = future.get(msg.num)
        response = await asyncio.wait_for(_future, timeout=20)
        print(response)
    #     await asyncio.sleep(5)
    #     Msg(
    #         platform=msg.platform,
    #         kind=f"私聊撤回",
    #         event="发送",
    #         user=msg.user,
    #         seq=response[0]
    #     )
    #
    except asyncio.TimeoutError:
        print("111111111")


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
    groups = [plain_text[i: i + 2] for i in range(0, len(plain_text), 2)]

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
