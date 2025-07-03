import os
import asyncio
import datetime
import subprocess
from pathlib import Path

# ==== 基础配置 ====
MYSQL_CONTAINER = "mysql"
MYSQL_DB = "lrobot_data"
MYSQL_USER = "weibu"
MONGO_CONTAINER = "mongodb"
MONGO_DB = "lrobot_log"

# 本地备份路径（宿主机路径）
MYSQL_BACKUP_PATH = "./storage/data/backup"
MONGO_BACKUP_PATH = "./storage/data/backup"

# 容器内路径（MongoDB 恢复时的挂载目录）
MONGO_CONTAINER_PATH = "/data/backup"

# === 配置路径 ===
# 宿主机路径（你执行脚本的位置）
BACKUP_BASE = "./storage/data/backup"
MYSQL_BACKUP_FILE = lambda date: f"{BACKUP_BASE}/mysql_{date}.sql"
MONGO_BACKUP_DIR  = lambda date: f"{BACKUP_BASE}/mongo_{date}"

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

# MySQL 恢复
def restore_mysql_from(local_path: str):
    print(f"[MySQL] 恢复：{local_path}")
    if not os.path.exists(local_path):
        print("[MySQL] 文件不存在")
        return
    # 使用 cat + docker exec 管道方式恢复
    cmd = f"type \"{local_path}\" | docker exec -i mysql mysql -u root lrobot_data" if os.name == "nt" \
        else f"cat \"{local_path}\" | docker exec -i mysql mysql -u root lrobot_data"
    ret = subprocess.call(cmd, shell=True)
    print("[MySQL] 恢复完成" if ret == 0 else "[MySQL] 恢复失败")

# MongoDB 恢复
def restore_mongo_from(local_folder: str):
    print(f"[MongoDB] 恢复：{local_folder}")
    if not os.path.exists(local_folder):
        print("[MongoDB] 文件夹不存在")
        return
    # 转换为 mongodb 容器内路径
    folder_name = Path(local_folder).name
    # /data/backup 是 mongodb 容器内挂载目录
    container_path = f"/data/backup/{folder_name}"
    cmd = f'docker exec -i mongodb mongorestore --drop --dir="{container_path}"'
    ret = subprocess.call(cmd, shell=True)
    print("[MongoDB] 恢复完成" if ret == 0 else "[MongoDB] 恢复失败")

# 备份测试脚本

# if __name__ == "__main__":
#     asyncio.run(backup_mysql())
#     asyncio.run(backup_mongo())

# 以下为恢复脚本
if __name__ == "__main__":
    # 日期格式备份文件（可根据实际指定）
    date_str = datetime.datetime.today().strftime("%Y-%m-%d")
    mysql_file = MYSQL_BACKUP_FILE(date_str)
    mongo_dir = MONGO_BACKUP_DIR(date_str)
    restore_mysql_from(mysql_file)
    restore_mongo_from(mongo_dir)