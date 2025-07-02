# TODO 定时检查
import os
import time
import psutil
import aiohttp
import tracemalloc
from datetime import datetime, timedelta
from config import loggers,update_database,connect

system_logger = loggers["system"]


async def network_check():
    """检查网站能否访问"""
    url = "https://whumystery.cn/test"
    client = connect()
    response = await client.get(url)
    if response.status != 200:
        raise Exception("网站异常 -> 状态码{response.status}")
    text = await response.text()
    if text.strip() == "Hello World!":
        system_logger.info("网站连接正常", extra={"event": "定时任务"})
        return


_last_net = None
_last_time = None


async def system_check():
    """统计系统属性"""
    # 上传下载网速 /Mbps
    global _last_net, _last_time
    current_net = psutil.net_io_counters()
    current_time = time.time()

    if _last_time is None:
        _last_net = current_net
        _last_time = current_time
        upload, download = 0.0, 0.0
    else:
        interval = current_time - _last_time

        upload = (
            (current_net.bytes_sent - _last_net.bytes_sent) * 8 / 1e6 / interval
        )  # Mbps
        download = (current_net.bytes_recv - _last_net.bytes_recv) * 8 / 1e6 / interval
        _last_net = current_net
        _last_time = current_time

    # python 总内存分配 /MB
    snapshot = tracemalloc.take_snapshot()
    total_tracemalloc = (
        sum(stat.size for stat in snapshot.statistics("filename")) / 1024 / 1024
    )

    # 当前 Python 进程的内存占用（RSS） /MB
    process = psutil.Process(os.getpid())
    process_mem = (
        process.memory_info().rss / 1024 / 1024
    )  # 常驻内存（Resident Set Size）

    # 系统内存占用、总内存 /MB
    system_mem = psutil.virtual_memory()
    system_used = system_mem.used / 1024 / 1024
    system_total = system_mem.total / 1024 / 1024

    now = datetime.utcnow() + timedelta(hours=8)
    now_str = now.isoformat()
    query = "INSERT INTO system_metrics (timestamp, trace_mb, process_mb, used_mb, total_mb,upload_mbps, download_mbps) VALUES (?, ?, ?, ?, ?, ?, ?)"
    params = (
        now_str,
        round(total_tracemalloc, 2),
        round(process_mem, 2),
        round(system_used, 2),
        round(system_total, 2),
        round(upload, 2),
        round(download, 2),
    )
    await update_database(query, params)
