import os
import asyncio
import datetime

async def backup_mysql():
    """备份sql"""
    date = datetime.date.today().isoformat()
    backup_dir = "/app/storage/backup"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = f"/app/storage/backup/mysql_{date}.sql"
    cmd = f"mysqldump -h mysql -P 3306 -u root lrobot_data > {backup_path}"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()


async def backup_mongo():
    date = datetime.date.today().isoformat()
    backup_dir = "/app/storage/backup"
    os.makedirs(backup_dir, exist_ok=True)
    out_path = f"/app/storage/backup/mongo_{date}"
    cmd = f'mongodump --uri="mongodb://mongodb:27017/lrobot_log" --out={out_path}'
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()


# 备份测试脚本

if __name__ == "__main__":
    asyncio.run(backup_mysql())
    asyncio.run(backup_mongo())

