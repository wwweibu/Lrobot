"""用户状态相关"""

import json

from config import database_query, database_update


async def id_get(platform, platform_id):
    """查或新建用户"""
    platform = platform.lower()
    rows = await database_query(f"SELECT id FROM user_platform WHERE {platform} = %s LIMIT 1", (platform_id,))
    if rows:
        return int(rows[0]["id"])
    sql = f"INSERT INTO user_platform ({platform}) VALUES (%s)"
    new_id = await database_update(sql, (platform_id,))
    return int(new_id)


async def status_check(user, platform, status=None):
    """查找用户状态，返回状态列表或对应状态信息"""
    if user is None:
        return {} if status is None else None
    user_id = await id_get(platform, user)

    if status is None:
        rows = await database_query("SELECT status, info FROM user_status WHERE user_id = %s", (user_id,))
        return [r["status"] for r in rows if "status" in r]

    rows = await database_query("SELECT info FROM user_status WHERE user_id = %s AND status = %s LIMIT 1",
                                (user_id, status))
    if not rows:
        return None
    try:
        return json.loads(rows[0]["info"]) if rows[0]["info"] else None
    except Exception:
        return rows[0]["info"]


async def status_user_check(platform, status):
    """查找某个状态在某个平台上的所有用户"""
    rows = await database_query("SELECT DISTINCT user_id FROM user_status WHERE status = %s", (status,))
    user_ids = [int(r["user_id"]) for r in rows]
    if not user_ids:
        return []

    platform = platform.lower()
    placeholders = ",".join(["%s"] * len(user_ids))
    q = f"SELECT id, {platform} FROM user_platform WHERE id IN ({placeholders})"
    rows = await database_query(q, tuple(user_ids))
    return [r["id"] for r in rows if r.get(platform)]



async def status_add(user, platform, status, info=None):
    """插入或更新状态"""
    user_id = await id_get(platform, user)
    info_json = json.dumps(info) if info is not None else None
    await database_update(
        "INSERT INTO user_status (user_id, status, info) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE info = VALUES(info)",
        (user_id, status, info_json),
    )


async def status_delete(user, platform, status):
    """删除某用户某平台的某状态"""
    user_id = await id_get(platform, user)
    await database_update("DELETE FROM user_status WHERE user_id = %s AND status = %s", (user_id, status))
    rows = await database_query("SELECT 1 FROM user_status WHERE user_id = %s LIMIT 1", (user_id,))
    if not rows:  # 该用户无状态
        await database_update("DELETE FROM user_platform WHERE id = %s", (user_id,))


def info_merge(info1, info2):
    """合并 info"""
    if info1 is None and info2 is None:
        return None
    if info1 is None:
        return info2
    if info2 is None:
        return info1
    try:
        v1 = int(info1)
        v2 = int(info2)
        return json.dumps(max(v1, v2))
    except Exception:
        return info1


async def status_platform_bind(qq, platform, platform_id):
    """绑定平台"""
    if platform == "LR5921":
        return "绑定失败:平台错误"

    target_id = await id_get("LR5921", qq)
    source_id = await id_get(platform, platform_id)
    if target_id == source_id:
        return "绑定失败:已绑定"

    rows = await database_query(
        "SELECT * FROM user_platform WHERE id IN (%s, %s)",
        (target_id, source_id)
    )
    if len(rows) < 2:
        return "绑定失败:系统异常"

    row_target = next(r for r in rows if r["id"] == target_id)
    row_source = next(r for r in rows if r["id"] == source_id)

    for bind_platform in ["lr5921", "lr232", "wechat", "bili"]:
        if row_target.get(bind_platform) and row_source.get(bind_platform):
            return f"绑定失败:{bind_platform}已绑定{row_source[bind_platform]}"

    # 合并状态
    source_status_list = await database_query("SELECT status, info FROM user_status WHERE user_id = %s", (source_id,))
    for r in source_status_list:
        source_status = r["status"]
        source_info = r["info"]
        target_rows = await database_query(
            "SELECT info FROM user_status WHERE user_id = %s AND status = %s LIMIT 1",
            (target_id, source_status)
        )
        if target_rows:
            merged_info = info_merge(target_rows[0]["info"], source_info)
            await database_update(
                "UPDATE user_status SET info = %s WHERE user_id = %s AND status = %s",
                (merged_info, target_id, source_status)
            )
        else:
            await database_update(
                "INSERT INTO user_status (user_id, status, info) VALUES (%s, %s, %s)",
                (target_id, source_status, source_info)
            )

    await database_update("DELETE FROM user_platform WHERE id = %s", (source_id,))
    await database_update("DELETE FROM user_status WHERE user_id = %s", (source_id,))

    # 合并平台
    updates = []
    params = []
    for bind_platform in ["lr5921", "lr232", "wechat", "bili"]:
        if not row_target.get(bind_platform) and row_source.get(bind_platform):
            updates.append(f"{bind_platform} = %s")
            params.append(row_source[bind_platform])
    if updates:
        sql = f"UPDATE user_platform SET {', '.join(updates)} WHERE id = %s"
        params.append(target_id)
        await database_update(sql, tuple(params))

    return "绑定成功"


async def status_lr5921_get(user, platform):
    """查找是否有 lr5921 平台"""
    platform = platform.lower()
    rows = await database_query(f"SELECT lr5921 FROM user_platform WHERE {platform} = %s LIMIT 1", (user,))
    if not rows:
        return None
    return rows[0].get("lr5921")
