# 多服务聚合
import asyncio
import subprocess
from prometheus_client import Gauge, Counter, Summary, start_http_server
from config import path, config
from log import loggers

server_logger = loggers["server"]

# exe与bat服务运行指标
SERVICE_STATUS = Gauge("service_status", "Status of the service", ["service_name"])

running_processes = {}  # 已启动服务的进程
SERVICES = {
    "xiaomiqiu": str(path.parent / "xiaomiqiu" / "xiaomiqiu.bat"),
    "windows_exporter": str(path.parent / "prometheus" / "windows_exporter.bat"),
    "prometheus": str(path.parent / "prometheus" / "prometheus.bat"),
    "promtail": str(path.parent / "loki" / "promtail.bat"),
    "loki": str(path.parent / "loki" / "loki.bat"),
    "grafana": str(path.parent / "grafana" / "grafana.bat"),
    "napcat": str(path.parent / "napcat" / "napcat.quick.bat"),
}


# 初始化 Prometheus 服务
async def Prometheus_start():
    start_http_server(5925)  # 在主线程启动 Prometheus 服务


# 启动服务
async def start_services():
    for name, path in SERVICES.items():
        if (
            name not in running_processes
            or running_processes[name].returncode is not None
        ):  # 服务未启动或已停止
            try:
                working_dir = path.parent
                process = await asyncio.create_subprocess_shell(
                    path,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                running_processes[name] = process
                SERVICE_STATUS.labels(service_name=name).set(1)
                server_logger.info(
                    f"Started {name}",
                    extra={"event": "运行日志"},
                )
                asyncio.create_task(log_service(name, process))
            except Exception as e:
                SERVICE_STATUS.labels(service_name=name).set(0)
                server_logger.error(
                    f"Failed to start {name}: {e}",
                    extra={"event": "运行日志"},
                )


# 启动日志记录
async def log_service(service_name, process):
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        server_logger.info(
            line.decode("utf-8").strip(),
            extra={"event": service_name},
        )
    await process.wait()
    server_logger.error(
        f"Service {service_name} has stopped.",
        extra={"event": "运行日志"},
    )


# 监控服务函数
async def monitor_services():
    while True:
        for name, process in list(running_processes.items()):
            if process.returncode is not None:  # 服务已停止
                SERVICE_STATUS.labels(service_name=name).set(0)
                running_processes.pop(name)
                server_logger.error(
                    f"Service {name} has stopped.",
                    extra={"event": "运行日志"},
                )
            else:
                SERVICE_STATUS.labels(service_name=name).set(1)
        await asyncio.sleep(60)


# 停止服务函数
async def stop_services():
    for name, process in running_processes.items():
        try:
            pid = process.pid
            await asyncio.create_subprocess_exec("taskkill", "/F", "/PID", str(pid))
            SERVICE_STATUS.labels(service_name=name).set(0)
            server_logger.info(
                f"Stopped {name}",
                extra={"event": "运行日志"},
            )
        except Exception as e:
            error_message = f"Failed to stop service: {e}"
            SERVICE_STATUS.labels(service_name=name).set(0)
            server_logger.error(
                f"Failed to stop {name}: {error_message}",
                extra={"event": "运行日志"},
            )


# 需要把下面的部分整合至 log.py,输出符合 loki 格式的日志
# 正则表达式定义
LOG_FORMATS = {
    "xiaomiqiu": r"\[(?P<level>.*?)\]\t(?P<file_path>.*?)\t(?P<info>.*)",
    "windows_exporter": r"level=(?P<level>[^ ]+).*?msg=(?P<info>.*)",
    "prometheus": r"level=(?P<level>[^ ]+).*?msg=(?P<info>.*)",
    "promtail": r"level=(?P<level>[^ ]+).*?msg=(?P<info>.*)",
    "loki": r"level=(?P<level>[^ ]+).*?caller=[^ ]+ (?P<info>.*)",
    "grafana": r"level=(?P<level>[^ ]+).*?msg=(?P<info>.*)",
    "napcat": r"\[(\u001b\[\d+m(?P<level>[^\u001b]+)\u001b\[39m)\] (?P<info>.*)",
}


class ServerFilter(logging.Filter):
    """各 server 的日志过滤器"""

    def filter(self, record):
        if not record.getMessage():
            return False
        service = getattr(record, "event", "")
        if "debug1" in record.getMessage():
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
            record.msg = record.msg.replace("debug1:", "").strip()  # 去掉 debug1: 前缀
        # 更改掉xiaomiqiu以error开头的日志
        if service == "xiaomiqiu" and record.getMessage().startswith("Error"):
            record.levelname = "ERROR"
        # 设置bat中激活utf-8的日志，以及napcat以[]开头的日志为DEBUG
        if record.getMessage() == "Active code page: 65001" or (
            service == "napcat"
            and record.getMessage().startswith("[")
            and not record.getMessage().startswith("[NapCat Backend]")
        ):
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
        if service in LOG_FORMATS:
            pattern = LOG_FORMATS[service]
            match = re.search(pattern, record.getMessage())
            if match:
                record.levelname = match.group("level").upper()  # 设置为 DEBUG 级别
                record.msg = match.group("info")
        record.levelno = getattr(logging, record.levelname, logging.INFO)

        record.msg = json.dumps(
            {
                "level": record.levelname,
                "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "service": service,
                "message": record.msg,
            },
            ensure_ascii=False,
        )

        return True


class AdapterFilter(logging.Filter):
    """机器人日志过滤器"""

    EVENT_TO_LEVEL = {
        # "事件名称": "日志级别"
        # 例如： "error_event": "ERROR"
    }

    def filter(self, record):
        # 处理事件日志级别
        event = getattr(record, "event", "")
        log_level = self.EVENT_TO_LEVEL.get(event, "INFO").upper()

        record.levelname = log_level
        record.levelno = getattr(logging, log_level, logging.INFO)

        # 统一日志格式
        record.msg = json.dumps(
            {
                "level": record.levelname,
                "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "robot": getattr(record, "robot", ""),
                "event": event,
                "command": getattr(record, "command", ""),
                "target": getattr(record, "target", ""),
                "message": record.getMessage(),
            },
            ensure_ascii=False,
        )

        return True
