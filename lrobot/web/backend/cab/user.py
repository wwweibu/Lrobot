from fastapi import Request, APIRouter,Depends
from config import config,loggers
from .cookie import get_account_from_cookie

router = APIRouter()
website_logger = loggers["website"]


@router.get("/users")
async def get_users():
    """获取用户组"""
    chat_users = config["私聊"]
    chat_groups = config["群聊"]
    return {"private_users": chat_users, "group_users": chat_groups}


@router.put("/users")
async def update_users(request: Request,account: str = Depends(get_account_from_cookie)):
    """更新用户组"""
    try:
        new_data = await request.json()
        if not isinstance(new_data, dict):
            raise Exception(f"用户组数据格式错误 | {new_data}")

        private_users = new_data.get("private_users", {})
        group_users = new_data.get("group_users", {})
        config["私聊"] = private_users
        config["群聊"] = group_users
        website_logger.info(f"{account} 更新用户组:{private_users},{group_users}",
                            extra={"event": "请求成功"})

    except Exception as e:
        raise Exception(f"用户组更新失败: {e}")
