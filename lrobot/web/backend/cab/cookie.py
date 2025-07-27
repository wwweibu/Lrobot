"""获取用户"""

import urllib.parse
from fastapi import Request


def cookie_account_get(request: Request):
    """从 cookie 获取账户名"""
    raw_account = request.cookies.get("account")
    account = urllib.parse.unquote(raw_account)
    return account
