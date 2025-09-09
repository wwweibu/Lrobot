"""帮助与转发"""

import re
import datetime

from logic import data
from message.handler.msg import Msg
from config import config, path, temp_key


def caesar_encrypt(text, shift):
    """凯撒加密"""
    encrypted = []
    for char in text:
        if char.isalpha():  # 只对字母进行加密
            start = ord("A") if char.isupper() else ord("a")
            encrypted.append(chr(start + (ord(char) - start + shift) % 26))
        else:
            encrypted.append(char)  # 其他字符不变
    return "".join(encrypted)

async def help_show(msg: Msg):
    """帮助说明"""
    help_content = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    isCab = False
    if msg.group:
        if any(msg.group in group_list for group_list in
               [config["public"]["公测群"], config["public"]["内测群"], config["public"]["内阁"]]):
            isCab = True
    else:
        user_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" in user_list:
            isCab = True
    if len(help_content) == 2:
        help_content = help_content[1]
        if help_content == "帮助":
            current_hour = datetime.datetime.now().hour
            # 使用当前小时数作为偏移量加密文本
            bonus_scene = caesar_encrypt("bonus scene", current_hour)
            content = (
                "有任何问题或建议可进行留言\n"
                "输入'/留言xxx'\n\n"
                f"Here is the zeroth {bonus_scene}"
            )
        elif help_content == "常见问题":
            content = ("/常见问题:获取常见问题列表\n"
                       "/常见问题,[序号]:输入列表序号获取对应回答")
        elif help_content == "当前活动":
            content = "/当前活动:查看当前活动"
        elif help_content == "书单":
            content = "/书单:获取推荐书单"
        elif help_content == "绑定":
            content = ("/绑定:私聊LR232、WECHAT、BILI，获取验证码\n"
                       "[验证码]:验证码私聊发送LR5921处以绑定\n"
                       "绑定可以同步各平台状态(答题进度、订阅状态等)\n"
                       "其中以LR5921为主平台")
        elif help_content == "入会":
            content = ("/入会:第一步，私聊获取入会说明\n"
                       "[会员信息]:第二步，私聊填写会员信息\n"
                       "[付款截图]:第三步，私聊发送付款截图\n"
                       "注:使用此方法仍需添加小推为好友")
        elif help_content == "反馈":
            content = ("/反馈:获取收集表列表\n"
                       "/反馈,[序号]:开始填写对应收集表\n"
                       "[回答]:回答对应问题")
        elif help_content == "小游戏":
            content = ("/小游戏:小游戏列表和对应指令\n"
                       "/成语,[成语]\n"
                       "/成语,[成语],[数字]\n"
                       "/成语,[成语],严格\n"
                       "/成语,[成语],知识\n"
                       "/成语接龙\n"
                       "/成语接龙严格\n"
                       "/成语接龙结束\n"
                       "/真心话\n"
                       "/大冒险")
        elif help_content == "工具":
            content = ("/工具:工具列表及对应指令\n"
                       "/待办,[时间],[事项]")
        elif help_content == "订阅":
            content = ("/订阅:可订阅项目及对应指令、已订阅项目\n"
                       "/取消订阅,[序号]:取消对应序号订阅\n"
                       "/订阅花火")
        elif help_content == "留言":
            content = "/留言[内容]:进行留言"
        elif help_content == "面板" and isCab:
            content = ("/面板,[功能组],[描述]:添加功能组\n"
                       "/面板功能,[功能组],[序号],[功能]:修改功能\n"
                       "/面板功能,[功能组],[功能]:添加功能\n"
                       "私聊:微部;群聊:公测群")
        elif help_content == "修改当前活动" and isCab:
            content = ("/修改当前活动,[内容]:可修改内容\n"
                       "私聊:微部;群聊:公测群、内阁")
        elif help_content == "修改当前书单" and isCab:
            content = ("/修改书单,[内容]:可修改书单\n"
                       "私聊:微部;群聊:公测群、内阁")
        elif help_content == "小推入会" and isCab:
            content = ("[入会信息]:完整发送标准入会格式即可实现信息导入\n"
                       "私聊:微部")
        elif help_content == "反馈设置" and isCab:
            content = ("/反馈设置,[标题],[时间],[问题]:设置收集表\n"
                       "其中时间是 24 点截止\n"
                       "问题格式为1xxx2xxx\n"
                       "序号后可以加.或者空格等\n"
                       "需要按顺序排列\n"
                       "私聊:内阁;群聊:公测群、内阁")
        elif help_content == "反馈结果" and isCab:
            content = ("/反馈结果:获取所有历史收集表\n"
                       "/反馈结果,[序号]:获取对应收集表的收集结果\n"
                       "其中序号使用'/反馈'查看\n"
                       "按照问题-用户进行展示")
        elif help_content == "网址" and isCab:
            content = "/网址:获取管理页面网址"
        else:
            content = "未知的指令，输入'/帮助'获取指令"
    else:
        cab_content = ("\n------\n"
                       "/面板\n"
                       "/修改当前活动\n"
                       "/修改书单\n"
                       "小推入会\n"
                       "/反馈设置\n"
                       "/反馈结果\n"
                       "/网址\n"
                       "------\n"
                       f"内阁页: whumystery.cn/{temp_key['uuid']}")
        content = (
            "<使用方式>\n"
            "私聊:直接发送指令"
            "群聊:@机器人并发送"
            "<指令列表>"
            "/帮助"
            "/常见问题"
            "/当前活动"
            "/书单"
            "/绑定"
            "/入会"
            "/反馈"
            "/小游戏"
            "/工具"
            "/订阅"
            "/留言"
            "<其他>"
            "输入'/帮助,常见问题'等了解各指令详细用法"
            "任何指令中英文逗号均通用"
            "LR232可输入'/'或点击机器人图标唤出指令面板"
            "<平台>"
            "LR232:QQ,群管理员下方添加\n"
            "LR5921:QQ,群管理中添加(3502644244)\n"
            "BILI:B站'武大推协'\n"
            "WECHAT:微信公众号'武大推协\n"
            "网站:官网 whumystery.cn 可直接点击"
            f"{cab_content if isCab else ''}"
        )

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_question(msg: Msg):
    "常见问题"
    kind = msg.kind[:2]
    content = ("输入'/常见问题，[序号]'获取回答\n"
               "协会相关:\n"
               "1.介绍一下武汉大学逻辑推理协会\n"
               "2.协会有哪些活动？\n"
               "3.活动的频率以及参与方式（怎么报名，是否必须参与）\n"
               "4.如何加入协会？\n"
               "5.感觉自己没有逻辑思维qwq怎么办\n"
               "6.内阁是什么？如何加入？\n"
               "系统相关:\n"
               "7.LRobot是什么？\n"
               "8.一些平台特性"
               )
    question = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(question) == 2:
        question = question[1].strip()
        if question.isdigit():
            if question == "1":
                content = ("武汉大学逻辑推理协会（学生）（简称武大推协）是校级学术科技类社团\n"
                           "社团以培养逻辑思维、服务推理爱好者为宗旨\n"
                           "现有社员近1000人，设多个部门\n"
                           "常年开展原创密室、校园寻宝、特工逃生路等特色活动\n"
                           "还举办全国高校 bbs 侦探推理大赛等大型赛事，同时制作社刊《夜行》，与多所高校推理协会保持交流合作\n\n"
                           "社团的宗旨是培养逻辑思维能力，连接学习、实践与兴趣爱好，为广大武大学子提供一个让自己“思想畅游”的舞台，加强校园文化氛围建设，为广大推理爱好者服务，提高大学生的自身修养，培养逻辑思维能力。"
                           )
            elif question == "2":
                content = ("大型活动:\n"
                           "侦探扮演:你将扮演侦探进行一场案件的调差，面对心怀鬼胎的npc们，你将如何找到案件的真相？\n"
                           "原创密室:从密码锁到机关陷阱，从剧情脚本到场景布置，原创的密室体验，烧脑解密的同时，带给你武大推协的独家回忆\n"
                           "校园寻宝:让珞珈山变身超大推理现场！樱花大道的树影、老斋舍的石阶都藏着密码，跟着线索拆解藏头诗、破译摩斯电码，在打卡地标时解锁校园隐藏剧情，终点还有神秘彩蛋等你来拆箱～\n"
                           "特工逃生路:十道谜题暗藏杀机，每一步选择都可能让你瞬间出局。三局较量过后，得分最高的强者将捧走冠军奖杯，快来证明你的特工天赋！\n"
                           "武汉高校推理征文赛:把你的脑洞写成故事，和中南财大、湖大的同好 battle 文笔\n"
                           "全国高校bbs侦探推理大赛:与其他社员合作答题，和全国的推理大佬一争高下\n"
                           "读书会:定期举办并在B站直播，拆解推理小说里的谜题，分析书中伏线与线索的布置、逻辑推导的运用，讨论不同创作风格和流派的特色以及优势\n"
                           "社刊:《夜行》收录社内社外的优秀原创短篇推理小说和推理评论，是推理迷的灵感集中营，你笔下的每个文字都可能成为他人破解不了的难题\n\n"
                           "日常活动:\n"
                           "剧本杀:大家化身剧中人，在社团DM的引导下开启推理盛宴。听同伴发言找破绽、巧妙隐藏身份，搜证环节反转不断，真相揭开时的畅快感让社员们难忘\n"
                           "血字游戏:诡异任务需社员凭线索探真相，面对血字提示，在死路中寻找生路\n"
                           "文字博弈:以选择题形式的文本为载体，与其他玩家进行心理和语言上的博弈\n"
                           "海龟汤:在主持人只能回答是或者不是的情况下，根据汤面找出匪夷所思的汤底\n"
                           "桌游:线上各种原创小桌游以及线下的经典桌游均可以体验，血染钟楼尤其受欢迎\n"
                           "理研推送:定期推送推理作品\n"
                           "集体观影:不定期组织观影活动")
            elif question == "3":
                content = ("所有活动包括协会组织的与自发组织的，均为自愿参与，无强制报名"
                           "大型活动每年1次，平均每月1-2场\n"
                           "日常活动每周1-2场（加上自发组织的则天天有）\n"
                           "活动均在会员群内通知，每年招新时至校园寻宝前，活动会在招新群内通知")
            elif question == "4":
                content = ("加入水群即获得了一张限时会员体验卡（至校园寻宝结束）\n"
                           "续费的话需要交20会费哦\n"
                           "会费只需要交一次即可获得终生有效的会员资格啦~\n"
                           "入会可以直接找小推，或者在微信、B站、LR232、LR5921处发送'/入会'\n"
                           "入会需要缴纳会费以及填写会员信息\n"
                           "仅限武汉大学的学生（不限于本科生）")
            elif question == "5":
                content = ("小推也跟你一样不知道密室的八种写法，栅栏密码如何摆开>_<\n"
                           "反正海龟汤灵魂三问：是不是人，有没有人死，有几个人就好了\n"
                           "文字博弈选C，血字复制上一个人的行动\n"
                           "很多活动都没有想象中的那么有门槛\n"
                           "更多地是体验解谜与思考的乐趣\n"
                           "喜欢剧本杀的可以抢每周的免费剧本杀或者自己开\n"
                           "如果喜欢桌游也可以和大家一起约局\n"
                           "接触过puzzlehunt也可以挑战把特工的题目都解出来（会长说那是不可能的）\n"
                           "或者来策划部出题为难大家\n"
                           "喜欢推理小说的也可也看看小推空间的每周分享\n"
                           "参加读书会，给征文和社刊投稿\n\n"
                           "把各种推理爱好者聚在一起，提供一个交流的平台，是推协的宗旨")
            elif question == "6":
                content = ("你也可以选择加入推协内阁（推协工作组），和一群志同道合的朋友共同参与管理推协事务，学习新技能，一起成长\n"
                           "每年在开学前后以及寻宝前后有两次招新机会，注意留意群消息\n"
                           "理研部\n"
                           "理研部负责文学创作和作品研讨，也可以组织学生参加推理赛事\n"
                           "你将和一群“推批”进行推理小说研讨交流各自观点，也会撰写推理作品推送发表自己的独到见解\n"
                           "我们会与其他高校推理社团与组织合作搭建故事场景，参加征文比赛或征稿活动，也会征集创作者，负责审稿工作，编写属于我们自己的社刊\n"
                           "我们还会联系作家团队进行交流，从而体验不同作者创作时的想法与见解\n"
                           "如果你有一定的逻辑思维能力和文学创作意愿，欢迎加入推协理研！\n\n"
                           "公关部\n"
                           "公关部负责社交媒体运营和宣传设计\n"
                           "你将负责微信公众号、QQ号、B站、小红书账号的日常运营，定期编写活动预告和总结推文，让大家及时了解活动动态、回味活动点滴\n"
                           "部内活动的照片也由你上传，让这些美好瞬间在平台上留存\n"
                           "所有推文都会在四方平台同步发布，确保信息广泛传播\n"
                           "在这里，你将学会制作公众号推文、独立创作海报、学会直播运营......\n"
                           "你可以尽情发挥创意，用文字和影像为大家搭建起了解活动的桥梁，享受这份独特的乐趣！\n\n"
                           "秘书部\n"
                           "秘书部负责财务，资料管理和与校方对接等事务\n"
                           "从接引新人入社到编辑参评文件，从日常账务管理到活动奖品供应，大大小小的活动离不开秘书部的管理和调控\n"
                           "我们需要细致用心的你！\n\n"
                           "策划部\n"
                           "策划部负责活动组织和出题，看着同学们因你组织的活动绞尽脑汁推理的样子，无疑是一种乐趣\n"
                           "你将定期举办剧本杀、桌游等线下活动，还有血字、海龟汤、文字博弈等线上活动\n"
                           "除了这些小型活动外，我们还有校园寻宝、特工逃生路、密室逃脱、侦探扮演等一年一度的大型活动等着你来规划\n"
                           "你可以尽情发挥想象力，引领同学们享受一场又一场游戏！"
                           )
            elif question == "7":
                content = ("LRobot是推协开发的社团管理工具，涵盖QQ、微信、B站、网页四个平台的界面和指令功能\n"
                           "不仅有协会业务相关的问答、入会、反馈等指令\n"
                           "也有活动通知、线上活动、活动工具等\n"
                           "以及一些日常工具")
            elif question == "8":
                content = ("LR5921最强大，系统功能实现都靠它\n"
                           "LR232存在面板，不能发网址就很麻烦\n"
                           "WECHAT有问题，内容全部都不能换行\n"
                           "BILI检测有延迟，打字较慢莫要着急~\n\n"
                           "如果在微信看到了多个句号、QQ的LR232看到'网页 中'后缺少网址均为系统特性")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{kind}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_welcome(msg: Msg):
    """欢迎内容"""
    content = ("锵锵！我是各位福尔摩斯的华生，各位侦探的小助手，武汉大学逻辑推理协会的小推:0\n"
               "QQ、微信公众号、B站、豆瓣、小红书会持续更新我们的活动及作品分享\n"
               "今年的招新群是708346432\n"
               "成为尊贵的会员后可以加入活动群，有很多谜题游戏等你来玩哦（￣︶￣）\n"
               # "悄悄告诉你，'/帮助'有神奇的效果哦"
               )
    Msg(
        platform=msg.platform,
        kind=f"{msg.kind[:2]}添加发送",
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )


