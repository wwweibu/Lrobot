"""备份相关，可单独运行"""

import sys
import asyncio
import datetime
from pathlib import Path

path = Path("/app")  # 可单独运行，不使用 config
backup_dir = path / "storage/data/backup"
backup_dir.mkdir(parents=True, exist_ok=True)


async def backup_mysql(edit=False):
    """备份 Mysql"""
    if edit:
        backup_path = backup_dir / "mysql.sql"
        cmd1 = f"mysqldump -h mysql -P 3306 -u root --no-data lrobot_data > {backup_path}"
        proc1 = await asyncio.create_subprocess_shell(cmd1)
        await proc1.communicate()
        full_tables = ["system_joke"]
        cmd2 = f"mysqldump -h mysql -P 3306 -u root lrobot_data {' '.join(full_tables)} >> {backup_path}"
        proc2 = await asyncio.create_subprocess_shell(cmd2)
        await proc2.communicate()
    else:
        date = datetime.date.today().isoformat()
        backup_path = backup_dir / f"mysql_{date}.sql"
        cmd = f"mysqldump -h mysql -P 3306 -u root lrobot_data > {backup_path}"
        proc = await asyncio.create_subprocess_shell(cmd)
        await proc.communicate()


async def backup_mongo():
    """备份 Mongodb"""
    date = datetime.date.today().isoformat()
    backup_path = backup_dir / f"mongo_{date}"
    cmd = f'mongodump --uri="mongodb://mongodb:27017/lrobot_log" --out={backup_path}'
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()


# 手动备份
if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(backup_mysql(True))
    else:
        asyncio.run(backup_mysql())
        asyncio.run(backup_mongo())
