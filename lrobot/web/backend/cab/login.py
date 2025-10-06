"""登录逻辑"""

import time
import random

from secret import secret
from message.handler.msg import Msg
from .base import APIRouter, R, Dict
from config import config, monitor_adapter, storage
from logic import user_codename_change, firefly_password_get


router = APIRouter()
login_list = storage.setdefault("logic_list", {})


@router.put("/password")
@monitor_adapter("#内阁_登录密码")
async def password_validate(data: dict):
    """管理员页面登录密码"""
    password = data["password"]
    if password == secret("lrobot"):
        return R(status="success", data="lrobot")
    for user, (token, expire_time) in list(login_list.items()):
        if password == token and time.time() < expire_time:
            del login_list[user]
            return R(status="success", data=user)
    return R(status="fail")


@router.put("/account")
@monitor_adapter("#内阁_登录账号")
async def account_validate(data: Dict):
    """管理员页面登录账号"""
    account = data["account"]
    if account == "lrobot":
        return R(status="success")
    if account.startswith("花火"):
        password = await firefly_password_get(account)
        if password:
            login_list[account] = (password, time.time() + 60)
            return R(status="success")
    user = await user_codename_change(account)
    if user:
        for identity, numbers in config["private"].items():
            if str(user) in numbers:
                token = f"{random.randint(100000, 999999)}"
                login_list[user] = (token, time.time() + 60)
                Msg(
                    platform="LR5921",
                    kind=f"私聊发送",
                    event="发送",
                    user=user,
                    content=Msg.content_disjoin(f"请在网站中输入验证码{token}"),
                )
                return R(status="success")
    return R(status="fail")
