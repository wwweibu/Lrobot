import json
from config import query_database



async def check_status(source: str, status: str = None):
    """查找状态,返回状态列表或对应的信息"""
    result = await query_database(
        "SELECT status, information FROM user_status WHERE source = %s", (source,)
    )

    if not result:
        return []

    current_status = json.loads(result[0]["status"]) if result[0]["status"] else []
    current_info = (
        json.loads(result[0]["information"]) if result[0]["information"] else []
    )

    if status is None:
        return current_status  # 只查询状态列表

    if status in current_status:
        index = current_status.index(status)
        return current_info[index]  # 返回对应的信息

    return None  # 状态不存在



# TODO 更改下面两个函数
async def add_status(qq: str, status: str, information: str = ""):
    """添加用户状态，如果状态已存在则替换对应的 information，否则追加"""
    # 获取当前用户状态
    result = await query_database(
        "SELECT status, information FROM user_status WHERE qq = ?", (qq,)
    )

    if result:
        current_status = json.loads(result[0]["status"]) if result[0]["status"] else []
        current_info = (
            json.loads(result[0]["information"]) if result[0]["information"] else []
        )
    else:
        current_status, current_info = [], []

    # 检查 status 是否已存在
    if status in current_status:
        index = current_status.index(status)
        current_info[index] = information  # 更新对应的信息
    else:
        current_status.append(status)
        current_info.append(information)

    # 更新数据库
    await update_database(
        """
        INSERT INTO user_status (qq, status, information)
        VALUES (?, ?, ?)
        ON CONFLICT(qq) DO UPDATE SET status = ?, information = ?
        """,
        (
            qq,
            json.dumps(current_status),
            json.dumps(current_info),
            json.dumps(current_status),
            json.dumps(current_info),
        ),
    )


async def delete_status(qq: str, status: str):
    """删除状态及其对应的信息"""
    # 获取当前状态
    result = await query_database(
        "SELECT status, information FROM user_status WHERE qq = ?", (qq,)
    )

    if not result:
        return  # 没有这个用户，直接返回

    current_status = json.loads(result[0]["status"]) if result[0]["status"] else []
    current_info = (
        json.loads(result[0]["information"]) if result[0]["information"] else []
    )

    if status in current_status:
        index = current_status.index(status)
        current_status.pop(index)
        current_info.pop(index)

        if current_status:  # 如果还有剩余状态，更新数据库
            await update_database(
                "UPDATE user_status SET status = ?, information = ? WHERE qq = ?",
                (json.dumps(current_status), json.dumps(current_info), qq),
            )
        else:  # 如果没有状态了，删除整个条目
            await update_database("DELETE FROM user_status WHERE qq = ?", (qq,))

