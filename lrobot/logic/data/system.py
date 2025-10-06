"""系统数据相关"""

import re

from config import database_update, database_query, loggers


async def system_edit(name, text):
    """修改数据"""
    query = """
        INSERT INTO system_data (name, text)
        VALUES (%s, %s) AS new
        ON DUPLICATE KEY UPDATE text = new.text
    """
    await database_update(query, (name, text))


async def system_get(name):
    """获取数据"""
    query = "SELECT text FROM system_data WHERE name = %s"
    result = await database_query(query, (name,))
    if result:
        return result[0]["text"]
    return None


async def system_command_add(source, user, platform, content, result):
    """添加指令记录"""
    if result is not None and re.match(r"success-chunk \d+ uploaded", result):
        return

    sql = """
          INSERT INTO system_command
          (command, user, platform, recv_content,send_content)
          VALUES (%s, %s, %s, %s, %s)
       """
    loggers["message"].info(f"[{source}]⌈{platform}⌋{user}-> {content}: {result}",
                            extra={"event": "消息分析"})
    await database_update(sql, (source, user, platform, content, result))
