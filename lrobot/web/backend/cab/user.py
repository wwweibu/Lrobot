"""用户界面"""

from fastapi import Request, APIRouter, Depends
from config import config, loggers
from .cookie import cookie_account_get

router = APIRouter()
website_logger = loggers["website"]


@router.get("/users")
async def get_users():
    """获取用户组"""
    chat_users = config["private"]
    chat_groups = config["public"]
    return {"private_users": chat_users, "group_users": chat_groups}


@router.put("/users")
async def update_users(request: Request, account: str = Depends(cookie_account_get)):
    """更新用户组"""
    try:
        new_data = await request.json()
        if not isinstance(new_data, dict):
            raise Exception(f"用户组数据格式错误 | {new_data}")

        private_users = new_data.get("private_users", {})
        group_users = new_data.get("group_users", {})
        config["private"] = private_users
        config["public"] = group_users
        website_logger.info(
            f"[{account}] 更新用户组:{private_users},{group_users}",
            extra={"event": "管理操作"},
        )

    except Exception as e:
        raise Exception(f"用户组更新失败: {e}")
