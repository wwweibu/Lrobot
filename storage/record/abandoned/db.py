# 测试数据库连接
# 把下面两行代码放在 logic/data/database.py 的第 55 行 try 的下面
# await asyncio.sleep(10)
# print(1)
import asyncio
from logic import execute_update, execute_query, db_manager


async def db_test():
    """测试连接池是否生效"""
    await db_manager.initialize()
    try:
        # 清空测试数据
        await execute_update("UPDATE users_status SET qq_number = NULL", ())

        # 并发写入测试
        queries = [
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("123", 1)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("456", 2)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("789", 3)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("987", 4)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("654", 5)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("321", 6)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("777", 7)),
            ("UPDATE users_status SET qq_number = ? WHERE id = ?", ("888", 8)),
        ]
        tasks = [execute_update(q, p) for q, p in queries]
        update_counts = await asyncio.gather(*tasks)
        print(f"更新影响行数: {update_counts}")

        # 验证查询测试
        result = await execute_query(
            "SELECT id, qq_number FROM users_status WHERE id IN (1,2,3,4,5,6)"
        )
        print("查询结果:", result)

        return result  # 返回结果供进一步验证
    finally:
        await db_manager.close()


asyncio.run(db_test())
