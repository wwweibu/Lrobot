from message.handler.msg import Msg

async def register_first(msg: Msg):
    kind = msg.kind[:2]
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content="入会需要提交信息以及缴纳会费，如有活动形式、入会权益等需要了解请发送/常见问题\n"
                "入会信息需要复制并编辑以下内容（到*结束）：\n"
                "姓名:张三 代号:自己取 性别:男 年级:25/25研/25博 专业:计算机科学与技术 学号:2025 电话:137 qq:123 政治面貌:群众/团员/党员 籍贯:湖北武汉 *\n"
                "同时扫描以下二维码缴纳20会费",

        group=msg.group,
    )