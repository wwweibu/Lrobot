# 数据库连接池及测试
import re
import asyncio
import aiosqlite
from config import path


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str, max_connections: int = 50):
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = []  # 连接池
        self.condition = asyncio.Condition()  # 用于条件同步

    async def init(self):
        """初始化连接池"""
        self.pool = [
            await aiosqlite.connect(self.db_path) for _ in range(self.max_connections)
        ]

    async def get_connection(self):
        """取出连接"""
        async with self.condition:  # 等待直到池中有可用连接
            try:
                await asyncio.wait_for(
                    self.condition.wait_for(lambda: len(self.pool) > 0), 10
                )
            except Exception as e:
                raise Exception(f"连接池异常 -> 获取连接超时 | 异常: {e}")
            return self.pool.pop(0)

    async def release_connection(self, conn):
        """释放连接"""
        async with self.condition:
            self.pool.append(conn)
            self.condition.notify()  # 通知其他等待的任务

    async def term(self):
        """清理连接池"""
        async with self.condition:
            for conn in self.pool:
                await conn.close()
            self.pool.clear()
            self.condition.notify_all()


async def query_database(query: str, params: tuple = ()):
    """查询语句"""
    conn = await db_manager.get_connection()
    cursor = None
    try:
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        raise Exception(f"查询语句异常 -> {e} | 查询: {query} | 参数: {params}")
    finally:
        if cursor:
            await cursor.close()
        await db_manager.release_connection(conn)


async def update_database(query: str, params: tuple = ()):
    """更新语句"""
    conn = await db_manager.get_connection()
    cursor = None
    try:
        cursor = await conn.execute(query, params)
        await conn.commit()
        table_match = re.search(
            r"(?:INSERT INTO|UPDATE|DELETE FROM)\s+`?(\w+)`?", query, re.IGNORECASE
        )
        if table_match:
            table_name = table_match.group(1)
            if not table_name.startswith("system"):
                from web.backend.cab.database import broadcast_db_update

                await broadcast_db_update()
        return cursor.lastrowid

    except Exception as e:
        await conn.rollback()
        raise Exception(f"更新语句异常 -> {e} | 更新: {query} | 参数: {params}")
    finally:
        if cursor:
            await cursor.close()
        await db_manager.release_connection(conn)


db_manager = DatabaseManager(db_path=path / "storage/lrobot.db")

# 下面代码为测试代码
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
