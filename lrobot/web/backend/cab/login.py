import time
import random
from fastapi import APIRouter
from config import config
from logic import user_codename
from message.handler.msg import Msg

router = APIRouter()
login_list = {}

@router.get("/password")
async def validate_password(password: str):
    """管理员页面登录密码"""
    for source, (token, expire_time) in list(login_list.items()):
        if password == token and time.time() < expire_time:
            del login_list[source]
            return {"isValid": True}
    return {"isValid": False}


@router.get("/account")
async def validate_account(account: str):
    """管理员页面登录账号"""
    source = await user_codename(account)
    if source:
        for identity, numbers in config["私聊"].items():
            if str(source) in numbers:
                token = f"{random.randint(100000, 999999)}"
                login_list[source] = (token, time.time() + 20)
                Msg(
                    robot="LR5921",
                    kind=f"私聊发送文字",
                    event="发送",
                    source=source,
                    seq="",
                    content=f"请在网站中输入验证码{token}",
                )
                return {"isValid": True}
    return {"isValid": False}
