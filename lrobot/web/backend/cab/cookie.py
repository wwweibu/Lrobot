import urllib.parse
from fastapi import Request, HTTPException

def get_account_from_cookie(request: Request) -> str:
    raw_account = request.cookies.get("account")
    account = urllib.parse.unquote(raw_account)
    return account