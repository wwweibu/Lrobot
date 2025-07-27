"""用户状态相关"""

import json

from config import database_query, database_update


async def status_check(user=None, status=None):
    """查找状态,
    填写用户，返回状态列表或状态对应的信息
    只填状态，返回该状态的用户
    """
    if user:
        user = str(user)
        result = await database_query(
            "SELECT status, information FROM user_status WHERE user = %s", (user,)
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
    else:
        query = "SELECT user, status FROM user_status"
        result = await database_query(query)

        matched_users = []
        for row in result:
            status_list = json.loads(row["status"]) if row["status"] else []

            if status is None:
                matched_users.append(row["user"])  # 全部用户
            elif status in status_list:
                matched_users.append(row["user"])  # 匹配状态的用户

        return matched_users


async def status_add(user, status, information="无信息"):
    """添加用户状态，自动同步到各平台"""
    user = str(user)
    if status in ["qq", "LR232", "WECHAT", "BILI", "QQAPP"]:
        await status_edit(user, status, information)
        return

    qq = await status_check(user, "qq")
    if not qq:  # 不存在 qq 状态，则为 LR5921 或其他未绑定账号
        qq = user
    bind_list = [qq]
    for platform in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        bind_id = await status_check(qq, platform)
        if bind_id:
            bind_list.append(bind_id)
    for bind_source in bind_list:
        await status_edit(bind_source, status, information)


async def status_delete(user, status):
    """删除状态，自动同步到各平台"""
    user = str(user)
    if status in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        bind_user = await status_check(user, status)
        await status_edit(user, status, None)
        await status_edit(bind_user, "qq", None)
        return
    elif status == "qq":
        bind_user = await status_check(user, status)
        for platform in ["LR232", "WECHAT", "BILI", "QQAPP"]:
            bind_id = await status_check(bind_user, platform)
            if bind_id == user:
                await status_edit(bind_user, platform, None)

    qq = await status_check(user, "qq")
    if not qq:
        qq = user
    bind_list = [qq]
    for platform in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        bind_id = await status_check(qq, platform)
        if bind_id:
            bind_list.append(bind_id)
    for bind_source in bind_list:
        await status_edit(bind_source, status, None)


async def status_edit(user, status, information=None):
    """添加/更新/删除用户状态"""
    if not user:
        return
    user = str(user)
    result = await database_query(
        "SELECT status, information FROM user_status WHERE user = %s", (user,)
    )

    if result:
        current_status = json.loads(result[0]["status"]) if result[0]["status"] else []
        current_info = (
            json.loads(result[0]["information"]) if result[0]["information"] else []
        )
        if len(current_status) != len(current_info):
            min_len = min(len(current_status), len(current_info))
            current_status = current_status[:min_len]
            current_info = current_info[:min_len]
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
        await database_update(
            """
                INSERT INTO user_status (user, status, information)
                VALUES (%s, %s, %s) AS new_val
                ON DUPLICATE KEY UPDATE
                    status = new_val.status,
                    information = new_val.information
                """,
            (
                user,
                json.dumps(current_status),
                json.dumps(current_info),
            ),
        )
    else:  # 如果状态已清空，删除记录
        await database_update("DELETE FROM user_status WHERE user = %s", (user,))
