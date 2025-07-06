import re
import datetime
from message.handler.msg import Msg


def caesar_encrypt(text, shift):
    encrypted = []
    for char in text:
        if char.isalpha():  # 只对字母进行加密
            start = ord("A") if char.isupper() else ord("a")
            encrypted.append(chr(start + (ord(char) - start + shift) % 26))
        else:
            encrypted.append(char)  # 其他字符不变
    return "".join(encrypted)


async def help_text(msg:Msg):
    kind = msg.kind[:2]
    help_content = re.sub(r"/帮助[，,]?\s*", "", msg.content).strip()
    content = ""
    if help_content == "":
        content = (
            "\n《LRobot用户指南》\n"
            "<使用>\n"
            "使用范围: QQ、微信公众号、B 站三个平台\n"
            "LR232:QQ机器人，在群内管理员下方添加\n"
            "LR5921:QQ机器人，在群管理中添加\n"
            "BILI:B站搜索'武大推协'\n"
            "WECHAT:微信搜索公众号'武大推协'\n"
            "QQAPP:QQ搜索小程序'武大推协社团物资租借'\n"
            "网站:社团官网whumystery.cn"
            "\n"
            "<功能>\n"
            "[指令]\n"
            "格式:以'/xx,xxx'的方式发送指令,其中中英文逗号通用\n"
            "私聊:直接发送\n"
            "群聊:@机器人并发送\n"
            "指令查询:输入'/帮助'可查看指令列表，输入'/帮助,xxx（指令）'可获取详情，如'/帮助,入会'\n"
            "指令面板:LR232在私聊和群聊中输入'/'或者点击机器人图标均可唤出指令面板\n"
            "\n"
            "[指令列表]\n"
            "入会:加入协会\n"
            "绑定:绑定其他平台，实现状态、身份统一\n"
        )
    elif help_content == "入会":
        content = ""
    elif help_content == "绑定":
        content = ""
    elif help_content == "帮助":
        # 获取当前小时数
        current_hour = datetime.datetime.now().hour
        # 使用当前小时数作为偏移量加密文本
        bonus_scene = caesar_encrypt("bonus scene", current_hour)
        content = (
            "有任何问题或建议可向 LR5921 留言\n"
            "输入'/留言'\n\n"
            f"Here is the zeroth {bonus_scene}"
        )
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


