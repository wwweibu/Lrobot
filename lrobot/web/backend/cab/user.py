from fastapi import Request, APIRouter
from config import config

router = APIRouter()


@router.get("/users")
async def get_users():
    """获取用户组"""
    chat_users = config["私聊"]
    chat_groups = config["群聊"]
    return {"private_users": chat_users, "group_users": chat_groups}


@router.put("/users")
async def update_users(request: Request):
    """更新用户组"""
    try:
        new_data = await request.json()
        if not isinstance(new_data, dict):
            raise Exception(f"用户组数据格式错误 | {new_data}")

        private_users = new_data.get("private_users", {})
        group_users = new_data.get("group_users", {})
        config["私聊"] = private_users
        config["群聊"] = group_users

    except Exception as e:
        raise Exception(f"用户组更新失败: {e}")
