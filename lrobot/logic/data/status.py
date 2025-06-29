import json
from config import query_database,update_database



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


async def add_status(source: str, status: str, information: str = "无信息"):
    """添加用户状态，自动同步到各平台"""
    if status in ["qq","LR232","WECHAT","BILI","QQAPP"]:
        await edit_status(source,status,information)
        return

    qq = await check_status(source, "qq")
    if not qq:
        qq = source
    bind_list = [qq]
    for platform in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        bind_id = await check_status(qq, platform)
        if bind_id:
            bind_list.append(bind_id)
    for bind_source in bind_list:
        await edit_status(bind_source, status, information)


async def delete_status(source: str, status: str):
    """删除状态，自动同步到各平台"""
    if status in ["qq", "LR232", "WECHAT", "BILI", "QQAPP"]:
        await edit_status(source, status, None)
        return

    qq = await check_status(source, "qq")
    if not qq:
        qq = source
    bind_list = [qq]
    for platform in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        bind_id = await check_status(qq, platform)
        if bind_id:
            bind_list.append(bind_id)
    for bind_source in bind_list:
        await edit_status(bind_source, status, None)


async def edit_status(source: str, status: str, information: str = None):
    """添加/更新/删除用户状态"""
    if not source:
        return
    result = await query_database(
        "SELECT status, information FROM user_status WHERE source = %s", (source,)
    )

    if result:
        current_status = json.loads(result[0]["status"]) if result[0]["status"] else []
        current_info = (
            json.loads(result[0]["information"]) if result[0]["information"] else []
        )
    else:
        current_status, current_info = [], []

    if information is None:
        # 删除
        if status in current_status:
            index = current_status.index(status)
            current_status.pop(index)
            current_info.pop(index)
        else:
            return
    else:
        # 添加/更新
        if status in current_status:
            index = current_status.index(status)
            current_info[index] = information
        else:
            current_status.append(status)
            current_info.append(information)

    # 更新数据库
    if current_status:
        await update_database(
            """
                INSERT INTO user_status (source, status, information)
                VALUES (%s, %s, %s) AS new_val
                ON DUPLICATE KEY UPDATE
                    status = new_val.status,
                    information = new_val.information
                """,
            (
                source,
                json.dumps(current_status),
                json.dumps(current_info),
            ),
        )
    else:  # 如果状态已清空，删除记录
        await update_database("DELETE FROM user_status WHERE source = %s", (source,))
