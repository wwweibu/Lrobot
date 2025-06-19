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