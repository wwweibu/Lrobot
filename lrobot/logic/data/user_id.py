# TODO 不需要了
from config import config
from .database import query_database, update_database


async def users_id_query(off_qq):
    # 将 off_qq 转换为 qq，通过查询数据库获取对应的 qq_number
    result = await query_database(
        "SELECT qq_number FROM user_id WHERE off_id = ?", (off_qq,)
    )
    if result and isinstance(result, list) and len(result) > 0:
        return result[0][0]  # 返回第一个元组中的第一个元素 qq_number
    return None  # 如果没有找到，返回 None


async def users_group_query(off_group):
    # 将 off_group 转换为群号
    group_mapping = config.get("groups", [])

    qq_number = None
    for group in group_mapping:
        if group.get("id") == off_group:
            qq_number = group.get("number")
            break
    if qq_number:
        return qq_number  # 返回匹配的 qq_number
    else:
        # 如果没有找到匹配，记录警告日志
        log_event("LRobot", "系统警告信息", f"收到未知群聊[{off_group}]的消息")
        return None  # 如果没有找到，返回 None


async def users_id_update(msg):
    # 更新users_id数据库
    record = await execute_query(
        "SELECT * FROM users_qq_id WHERE off_id = ?", (msg.off_qq,)
    )

    if record:
        # 如果记录存在，记录系统错误
        log_event(
            "LRobot", "系统未知错误", f"QQ {msg.qq} 对应 ID {msg.off_qq} 已存在，错误"
        )
    else:
        # 如果记录不存在，插入新记录
        await execute_update(
            "INSERT INTO users_qq_id (off_id, qq_number) VALUES (?, ?)",
            (msg.off_qq, msg.qq),
        )
        log_event("LRobot", "添加id", f"QQ {msg.qq} 对应 ID {msg.off_qq}")
