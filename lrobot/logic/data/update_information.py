# TODO 改成其他的
import json
from .delay import delay
from config import config
from message.handler.msg import Msg
from message.handler.msg_send import msg_send

# from logic.data import users_all, download_files, excel_to_users_info


async def update_information(msg: Msg):
    file_path = await download_files(msg)
    msg.file_name = ""
    if file_path:
        await excel_to_users_info(file_path)
        info = {
            "action": "get_group_member_list",
            "params": {
                "group_id": config["水群"],
                "no_cache": True,
            },
            "echo": "get_users",
        }
        await global_ws.get("ws").send(json.dumps(info))
        await delay(10)
        info = {
            "action": "get_group_member_list",
            "params": {
                "group_id": config["玩耍地"],
                "no_cache": True,
            },
            "echo": "get_users",
        }
        await global_ws.get("ws").send(json.dumps(info))
        await delay(20)
        await users_all()
        msg.content = "会员信息更新完成"
        await msg_send(msg)
    else:
        msg.content = "文件下载错误"
        await msg_send(msg)
