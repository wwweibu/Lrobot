# ip 封禁处理
from time import time
from config import update_database, query_database

BAN_TIME = 600  # 封禁时间
ERROR_RESET_TIME = 10  # 访问间隔 5 次 / x 秒


async def check_and_update_ip(ip: str):
    """
    检查 IP 是否已被封禁，并更新数据库状态。
    """
    if ip == "222.20.193.18":  # 武汉大学 ip
        return False
    current_time = int(time())

    # 解封
    await update_database(
        "UPDATE system_ip SET count = -2 WHERE count = -1 AND ? - first_time > ?",
        (current_time, BAN_TIME),
    )

    # 次数重置
    await update_database(
        "UPDATE system_ip SET count = 0 WHERE count BETWEEN 1 AND 5 AND ? - first_time > ?",
        (current_time, ERROR_RESET_TIME),
    )

    # 查找 IP 记录
    result = await query_database(
        "SELECT count, first_time FROM system_ip WHERE ip = ? AND count != -2",
        (ip,),
    )

    if result:
        count = result[0]["count"]

        # IP 仍处于封禁状态
        if count == -1:
            return True

        # 累计访问次数
        if 0 <= count < 5:
            await update_database(
                "UPDATE system_ip SET count = count + 1 WHERE ip = ? AND count = ?",
                (ip, count),
            )
        elif count == 5:
            await update_database(
                "UPDATE system_ip SET count = -1, first_time = ? WHERE ip = ?",
                (
                    current_time,
                    ip,
                ),
            )
            return True  # 触发封禁

    else:
        # 如果 IP 记录不存在，则插入新记录
        await update_database(
            "INSERT INTO system_ip (ip, count, first_time) VALUES (?, 1, ?)",
            (ip, current_time),
        )

    return False
