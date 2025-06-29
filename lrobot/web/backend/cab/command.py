# 后端指令
from fastapi import Request,Depends
from fastapi import APIRouter
from config import config,loggers
from .cookie import get_account_from_cookie

router = APIRouter()
website_logger = loggers["website"]


@router.get("/commands")
async def get_commands():
    """获取指令"""
    commands = config["commands"]
    chat_users = config["私聊"]
    chat_groups = config["群聊"]
    events = config["事件"]
    states = config["状态"]
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
async def update_commands(request: Request,account: str = Depends(get_account_from_cookie)):
    """更新指令"""
    try:
        new_commands = await request.json()
        if not isinstance(new_commands, list):
            raise Exception(f" 指令集更新错误 | 数据:{new_commands}")
        config["commands"] = new_commands
        website_logger.info(f"[{account}] 更新指令:{new_commands})", extra={"event": "请求成功"})
    except Exception as e:
        raise Exception(e)
