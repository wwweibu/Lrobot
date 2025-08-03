"""botpy 旧逻辑，使用需安装 botpy"""
# 把这两个函数在botpy/api.py的最下面，修改后可上传本地文件
async def post_group_file(
    self,
    group_openid: str,
    file_type: int,
    url: str,
    srv_send_msg: bool = False,
) -> message.Media:
    if os.path.isfile(url):  # 检查是否为本地文件路径
        # 读取本地文件并编码为 base64
        with open(url, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
    else:  # 假设传入的是 URL
        response = requests.get(url)
        if response.status_code == 200:
            file_data = base64.b64encode(response.content).decode("utf-8")
        else:
            print(f"下载文件失败，状态码: {response.status_code}")
    payload = {
        "group_openid": group_openid,
        "file_type": file_type,
        "file_data": file_data,  # 使用 base64 编码的文件数据
        "srv_send_msg": srv_send_msg,
    }
    route = Route("POST", "/v2/groups/{group_openid}/files", group_openid=group_openid)
    return await self._http.request(route, json=payload)


async def post_c2c_file(
    self,
    openid: str,
    file_type: int,
    url: str,
    srv_send_msg: bool = False,
) -> message.Media:
    if os.path.isfile(url):  # 检查是否为本地文件路径
        # 读取本地文件并编码为 base64
        with open(url, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
    else:  # 假设传入的是 URL
        response = requests.get(url)
        if response.status_code == 200:
            file_data = base64.b64encode(response.content).decode("utf-8")
        else:
            print(f"下载文件失败，状态码: {response.status_code}")
    payload = {
        "openid": openid,
        "file_type": file_type,
        "file_data": file_data,  # 使用 base64 编码的文件数据
        "srv_send_msg": srv_send_msg,
    }
    route = Route("POST", "/v2/users/{openid}/files", openid=openid)
    return await self._http.request(route, json=payload)


# 下面的为主要代码，可参考 botpy 的 pythonsdk 中的包引入
import re
import botpy
from botpy.message import C2CMessage, GroupMessage
from log import loggers
from config import config
from message.handler.msg import Msg

adapter_logger = loggers["adapter"]
global_api = {}  # 用于存储 message.api


def set_global_api(api):
    # 设置botpy的全局api
    global global_api
    if "api" not in global_api:  # 只在第一次赋值
        global_api["api"] = api


class MyClient(botpy.Client):
    #  官方QQ机器人客户端类
    async def on_ready(self):
        adapter_logger.debug(f"⌈LR232⌋ 启动成功", extra={"event": "运行日志"})

    @staticmethod
    async def on_c2c_message_create(message: C2CMessage):
        adapter_logger.debug(f"⌈LR232⌋ 接收:{message}", extra={"event": "消息接收"})
        set_global_api(message._api)
        message.content = await msg_content_join(message.content)
        files = {}
        if message.attachments:
            for attachment in message.attachments:
                file_name = attachment.get("filename")
                file_url = attachment.get("url")
                if file_name and file_url:
                    files.append((file_name, file_url))
            Msg(
                robot="LR232",
                kind="私聊文件消息" if message.content else "私聊图文消息",
                event="处理",
                source=message.author.user_openid,
                seq=message.id,
                content=message.content,
                files=files,
            )
        else:
            Msg(
                robot="LR232",
                kind="私聊文字消息",
                event="处理",
                source=message.author.user_openid,
                seq=message.id,
                content=message.content,
                files=files,
            )

    @staticmethod
    async def on_group_at_message_create(message: GroupMessage):
        adapter_logger.debug(f"⌈LR232⌋ 接收:{message}", extra={"event": "消息接收"})
        set_global_api(message._api)
        message.content = await msg_content_join(message.content)
        files = {}
        if message.attachments:
            for attachment in message.attachments:
                file_name = attachment.get("filename")
                file_url = attachment.get("url")
                if file_name and file_url:
                    files.append((file_name, file_url))
            Msg(
                robot="LR232",
                kind="私聊文件消息" if message.content else "私聊图文消息",
                event="处理",
                source=message.author.member_openid,
                seq=message.id,
                content=message.content,
                files=files,
                group=message.group_openid,
            )
        else:
            Msg(
                robot="LR232",
                kind="私聊文字消息",
                event="处理",
                source=message.author.member_openid,
                seq=message.id,
                content=message.content,
                files=files,
                group=message.group_openid,
            )


async def msg_content_join(content):
    # 转换内容中的表情包
    content = content.strip()
    pattern = r"<faceType=(\d+),faceId=\"(\d*)\".*?>"

    def replace_face(match):
        face_type = int(match.group(1))  # 获取 faceType

        if face_type == 1:
            face_id = int(match.group(2))  # 获取 faceId
            emoji_name = config["emojis"].get(face_id, "未知表情")
            return f"[{emoji_name}]"
        elif face_type == 4:
            return "[动画表情]"
        else:
            return match.group(0)  # 保留原内容，适用于其他情况

    # 替换所有匹配项
    return re.sub(pattern, replace_face, content)


async def LR232_start():
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    await client.start(appid=config["appid"], secret=config["secret"])


# 以下是需要并入 msg_send 的 botpy 发送逻辑
async def msg_send(msg: Msg):
    if msg.robot == "LR232":
        if msg.group:
            # 发送群消息
            message_instance = GroupMessage(global_api.get("api"), "", {})
            uploadMedia = ""
            if msg.files:
                # 调用上传函数，传入 base64 编码的文件内容
                uploadMedia = await message_instance.api.post_group_file(
                    group_openid=msg.group,
                    file_type=1,  # 图片类型
                    url=msg.files[0][1],  # 传入 base64 编码后的文件内容
                )
            await message_instance.api.post_group_message(
                group_openid=msg.group,
                msg_type=7 if uploadMedia else 0,
                content=msg.content,
                media=uploadMedia if uploadMedia else None,
                msg_id=msg.seq,
            )
            # 记录消息
            if msg.files:
                msg.content = f"{msg.content}|{msg.files[0][1]}"
            adapter_logger.debug(
                f"⌈LR232⌋ 发送:文件{msg.content}", extra={"event": "消息发送"}
            )
        else:
            # 发送好友消息
            message_instance = C2CMessage(global_api.get("api"), "", {})
            uploadMedia = ""
            if msg.files:
                # 调用上传函数，传入 base64 编码的文件内容
                uploadMedia = await message_instance.api.post_c2c_file(
                    openid=msg.source,
                    file_type=4,  # 图片类型
                    url=msg.files[0][1],  # 传入 base64 编码后的文件内容
                )
            await message_instance.api.post_c2c_message(
                openid=msg.group,
                msg_type=7 if uploadMedia else 0,
                content=msg.content,
                media=uploadMedia if uploadMedia else None,
                msg_id=msg.seq,
            )
            if msg.files:
                msg.content = f"{msg.content}|{msg.files[0][0]}"
            adapter_logger.debug(
                f"⌈LR232⌋ 发送:文件{msg.content}", extra={"event": "消息发送"}
            )
