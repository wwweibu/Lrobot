"""运行命令行指令"""

import sys
import asyncio
import subprocess

from config import config, path, loggers, log_writer

pem_path = path / "storage" / "lrobot.pem"
ip = config["SERVER_IP"]
username = config["SERVER_USERNAME"]


async def ssh_clean():
    """清除服务器的 10000 端口残留服务"""
    script = "echo '端口占用情况:'; sudo lsof -i:10000; sudo fuser -k 10000/tcp;sudo lsof -i:10000;"
    clean_ssh_command = (
        f'ssh -i {pem_path} {username}@{ip} '
        f'-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
        f'"{script}"'
    )
    await command_run(clean_ssh_command, loggers["server"])

async def ssh_run():
    """运行 ssh 连接"""
    ssh_command = (f"ssh -i {pem_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
                   f"-C -v -N -D 0.0.0.0:5923 -R 10000:lrobot:5922 {username}@{ip}")
    await command_run(ssh_command, loggers["server"])



async def napcat_run():
    """命令行运行 napcat，已被 docker 替代"""
    napcat_path = path / "NapCat.Shell" / "NapCatWinBootMain.exe"  # napcat 路径
    qq = config["LR5921_ID"]
    napcat_command = f"{napcat_path} {qq}"
    await command_run(napcat_command, loggers["adapter"])


async def xiaomiqiu_run():
    """运行小米球，已被 ssh+服务器 替代"""
    xiaomiqiu_path = path / "xiaomiqiu" / "xiaomiqiu.exe"
    xiaomiqiu_config = path / "xiaomiqiu" / "xiaomiqiu.conf"
    xiaomiqiu_command = f"{xiaomiqiu_path} -config {xiaomiqiu_config} -log=stdout -log-level=info start-all"
    await command_run(xiaomiqiu_command, loggers["server"])


async def command_run(command, logger=None):
    """运行指令"""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,  # 捕获标准输出
        stderr=subprocess.STDOUT,  # 标准错误输出重定向到标准输出
    )

    try:
        async for line in process.stdout:
            output = line.decode().strip()
            if logger:  # 使用传入的日志处理器输出日志
                logger.info(output, extra={"event": "运行日志"})
            sys.stdout.flush()  # 强制刷新输出
    finally:
        # 退出时处理剩余输出
        remaining_output, _ = await process.communicate()
        if remaining_output and logger:
            for line in remaining_output.decode().split("\n"):
                logger.info(line.strip(), extra={"event": "运行日志"})


async def main():
    """主函数"""
    try:
        await ssh_clean()
        await asyncio.sleep(3)
        await asyncio.gather(log_writer(), ssh_run())
    except Exception as e:
        loggers["server"].error(f"[服务器]{e}", extra={"event": "运行失败"})

if __name__ == "__main__":
    asyncio.run(main())
