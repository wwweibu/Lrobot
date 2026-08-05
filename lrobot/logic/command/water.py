"""水群"""

import re
import time
import random
import datetime

from logic import data
from message.handler.msg import Msg
from config import config, path, monitor_adapter


count = 0
last_send_time = 0.0
EVENING_TO_GROUP = False  # 2026-08-05 关闭:新老水群都不再自动发晚安语音;私聊订阅"晚安"的人照旧收得到


async def water_send(msg: Msg):
    """水群"""
    global count, last_send_time
    if msg.kind != "群聊接收":
        return
    if msg.group not in config["public"]["水群"]:
        return
    count += 1
    now = time.time()

    if count >= 200 and now - last_send_time >= 3600:
        content = await data.system_get("activity")
        Msg(
            platform=msg.platform,
            kind=f"群聊发送",
            event="发送",
            content=f"欢迎找小推(1326016706)或小推·人机版(me)入会。可以不用加好友直接私聊我，发送'入会'二字\n对协会活动有疑问也可以找我发送'/常见问题'(5个字符)\n当前活动：\n{content}\n注：本推仅支持固定指令，智能问答请找另一个推",
            seq=msg.seq,
            group=msg.group
        )
        user1 = "小推·人机版"
        id1 = config['LR5921_ID']
        id2 = await data.system_get("water_name")
        if not id2:
            id2 = config["LR232_QQ"]
            await data.system_edit("water_name", id2)
        msg_lists = [["/入会",
                      "阁下，欢迎您申请加入我们的推理殿堂。入会需完成信息登记并缴纳20元会费。\n若您对活动形式或会员权益存有疑问，可随时使用'/常见问题'指令查阅。\n请您复制并完善以下档案信息（至*号结束）：姓名:张三,代号:自取,性别:男,年级:24/25研/26博,专业:计算机科学与技术,学号:2025,电话:137,qq:123,政治面貌:群众/团员/党员,籍贯:湖北武汉*"],
                     ["/常见问题",
                      "尊敬的侦探阁下,您希望查阅哪个问题?\n请直接告知我对应的序号即可\n1. 介绍一下武汉大学逻辑推理协会\n2. 协会有哪些活动？\n3. 活动的频率以及参与方式（怎么报名，是否必须参与）\n4. 如何加入协会？\n5. 感觉自己没有逻辑思维qwq怎么办\n6. 内阁是什么？如何加入？\n7. 我没有玩过xxx怎么办？（染，剧本杀，读书会没看书）\n8. LRobot是什么？\n9. 一些平台特性",
                      "3",
                      "问：活动的频率以及参与方式（怎么报名，是否必须参与）\n\n答：所有活动包括协会组织的与自发组织的，均为自愿参与，无强制报名\n大型活动每年1次，平均每月1-2场\n日常活动每周1-2场（加上自发组织的则天天有）\n活动均在会员群内通知，每年招新时至校园寻宝前，活动会在招新群内通知",
                      "4",
                      "问：如何加入协会？\n\n答：加入水群即获得了一张限时会员体验卡（至校园寻宝结束）\n续费的话需要交20会费哦\n会费只需要交一次即可获得终生有效的会员资格啦~\n入会可以直接找小推，或者在微信、B站、LR232、LR5921处发送'/入会'\n入会需要缴纳会费以及填写会员信息\n仅限武汉大学的学生（不限于本科生）"],
                     ["/帮助，书单", " 理研部倾心推荐书单", "/帮助，订阅",
                      "可选择'活动、早上好、晚安、up视频更新'进行订阅，未绑定5921的其他平台无法使用"],
                     ["/帮助，绑定", "以 QQ 为基础，同步各平台身份、状态、指令权限", "(除LR5921外其他平台)/绑定",
                      "请将整条消息复制至 LR5921(QQ) 处 123456,五分钟有效",
                      "(LR5921处)请将整条消息复制至 LR5921(QQ) 处 123456,五分钟有效", "绑定成功"],
                     ["/待办", "阁下，请告知我需要提醒的具体事项。", "睡觉",
                      "请以中文方式提供提醒时间，若系统无法识别，则无返回消息，说明时间格式需要调整。", "五天后",
                      "已为您在 2025-11-03 00:00:00 设置提醒：睡觉。届时我会准时提醒您，阁下。"],
                     ["/进阶",
                      "<进阶说明>\n阁下，关于指令系统，容我为您提供一个更为高效之道:\n常规的分步指令('/a,输入b,输入c')在批量处理时略显繁琐\n进阶指令采用'/a,b,c'一步实现的方法\n为此，您可直接使用'/进阶,[分组]'来获取完整指令集\n分组列表如下：帮助,基础,入会,收集表,工具,游戏,密码,订阅,活动\n列表将呈现'指令: 用法'格式，其中'[]'内即为需要您提供的核心参数",
                      "/进阶，游戏",
                      "/成语,[成语]: 进行同音成语接龙\n/成语,[成语],知识: 返回成语释义\n/成语,[成语],同字: 进行同字成语接龙\n/成语,[成语],[数字]: 进行任意数量的同音成语接龙",
                      "/成语，我要入会，5", "恢廓大度,独行其道,倒背如流,流芳百世,视险如夷"],
                     ["/成语接龙严格",
                      "接龙游戏现已开始，阁下。\n请您随意出题，我将依据同字模式进行接龙。\n若要结束这场文字游戏，请使用'/成语接龙退出'指令",
                      "笾", "无匹配成语", "我要入会", "会家不忙", "/真心话", "世界上最大的悲剧是什么。", "/成语接龙退出",
                      "退出成功"
                      ],
                     ["/密码", "阁下，请选择您要使用的密码：凯撒、维吉尼亚、摩斯、培根或频率分析。", "摩斯",
                      "请提供您需要处理的密文。请提供由英文句点('-')和点('.')组成的密文，以空格或换行分隔，解密后未知字符将返回'？'。若有原文需要加密，请输入'无'。",
                      "无", "若上一步已输入内容，请输入'无'；若需要加密，请输入原文，且确保上一步输入了'无'", "LR5921",
                      "摩斯加密结果: .-.. / .-. / ..... / ----. / ..--- / .----"]]
        chosen_list = random.choice(msg_lists)
        content_parts = []
        for i, text in enumerate(chosen_list):
            if i % 2 == 0:
                content_parts.append(f"[节点:{id2}|''|{text}]")
            else:
                content_parts.append(f"[节点:{id1}|{user1}|{text}]")
        content = "".join(content_parts)
        content = f"[节点:{id1}|{user1}|让小推给你推荐一条指令喵~]" + content
        extra_content = [
            f"[节点:{id1}|{user1}|有什么问题使用'/留言+问题'告知小推哦~][节点:{id1}|{user1}|悄悄告诉你，使用'换成xxx'(qq号)，可以伪装成任意一个人(≧∇≦)ﾉ]",
            f"[节点:{id1}|{user1}|如果想要了解系统的更多功能，测试优化格式x乱玩√，可以加公测群786159347][节点:{id1}|{user1}|考虑清楚哦~没有写完测试报告的话，将会受到可怕的惩罚]"]
        content += random.choice(extra_content)
        Msg(
            platform=msg.platform,
            kind="群聊发送",
            event="发送",
            content=f"[节点:{id1}|{user1}|{content}]",
            user=msg.user,
            group=msg.group
        )
        count = 0
        last_send_time = now


async def water_send_evening():
    """每天0点把前一天的晚安语音发到水群"""
    if not EVENING_TO_GROUP:
        return
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    storage_path = path / "storage/file/command"
    record = storage_path / f"evening_{yesterday}.wav"
    if not record.exists():
        return

    for group in config["public"]["水群"]:
        Msg(
            platform="LR5921",
            kind="群聊发送",
            event="发送",
            group=group,
            content=f"[语音:{record}]"
        )


@monitor_adapter("/帮助_水群")
async def water_set(msg: Msg):
    """设置水群发送者"""
    numbers = re.findall(r"\d+", Msg.content_join(msg.content))
    result = "".join(numbers)
    if result:
        await data.system_edit("water_name", result)
        content = "设置成功，请耐心等待or赶紧水群"
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content=content,
            user=msg.user,
            group=msg.group,
        )
