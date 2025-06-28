from config import path
from message.handler.msg import Msg
from logic import add_status,delete_status,download_file

async def register_first(msg: Msg):
    kind = msg.kind[:2]
    content="入会需要提交信息以及缴纳会费，如有活动形式、入会权益等需要了解请发送/帮助\n"\
            "入会信息需要复制并编辑以下内容（到*结束）：\n"\
            "姓名:张三 代号:自己取 性别:男 年级:25/25研/25博 专业:计算机科学与技术 学号:2025 电话:137 qq:123 政治面貌:群众/团员/党员 籍贯:湖北武汉 *\n"\
            "同时扫描以下二维码缴纳20会费"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送图文",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        files=[("qrcode.png",path / "storage/file/firefly/firefly.png")],
        group=msg.group,
    )
    await add_status(msg.source,"待入会")


async def register_second(msg: Msg):
    kind = msg.kind[:2]
    print(123245346)
    content="已收到付款截图并发送给管理员核对"
    Msg(
        robot=msg.robot,
        kind=f"{kind}发送文字",
        event="发送",
        source=msg.source,
        seq=msg.seq,
        content=content,
        group=msg.group,
    )
    file_path = path / f"storage/file/users/{msg.source}/{msg.files[0][0]}"
    print(file_path)
    await download_file(file_path,msg.files[0][1])
    Msg(
        robot="LR5921",
        kind="私聊发送文件",
        event="发送",
        source="663748426",
        seq=msg.seq,
        content="",
        files=[(msg.files[0][0],file_path)],
        group=msg.group,
    )
    await add_status(msg.source,"入会状态1")
    await delete_status(msg.source, "待入会")