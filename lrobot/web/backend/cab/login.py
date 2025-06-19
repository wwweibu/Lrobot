import asyncio
from fastapi import APIRouter
from config import config

router = APIRouter()


@router.get("/password")
async def validate_password(password: str):
    """管理员页面登录密码"""
    if password == config["cab_password"]:
        return {"isValid": True}
    else:
        return {"isValid": False}


@router.get("/account")
async def validate_account(account: str):
    """管理员页面登录账号"""
    # TODO 发送验证码
    if account == config["cab_account"]:
        await asyncio.sleep(10)
        return {"isValid": True}
    else:
        return {"isValid": False}
