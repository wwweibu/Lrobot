"""登录逻辑"""

import time
import random
from fastapi import APIRouter
from config import config
from message.handler.msg import Msg
from logic import user_codename_change, firefly_password_get


router = APIRouter()
login_list = {}


@router.get("/password")
async def password_validate(password: str):
    """管理员页面登录密码"""
    for source, (token, expire_time) in list(login_list.items()):
        if password == token and time.time() < expire_time:
            del login_list[source]
            return {"isValid": True}
    return {"isValid": False}


@router.get("/account")
async def account_validate(account: str):
    """管理员页面登录账号"""
    if account.startswith("花火"):
        password = await firefly_password_get(account)
        if password:
            login_list[account] = (password, time.time() + 30)
            return {"isValid": True, "password": password}
    source = await user_codename_change(account)
    if source:
        for identity, numbers in config["private"].items():
            if str(source) in numbers:
                token = f"{random.randint(100000, 999999)}"
                login_list[source] = (token, time.time() + 30)
                Msg(
                    platform="LR5921",
                    kind=f"私聊发送",
                    event="发送",
                    user=source,
                    seq="",
                    content=Msg.content_disjoin(f"请在网站中输入验证码{token}"),
                )
                return {"isValid": True}
    return {"isValid": False}
