"""运行命令行指令"""
import sys
import time
import asyncio
import subprocess

from config import config, path, loggers, log_writer

pem_path = path / "storage" / "lrobot.pem"
ip = config["SERVER_IP"]
username = config["SERVER_USERNAME"]
napcat_path = path / "NapCat.Shell" / "NapCatWinBootMain.exe"
qq = config["LR5921_ID"]
xiaomiqiu_path = path / "xiaomiqiu" / "xiaomiqiu.exe"
xiaomiqiu_config = path / "xiaomiqiu" / "xiaomiqiu.conf"


async def ssh_clean():
    """清除服务器的 10000 端口残留服务"""
    clean_ssh_command = f'ssh -i {pem_path} {username}@{ip} "sudo lsof -t -i:10000 | xargs -r sudo kill -9"'
    await command_run(clean_ssh_command, loggers["server"])


async def ssh_run():
    """运行 ssh 连接"""
    time.sleep(3)  # 等待清理完成
    ssh_command = f"ssh -i {pem_path} -C -v -N -D 0.0.0.0:5923 -R 10000:lrobot:5922 {username}@{ip}"
    await command_run(ssh_command, loggers["server"])


async def napcat_run():
    """运行 napcat，已被 docker 指令替代"""
    napcat_command = f"{napcat_path} {qq}"
    await command_run(napcat_command, loggers["adapter"])


async def xiaomiqiu_run():
    """运行小米球"""
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
            # 检测 SSH 断开并重新连接
            if (
                    "closed by" in output
                    or "remote port forwarding failed" in output
            ):
                if logger:
                    logger.error(
                        "检测到连接关闭，正在重新启动...",
                        extra={"event": "运行日志"},
                    )
                    sys.exit(1)
    finally:
        # 退出时处理剩余输出
        remaining_output, _ = await process.communicate()
        if remaining_output:
            for line in remaining_output.decode().split("\n"):
                output = line.strip()
                if logger:
                    logger.info(output, extra={"event": "运行日志"})


async def main():
    """主函数"""
    await asyncio.gather(log_writer(), ssh_clean(), ssh_run())


if __name__ == "__main__":
    asyncio.run(main())
