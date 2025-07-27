"""指令列表"""

from fastapi import Request, Depends
from fastapi import APIRouter
from config import config, loggers
from .cookie import cookie_account_get

router = APIRouter()
website_logger = loggers["website"]


@router.get("/commands")
async def commands_get():
    """获取指令"""
    commands = config["commands"]
    chat_users = config["private"]
    chat_groups = config["public"]
    events = config["kind"]
    states = config["status"]
    users = list(chat_users.keys())  # 只获取键
    groups = list(chat_groups.keys())

    return {
        "commands": commands,
        "events": events,
        "states": states,
        "users": users,
        "groups": groups,
    }


@router.put("/commands")
async def commands_update(request: Request, account: str = Depends(cookie_account_get)):
    """更新指令"""
    try:
        new_commands = await request.json()
        if not isinstance(new_commands, list):
            raise Exception(f" 指令集更新错误 | 数据:{new_commands}")
        config["commands"] = new_commands
        website_logger.info(
            f"[{account}] 更新指令:{new_commands})", extra={"event": "管理操作"}
        )
    except Exception as e:
        raise Exception(e)
