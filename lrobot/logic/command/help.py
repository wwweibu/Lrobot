import re
import datetime
from config import config
from message.handler.msg import Msg
#from logic import identify_user


async def help_text(msg:Msg):
    kind = msg.kind[:2]
    help_content = re.sub(r"/帮助[，,]?\s*", "", msg.content).strip()
    if help_content == "":
        content = (
            "\n《LRobot用户指南》\n"
            "[使用]\n"
            "使用范围: QQ、微信公众号、B 站三个平台\n"
            "LR232:QQ机器人，在群内管理员下方添加\n"
            "LR5921:QQ机器人，在群管理中添加\n"
            "武大推协:B站搜索\n"
            "武大推协:微信搜索公众号\n"
            "武大推协社团物资租借:搜索小程序\n"
            "\n"
            "[功能]\n"
            "[指令]\n"
            "格式:以'/xx,xxx'的方式发送指令\n"
            "私聊:直接发送\n"
            "群聊:@机器人并发送\n"
            "指令查询:输入/帮助可查看指令列表，输入/帮助,xxx（指令）可获取详情\n"
            "指令面板:LR232在私聊和群聊中输入'/'或者点击机器人图标均可唤出指令面板\n"
            "\n"
            "[入会]\n"
            "指令格式:/入会"
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

def caesar_encrypt(text, shift):
    encrypted = []
    for char in text:
        if char.isalpha():  # 只对字母进行加密
            start = ord("A") if char.isupper() else ord("a")
            encrypted.append(chr(start + (ord(char) - start + shift) % 26))
        else:
            encrypted.append(char)  # 其他字符不变
    return "".join(encrypted)


async def help_text1(msg: Msg):
    # TODO 待参考
    kind = msg.kind[:2]
    help_content = re.sub(r"/帮助[，,]?\s*", "", msg.content).strip()
    manager_content = []  # 管理员显示内容
    qq = identify_user(msg.source, msg.robot)
    is_admin = 0
    is_group = 0
    if any(qq in qq_list for qq_list in config["私聊"].values()):
        is_admin = 1
    if any(qq in qq_list for qq_list in config["群聊"].values()):
        is_group = 1
    if is_admin or is_group:
        manager_content.append("管理指南: 管理员的使用说明\n")
        manager_content.append("活动审核: 审核社员添加的活动\n")

    if help_content == "":
        content = (
            "\n《LRobot用户指南》\n"
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
            f"{manager_content[0] if manager_content else ''}"
            "以下均为指令且省略'/':\n"
            "===========物资===========\n"
            "物资租借: 发送指令获取物资租借小程序\n"
            "===========活动===========\n"
            "活动添加:名称,时间,时长,地点,简介\n"
            "活动修改: 根据提示复制后发送\n"
            f"{manager_content[1] if manager_content else ''}"
            "活动参与: 添加活动参与者\n"
            "活动类型查询: 查询所有活动类型\n\n"
            "===========积分===========\n"
            "每日发言: 每日发言获得积分\n"
            "每日龙王: 每日龙王额外获得积分\n"
        )
    elif help_content == "LR232":
        content = (
            "\n==========LR232==========\n\n"
            "武汉大学逻辑推理协会（学生）\n"
            "使用机器人即代表你遵守\n"
            "武汉大学逻辑推理协会章程\n\n"
            "官方机器人,可以在群内找到\n"
            "找LR5921要二维码也可以哦\n"
            "发送消息即可免费领养一只\n"
            "致力于提供'便捷'的服务"
        )
    elif help_content == "LR5921":
        content = (
            "\n===========LR5921===========\n\n"
            "重生之我在推协当管理\n"
            "记得改备注别把我跟小推弄混了\n"
            "致力于提供'丰富'的服务\n"
            "祝：狩猎愉快\(￣︶￣*\))"
        )
    elif help_content == "使用范围":
        content = (
            "\n===========使用范围===========\n\n"
            "群聊·武大推协管理下所有群聊\n"
            "私聊·武汉大学学生\n\n"
            "未来可能会面向所有人开放\n"
            "拜托大家多跟机器人聊天\n"
            "之后可能上线更多功能\n"
            "爱你❤️"
        )
    elif help_content == "使用方式":
        content = (
            "\n===========使用方式===========\n\n"
            "私聊:直接向LR232发送消息\n"
            "群聊:@LR232后发送消息\n"
            "不建议在社员群中发送过多消息\n\n"
            "指令可以快速唤起\n"
            "在手机端输入'/'\n"
            "在电脑端点击机器人图标\n"
            "可以达到自动填写指令并@的效果\n\n"
            "LR5921私聊群聊方式同上\n"
            "不过需要自己记指令"
        )
    elif help_content == "激活方式":
        content = (
            "\n===========激活方式===========\n\n"
            "激活指将你的官方qqbotid\n"
            "绑定你的qq号以进行后续操作\n\n"
            "需要在群聊中@LR232\n"
            "并发送任意消息即可自动激活\n"
            "未激活的用户将限制部分功能"
        )
    elif help_content == "详细帮助":
        # 获取当前小时数
        current_hour = datetime.datetime.now().hour
        # 使用当前小时数作为偏移量加密文本
        bonus_scene = caesar_encrypt("bonus scene", current_hour)

        content = (
            "\n===========详细帮助===========\n\n"
            "帮助中所有子标题均可查详细帮助\n"
            "有任何问题或建议可向LR5921留言\n"
            "输入'/留言'\n\n"
            f"Here is the zeroth {bonus_scene}"
        )
    elif help_content == "其他说明":
        content = (
            "\n===========其他说明===========\n\n"
            "机器人会使用你的代号称呼你\n"
            "代号未取尽快去小推处更新\n\n"
            "LR232是为了方便使用指令开发\n"
            "LR5921是为了探索更多可能\n"
            "存在232对话时转移到5921的情况\n\n"
            "最终解释权归武大推协所有"
        )
    elif help_content == "指令格式":
        content = (
            "\n===========指令格式===========\n\n"
            "对于指令'@LR232/指令 abc'\n"
            "由三部分组成,@,指令名和参数\n"
            "@时必须自己输入,复制消息无效\n"
            "指令名支持本条以下的所有指令\n"
            "指令名和参数之间的分隔\n"
            "可以使用空格或逗号或不分隔\n"
            "参数之间需要用逗号隔开\n"
            "中英文逗号均可\n"
            "/活动添加,a,b,c,d,e\n"
            "/活动查询\n"
            "/活动修改 a，b\n"
            "/详细帮助活动添加"
        )
    elif help_content == "管理指南" and manager_content:
        content = (
            "\n===========管理指南===========\n\n"
            "管理员包括活动、积分管理员\n"
            "管理群为内阁\n"
            "活动审核由活动管理员进行\n"
            "会员信息更新由积分管理员进行"
        )
    elif help_content == "物资租借":
        content = (
            "\n===========物资租借===========\n\n"
            "发送物资租借小程序\n"
            "由LR5921发送\n\n"
            "群聊中会直接由LR5921发送\n"
            "若与LR232私聊\n"
            "在添加5921时才会由其发送"
        )
    elif help_content == "活动添加":
        content = (
            "\n===========活动添加===========\n\n"
            "激活后可添加要开的活动\n"
            "添加后会发送至管理员审核\n\n"
            "添加格式为:\n"
            "/活动添加,名,时间,时长,地点,简介\n"
            "如: /活动添加，校园寻宝，\n"
            "下周天下午两点,3小时,教三204,\n"
            "推协一年一度的寻宝活动，旨在通\n过游戏增强同学们之间的互动与交\n流，快来参与吧！\n\n"
            "其中逗号中英文均可\n"
            "主持人会自动根据qq号识别\n"
            "记得去收集表里填上你的代号\n\n"
            "时间和时长支持自动识别\n"
            "以中文为主，如10.2,3h无法识别\n"
            "且时间识别失败无法添加活动"
        )
    elif help_content == "活动修改":
        content = (
            "\n===========活动修改===========\n\n"
            "活动添加后至活动审核完成前可修改\n"
            "复制机器人发送的消息并修改内容\n"
            "可修改主持姓名\n\n"
            "活动审核通过后也可修改\n"
            "格式为:/活动修改，时间，明天\n"
            "在名称,时间,时长,地点,主持,简介中\n"
            "选择一项属性进行修改"
        )
    elif help_content == "物资租借":
        content = (
            "\n===========物资租借===========\n\n"
            "输入该指令可以收到小程序入口\n"
            "需要激活后使用\n"
            "物资租借程序仅限社员\n"
            "查看对应物资后联系管理员借用"
        )
    elif help_content == "社团管家":
        content = (
            "\n===========社团管家===========\n\n"
            "记：记录近期的计划\n"
            "等：等待外部的结果\n"
            "催：催促超时的任务\n"
            "示：确定提醒的时间\n"
            "删：删除对应的事项\n"
            "不用@也能触发"
            "===系统更新，只能由微步进行更新，用于动态更新系统，可在群聊私聊"
        )
    else:
        content = "无效的指令，请使用 /帮助"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文本",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