async def help_activity(msg: Msg):
    """当前活动"""
    content = await data.system_get("activity")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_activity_change(msg: Msg):
    """修改当前活动"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    await data.system_edit("activity", parts[1])


async def help_book(msg: Msg):
    """推荐书单"""
    content = await data.system_get("book")
    if msg.platform in ["WECHAT", "BILI"]:
        content = f"[图片:{path / 'storage/file/command/book.png'}]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_book_change(msg: Msg):
    """修改当前书单"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    await data.system_edit("book", parts[1])
    await data.text_to_image(parts[1], path / "storage/file/command/book.png",
                             path / "storage/file/command/simsun.ttc")


async def help_web(msg: Msg):
    """获取网址"""
    content = (f"主页: whumystery.cn/{temp_key['uuid']}\n"
               f"wiki页: whumystery.cn/{temp_key['uuid']}/wiki\n"
               f"功能页: whumystery.cn/{temp_key['uuid']}/firefly\n"
               f"网盘页: whumystery.cn/{temp_key['uuid']}/file\n"
               f"时间轴页: whumystery.cn/{temp_key['uuid']}/timeline\n"
               "可点击右上按钮/电脑端导航跳转其他页面\n"
               "页面均只能查看不能修改，有效期为十分钟\n\n"
               "编辑/获取固定地址:\n"
               "1.添加 LR5921\n"
               "2.访问 whumystery.cn/cmd ,输入代号\n"
               "3.输入对应验证码\n"
               "4.等待跳转\n"
               "5.后续可收藏并直接访问 whumystery.cn/cab")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


async def help_word(msg: Msg):
    """留言"""
    content = ("来自" + msg.user + "的留言--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
    Msg(
        platform="LR5921",
        event="发送",
        kind="私聊发送",
        content=content,
        user="663748426",
    )

async def help_unknown(msg: Msg):
    """兜底指令"""
    if Msg.content_join(msg.content).startswith("/"):
        Msg(
            platform=msg.platform,
            kind=f"{msg.kind[:2]}发送",
            event="发送",
            user=msg.user,
            seq=msg.seq,
            content="无效的指令，请使用'/帮助'",
            group=msg.group,
        )
    if msg.platform in ["LR232", "WECHAT", "BILI"]:
        content = ("来自" + msg.user + "的消息--" + Msg.content_join(msg.content)).replace("[", "").replace("]", "")
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            user="663748426",
            content=content
        )
