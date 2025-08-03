"""加群/好友欢迎"""

from message.handler.msg import Msg


async def welcome_all(msg: Msg):
    """多平台欢迎内容"""
    kind = f"{msg.kind[:2]}添加发送"
    if msg.platform == "WECHAT":
        kind = "私聊发送"
        content = "锵锵！我是各位福尔摩斯的华生，各位侦探的小助手，武汉大学逻辑推理协会的小推:O\n公众号上会持续更新我们的活动及作品分享\n今年的招新群是708346432\n成为尊贵的会员后可以加入活动群，有很多谜题游戏等你来玩哦（￣︶￣）"
    else:

        content = "这里是 LRobot，武大推协开发的多平台聊天工具，使用'/帮助'获取更多功能"

    Msg(
        platform=msg.platform,
        kind=kind,
        event="发送",
        user=msg.user,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
