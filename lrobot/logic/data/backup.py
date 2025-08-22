"""备份相关，可单独运行"""

import asyncio
import datetime
from pathlib import Path

path = Path("/app")  # 可单独运行，不使用 config
backup_dir = path / "storage/data/backup"
backup_dir.mkdir(parents=True, exist_ok=True)

async def backup_mysql():
    """备份 Mysql"""
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
    asyncio.run(backup_mysql())
    asyncio.run(backup_mongo())
