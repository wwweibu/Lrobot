"""用户状态相关"""

import json
from datetime import datetime, timedelta

from config import database_query, database_update

PERSISTENT_STATUSES = {
    "入会1",
    "入会2",
    "收集",
    "成语接龙",
    "日记",
    "七年之约"
}

# 永不超时的状态（长时游戏/活动，状态需与外部资源生命周期绑定）
# 持久化状态天然永不过期，这里补充非持久但需要长期保留的状态
NEVER_TIMEOUT_STATUSES = {
    "成语接龙",      # 游戏进行中，可能几小时
    "海军案",        # 海军案游戏，1-3 小时
    "头衔",          # 新人入群等第一句话，可能很久才发
    "直播1", "直播2", "直播3",  # B 站直播流程，状态需与 B 站直播生命周期绑定
}

DEFAULT_TIMEOUT_SECONDS = 3600  # 默认超时 1 小时

async def id_get(platform, platform_id):
    """查或新建用户"""
    platform = platform.lower()
    rows = await database_query(f"SELECT id FROM user_platform WHERE {platform} = %s LIMIT 1", (platform_id,))
    if rows:
        return int(rows[0]["id"])
    sql = f"INSERT INTO user_platform ({platform}) VALUES (%s)"
    new_id = await database_update(sql, (platform_id,))
    return int(new_id)


def _is_never_timeout(status):
    """判断状态是否永不过期"""
    return status in PERSISTENT_STATUSES or status in NEVER_TIMEOUT_STATUSES


async def status_check(user, platform, status=None):
    """查找用户状态，返回状态列表或对应状态信息
    过期状态会自动清理并返回 None
    """
    if user is None:
        return {} if status is None else None
    user_id = await id_get(platform, user)

    if status is None:
        # 先清理该用户所有过期状态
        await _expire_clean_by_user(user_id)
        rows = await database_query("SELECT status, info FROM user_status WHERE user_id = %s", (user_id,))
        return [r["status"] for r in rows if "status" in r]

    # 单个状态查询，先检查是否过期
    rows = await database_query(
        "SELECT info, expire_at FROM user_status WHERE user_id = %s AND status = %s LIMIT 1",
        (user_id, status),
    )
    if not rows:
        return None
    expire_at = rows[0].get("expire_at")
    if expire_at and datetime.now() > expire_at:
        # 已过期，清理并返回 None
        await database_update(
            "DELETE FROM user_status WHERE user_id = %s AND status = %s",
            (user_id, status),
        )
        return None
    try:
        return json.loads(rows[0]["info"]) if rows[0]["info"] else None
    except Exception:
        return rows[0]["info"]


async def _expire_clean_by_user(user_id):
    """清理某个用户的所有过期状态"""
    now = datetime.now()
    await database_update(
        "DELETE FROM user_status WHERE user_id = %s AND expire_at IS NOT NULL AND expire_at < %s",
        (user_id, now),
    )


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
    return [r[platform] for r in rows if r.get(platform)]



async def status_add(user, platform, status, info=None, timeout=DEFAULT_TIMEOUT_SECONDS):
    """插入或更新状态
    timeout: 超时秒数，默认 3600（1 小时）；传 0 或 None 表示永不过期
    持久化状态和 NEVER_TIMEOUT_STATUSES 中的状态永不过期
    """
    user_id = await id_get(platform, user)
    info_json = json.dumps(info) if info is not None else None

    # 计算过期时间
    if _is_never_timeout(status) or not timeout:
        expire_at = None
    else:
        expire_at = datetime.now() + timedelta(seconds=timeout)

    if status not in PERSISTENT_STATUSES:  # 删除非持久性状态
        placeholders = ','.join(['%s'] * len(PERSISTENT_STATUSES))
        await database_update(
            f"DELETE FROM user_status WHERE user_id = %s AND status NOT IN ({placeholders})",
            (user_id, *PERSISTENT_STATUSES)
        )
    await database_update(
        "INSERT INTO user_status (user_id, status, info, expire_at) VALUES (%s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE info = VALUES(info), expire_at = VALUES(expire_at)",
        (user_id, status, info_json, expire_at),
    )



async def status_delete(user, platform, status):
    """删除某用户某平台的某状态"""
    user_id = await id_get(platform, user)
    await database_update("DELETE FROM user_status WHERE user_id = %s AND status = %s", (user_id, status))


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

    row_target_list = await database_query("SELECT * FROM user_platform WHERE id = %s LIMIT 1", (target_id,))
    row_source_list = await database_query("SELECT * FROM user_platform WHERE id = %s LIMIT 1", (source_id,))
    row_target = row_target_list[0]
    row_source = row_source_list[0]

    for bind_platform in ["lr5921", "lr232", "wechat", "bili"]:
        if row_target.get(bind_platform) and row_source.get(bind_platform):
            return f"绑定失败:{bind_platform}已绑定{row_source[bind_platform]}"

    # 合并状态
    source_status_list = await database_query(
        "SELECT status, info, expire_at FROM user_status WHERE user_id = %s", (source_id,)
    )
    for r in source_status_list:
        source_status = r["status"]
        source_info = r["info"]
        source_expire = r.get("expire_at")
        target_rows = await database_query(
            "SELECT info, expire_at FROM user_status WHERE user_id = %s AND status = %s LIMIT 1",
            (target_id, source_status)
        )
        if target_rows:
            merged_info = info_merge(target_rows[0]["info"], source_info)
            # 合并过期时间：取较晚者，避免一方提前过期
            target_expire = target_rows[0].get("expire_at")
            merged_expire = max(filter(None, [target_expire, source_expire]), default=None)
            await database_update(
                "UPDATE user_status SET info = %s, expire_at = %s WHERE user_id = %s AND status = %s",
                (merged_info, merged_expire, target_id, source_status)
            )
        else:
            await database_update(
                "INSERT INTO user_status (user_id, status, info, expire_at) VALUES (%s, %s, %s, %s)",
                (target_id, source_status, source_info, source_expire)
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
    if platform == "LR5921":
        return user
    platform = platform.lower()
    rows = await database_query(f"SELECT lr5921 FROM user_platform WHERE {platform} = %s LIMIT 1", (user,))
    if not rows:
        return None
    return rows[0].get("lr5921")
