"""基础配置"""

import urllib.parse
from fastapi import Request
from typing import Any, Optional
from pydantic import BaseModel

from config import loggers

# 通用包及变量
from typing import Dict
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, Query, Response, HTTPException

website_logger = loggers["website"]


class R(BaseModel):
    """统一响应格式"""
    status: str
    data: Optional[Any] = None

def cookie_account_get(request: Request):
    """从 cookie 获取账户名"""
    raw_account = request.cookies.get("account")
    if not raw_account:
        return None
    account = urllib.parse.unquote(raw_account)
    return account


def ip_get(req: Request):
    """获取 ip"""
    return req.client.host
