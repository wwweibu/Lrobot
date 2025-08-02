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
    if status == "qq":
        await status_edit(user, status, information)
        return
    elif status in ["LR232", "WECHAT", "BILI", "QQAPP"]:
        await status_edit(user, status, information)

        def extract_base_and_merged(result):
            """分离绑定状态与其他状态"""
            base_status, base_info, merged_status, merged_info = [], [], [], []
            if result:
                s_list = json.loads(result[0]["status"]) or []
                i_list = json.loads(result[0]["information"]) or []
                for s, i in zip(s_list, i_list):
                    if s in ["qq", "LR232", "WECHAT", "BILI", "QQAPP"]:
                        base_status.append(s)
                        base_info.append(i)
                    else:
                        merged_status.append(s)
                        merged_info.append(i)
            return base_status, base_info, merged_status, merged_info

        # 此处进行平台绑定状态合并
        qq_result = await database_query(
            "SELECT status, information FROM user_status WHERE user = %s", (user,)
        )
        platform_result = await database_query(
            "SELECT status, information FROM user_status WHERE user = %s", (str(information),)
        )
        qq_status, qq_info, status_1, info_1 = extract_base_and_merged(qq_result)
        platform_status, platform_info, status_2, info_2 = extract_base_and_merged(platform_result)

        for s, i in zip(status_2, info_2):
            if s not in status_1:
                status_1.append(s)
                info_1.append(i)

        write_data = [
            (user, qq_status, qq_info),
            (str(information), platform_status, platform_info),
        ]

        for idx, platform in enumerate(qq_status):
            # 同步已绑定平台状态
            write_data.append((qq_info[idx], platform_status, platform_info))

        for u, base_status, base_info in write_data:
            final_status = base_status + status_1
            final_info = base_info + info_1

            await database_update(
                """
                INSERT INTO user_status (user, status, information)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    information = VALUES(information)
                """,
                (
                    u,
                    json.dumps(final_status),
                    json.dumps(final_info),
                ),
            )

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
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                information = VALUES(information)
            """,
            (
                user,
                json.dumps(current_status),
                json.dumps(current_info),
            ),
        )
    else:  # 如果状态已清空，删除记录
        await database_update("DELETE FROM user_status WHERE user = %s", (user,))
