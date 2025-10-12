"""ip 封禁处理"""

from time import time

from config import database_update, database_query, loggers


async def ip_check(ip):
    """检查 IP 是否处于封禁中"""
    now = int(time())
    result = await database_query("SELECT time FROM system_ip WHERE ip = %s", (ip,))
    if result and result[0]["time"] > now:
        return True
    return False


async def ip_ban(ip):
    """封禁指定 IP"""
    expire = int(time()) + 600  # 十分钟
    await database_update(
        "INSERT INTO system_ip (ip, time) VALUES (%s, %s) ON DUPLICATE KEY UPDATE time = %s",
        (ip, expire, expire)
    )
    loggers["website"].error(f"[IP]{ip}-> 封禁 10 分钟", extra={"event": "网页日志"})
