"""系统数据相关"""
from config import database_update, database_query


async def system_edit(name, text):
    """修改数据"""
    query = """
            INSERT INTO system_data (name, text)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE text = VALUES(text)
        """
    await database_update(query, (name, text))


async def system_get(name):
    """获取数据"""
    query = "SELECT text FROM system_data WHERE name = %s"
    result = await database_query(query, (name,))
    if result:
        return result[0]["text"]
    return None
