"""物资修改"""

from config import database_update, database_query


async def material_add(name, num):
    """物资添加"""
    query = """
           INSERT INTO user_material (name, num)
           VALUES (%s, %s) AS new
           ON DUPLICATE KEY UPDATE num = new.num
       """
    await database_update(query, (name, num))


async def material_get():
    """物资查询"""
    query = "SELECT name, num FROM user_material"
    results = await database_query(query)

    if not results:
        return "当前没有物资记录"

    # 格式化输出
    materials = [f"{item['name']}:{item['num']}" for item in results]
    return "\n".join(materials)
