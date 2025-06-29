# TODO 更改逻辑
from config import update_database, query_database


async def add_activity(name, time, duration, location, qq, description):
    """添加活动"""
    query = """
    INSERT INTO logic_activity (name, time, duration, location, qq, description, status)
    VALUES (?, ?, ?, ?, ?, ?, '待审核')
    """
    params = (name, time, duration, location, qq, description)
    id = await update_database(query, params)

    return id


async def edit_activity(id, attribute, new_value):
    """修改活动属性"""
    valid_attributes = [
        "name",
        "time",
        "duration",
        "location",
        "qq",
        "description",
        "status",
        "type",
    ]

    if attribute not in valid_attributes:
        raise Exception(f"修改未知的活动属性{attribute}")

    query = f"UPDATE logic_activity SET {attribute} = ? WHERE id = ?"
    params = (new_value, id)
    await update_database(query, params)


async def edit_activity_all(id, name, time, duration, location, description, type, qq):
    """修改活动所有属性"""
    query = """
                UPDATE logic_activity
                SET name = ?, time = ?, duration = ?, location = ?,  
                    description = ?,  status = ?,type = ?,qq=?
                WHERE id = ?
            """
    params = (
        name,
        time,
        duration,
        location,
        description,
        "进行中",  # 从审核中变成进行中
        type,
        qq,
        id,
    )
    host = await update_database(query, params)
    return host


async def get_activity_msg_id(id):
    """活动消息 id 查询"""
    query = "SELECT id, name, time, duration, location, qq, description, status,  type FROM logic_activity WHERE msg_id = ?"
    params = (id,)
    result = await query_database(query, params)
    return result


async def get_activity_qq(qq):
    """活动主持 qq 查询"""
    query = "SELECT id, name, time, duration, location, qq, description, status,  type FROM logic_activity WHERE qq = ?"
    params = (qq,)
    result = await query_database(query, params)

    if result:
        return result[0]

    return None


async def query_activity(value: str, status_list: list):
    """动态活动查询"""
    query = """
            SELECT id, name, time, duration, location, qq, description, status, type
            FROM logic_activity
            WHERE 1=1
        """
    params = []
    if value:
        query += (
            " AND (name LIKE ? OR location LIKE ? OR host LIKE ? OR host_id LIKE ?)"
        )
        params.extend([f"%{str(value)}%"] * 4)
    if status_list:
        status = ", ".join(["?"] * len(status_list))
        query += f" AND status IN ({status})"
        params.extend(status_list)

    results = await query_database(query, params)
    return results


async def check_activity(id, type, status):
    query = "SELECT qq FROM logic_activity WHERE msg_id = ? AND status = ?"
    params = (id, "待审核")
    result = await query_database(query, params)
    if result:
        qq = result[0]["qq"]  # 获取 host_id 值
        if status == "确认":
            query = "UPDATE logic_activity SET type = ?, status = ? WHERE msg_id = ?"
            params = (type, "进行中", id)
        elif status == "修改":
            query = "UPDATE logic_activity SET type = ?, status = ? WHERE msg_id = ?"
            params = (type, "审核中", id)
        elif status == "删除":
            query = "DELETE FROM logic_activity WHERE msg_id = ?"
            params = (id,)
        else:
            raise Exception(f"未知的审核回应 -> 活动审核 | 回应: {status}")
        await update_database(query, params)
    else:
        qq = None
    return qq
