"""基本的配置及常量"""
# 包含：全局路径、代理连接、future 变量、消息处理监控、进程池任务、定时任务、配置信息读写、日志记录器、数据库写入查询操作
# 需要使用 mysql 数据库引入 mysql_init；日志写入需要 gather log_writer；配置自动更新需要 gather config_watcher
import re
import os
import sys
import json
import time
import yaml
import httpx
import asyncio
import hashlib
import logging
import aiomysql
import datetime
import traceback
from collections import OrderedDict
from pathlib import Path
import motor.motor_asyncio
from functools import wraps
from colorama import Fore, Style
from logging.config import dictConfig
from contextlib import asynccontextmanager
from httpx_socks import AsyncProxyTransport
from concurrent.futures import ProcessPoolExecutor
from watchdog.events import FileSystemEventHandler
from watchdog.observers.inotify import InotifyObserver
from watchdog.observers.polling import PollingObserver

# 颜色匹配
COLOR_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
# napcat 日志匹配
NAPCAT_PATTERN = re.compile(
    r"\[(\u001b\[\d+m(?P<level>[^\u001b]+)\u001b\[39m)] (?P<info>.*)"
)
# 颜色设置
COLORS = {
    logging.DEBUG: Fore.YELLOW,  # 黄色
    logging.INFO: Fore.BLACK,  # 黑色
    logging.WARNING: Fore.RED,  # 红色
    logging.ERROR: Fore.RED,  # 红色
}
# 日志来源替换映射
SOURCE_DICT = {
    "system": "system ",
    "server": "server ",
    "uvicorn": "website",
    "uvicorn.access": "website",
    "uvicorn.error": "website",
    "napcat": "napcat "
}
# 监视器统计数据
MONITOR_METRICS = {}
path = Path(__file__).resolve().parent  # 全局路径,python 中为 /lrobot,dokcer 中为 /app
mongo_client = None  # mongo 连接
mongo_db = None
mysql_db_pool = None  # mysql 连接
LOG_QUEUE_MAX = max(100, int(os.getenv("LROBOT_LOG_QUEUE_MAX", "2000")))
LOG_MESSAGE_MAX_CHARS = max(1000, int(os.getenv("LROBOT_LOG_MESSAGE_MAX_CHARS", "65536")))
BACKGROUND_TASK_MAX = max(10, int(os.getenv("LROBOT_BACKGROUND_TASK_MAX", "1000")))
FUTURE_EARLY_RESULT_MAX = max(10, int(os.getenv("LROBOT_FUTURE_EARLY_MAX", "1000")))
FUTURE_EARLY_RESULT_TTL = max(1.0, float(os.getenv("LROBOT_FUTURE_EARLY_TTL", "60")))

log_queue = asyncio.Queue(maxsize=LOG_QUEUE_MAX)  # 有界日志队列
loggers = {}  # 日志记录器
temp_key = {}  # 网址临时密钥
process_pool = ProcessPoolExecutor()  # 进程池
RUNTIME_METRICS = {
    "future_early_evicted": 0,
    "log_dropped": 0,
    "log_evicted": 0,
    "log_truncated": 0,
    "background_task_rejected": 0,
}
_background_tasks = set()
_last_log_drop_report = 0.0

class FutureManager:
    """管理协程回调，并对已消费/超时/早到结果做有界回收。"""

    def __init__(self, early_ttl=FUTURE_EARLY_RESULT_TTL, early_max=FUTURE_EARLY_RESULT_MAX):
        self._futures = {}  # 只保留正在等待的 Future
        self._early_results = OrderedDict()  # key -> (expires_at, is_error, value)
        self._early_ttl = early_ttl
        self._early_max = early_max
        self._loop = None  # 主事件循环

    def init(self, loop):
        """传入主事件循环"""
        self._loop = loop

    def get(self, key):
        """获取等待对象；若结果早到，将其一次性转入 Future。"""
        if self._loop is None:
            raise RuntimeError("[future]主事件循环尚未初始化")
        self._purge_early()
        if key not in self._futures:
            future_obj = self._loop.create_future()
            early = self._early_results.pop(key, None)
            if early:
                _, is_error, value = early
                if is_error:
                    future_obj.set_exception(value)
                else:
                    future_obj.set_result(value)
            self._futures[key] = future_obj
        return self._futures[key]

    def set(self, key, result):
        """设置结果；无等待者时只保留有 TTL 的早到结果。"""
        return self._schedule_resolve(key, result, is_error=False)

    def set_exception(self, key, error):
        """让等待者立即收到异常，同样支持先到回调。"""
        if not isinstance(error, BaseException):
            error = RuntimeError(str(error))
        return self._schedule_resolve(key, error, is_error=True)

    def _schedule_resolve(self, key, value, is_error):
        if self._loop is None or self._loop.is_closed():
            return False
        try:
            if asyncio.get_running_loop() is self._loop:
                self._resolve(key, value, is_error)
                return True
        except RuntimeError:
            pass
        try:
            self._loop.call_soon_threadsafe(self._resolve, key, value, is_error)
            return True
        except RuntimeError:
            return False

    def _resolve(self, key, value, is_error):
        self._purge_early()
        future_obj = self._futures.get(key)
        if future_obj is not None:
            if not future_obj.done():
                if is_error:
                    future_obj.set_exception(value)
                else:
                    future_obj.set_result(value)
            return

        self._early_results[key] = (
            time.monotonic() + self._early_ttl,
            is_error,
            value,
        )
        self._early_results.move_to_end(key)
        while len(self._early_results) > self._early_max:
            self._early_results.popitem(last=False)
            RUNTIME_METRICS["future_early_evicted"] += 1

    def _purge_early(self):
        now = time.monotonic()
        while self._early_results:
            first_key = next(iter(self._early_results))
            if self._early_results[first_key][0] > now:
                break
            self._early_results.popitem(last=False)

    async def wait(self, key, err_msg=None, timeout=20):
        """等待 Future 结果并保证移除该 key。"""
        future_obj = self.get(key)
        try:
            return await asyncio.wait_for(asyncio.shield(future_obj), timeout=timeout)
        except asyncio.TimeoutError as error:
            raise TimeoutError(
                err_msg or f"[future]请求失败-> {key} 获取超时: {timeout}s"
            ) from error
        finally:
            if self._futures.get(key) is future_obj:
                self._futures.pop(key, None)
            if not future_obj.done():
                future_obj.cancel()

    def clear(self):
        """关闭时取消所有等待并丢弃早到结果。"""
        for future_obj in self._futures.values():
            if not future_obj.done():
                future_obj.cancel()
        self._futures.clear()
        self._early_results.clear()

    def stats(self):
        """返回可用于运行观察的当前数量。"""
        self._purge_early()
        return {
            "pending": len(self._futures),
            "early": len(self._early_results),
            "early_evicted": RUNTIME_METRICS["future_early_evicted"],
        }


def create_background_task(coro, *, name=None):
    """创建可追踪、有数量上限的后台任务。"""
    if len(_background_tasks) >= BACKGROUND_TASK_MAX:
        RUNTIME_METRICS["background_task_rejected"] += 1
        close = getattr(coro, "close", None)
        if close:
            close()
        return None

    task = asyncio.create_task(coro, name=name)
    _background_tasks.add(task)

    def _done(completed):
        _background_tasks.discard(completed)
        if completed.cancelled():
            return
        try:
            error = completed.exception()
        except asyncio.CancelledError:
            return
        if error and loggers.get("system"):
            loggers["system"].error(
                f"[后台任务]{completed.get_name()} 异常-> {type(error).__name__}: {error}",
                extra={"event": "运行失败"},
            )

    task.add_done_callback(_done)
    return task


async def cancel_background_tasks():
    """取消并等待本进程中受管的后台任务。"""
    tasks = list(_background_tasks)
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

class SafeDict(dict):
    """支持多层嵌套访问的字典，访问不存在的键时返回空 safe_dict 而非抛异常"""

    def __getitem__(self, key):
        return super().get(key, SafeDict())

    def get(self, key, default=None):
        """获取值"""
        return super().get(key, default if default is not None else SafeDict())


class AutoConfig:
    """配置参数读写"""

    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._config = {}
        self._config_sources = {}  # 记录每个 key 来自哪个文件
        self._config_hashes = {}  # 文件哈希，避免重复加载
        self._storage = {}  # 数据持久化存储
        self._log_hash = None  # 日志记录器哈希值
        self.config_load()

    def __setitem__(self, key, value):
        """自动写回 YAML"""
        if key not in self._config_sources:
            raise Exception(f"[配置数据]写入失败-> 配置项 {key} 不存在，无法确定其来源文件")

        file_path = self._config_sources[key]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            data[key] = value
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True,sort_keys=False)
            self._config[key] = value  # 同步更新内存中的值
            self._config_hashes[file_path] = file_hash_get(file_path)  # 更新哈希值
        except Exception as e:
            raise Exception(f"[配置数据]写入失败-> 配置项: {key} | 文件: {file_path.name} | 错误: {e}")

    def __getitem__(self, key):
        """实现多层访问"""
        value = self._config.get(key, {})
        if isinstance(value, dict):
            return SafeDict(value)
        return value

    def __str__(self):
        """返回配置的字符串，用于打印"""
        return f"config: {self._config}"

    def __contains__(self, key):
        """重载字典的 __contains__ 方法"""
        return key in self._config

    @staticmethod
    def hash_get():
        """获取哈希"""
        return config._config_hashes

    def config_load(self):
        """加载所有 YAML 文件记录到 config"""
        self._config.clear()
        self._config_sources.clear()
        for config_file in self._config_path.glob("*.yaml"):
            if config_file.name.endswith("_copy.yaml") or config_file.name in ["storage.yaml", "agent.yaml"]:
                continue  # 跳过模板文件
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f) or {}
                    self._config.update(yaml_data)
                    for key in yaml_data:  # key : 最外层键
                        self._config_sources[key] = config_file  # 记录来源文件
                    self._config_hashes[config_file] = file_hash_get(config_file)
            except Exception as e:
                print(f"[配置数据]yaml 文件格式错误-> {config_file.name}: {e}")
        self.log_set()  # 更新日志记录器

    @staticmethod
    def log_reset():
        """重置 logging 模块"""
        logging.shutdown()  # 关闭当前所有日志
        for name in list(
                logging.root.manager.loggerDict.keys()
        ):  # 获取所有 Logger 名称
            logger = logging.getLogger(name)
            logger.handlers.clear()  # 清空 handlers
            logger.filters.clear()  # 清空 filters
            logger.setLevel(logging.NOTSET)  # 重置 level

    def log_set(self):
        """应用日志配置"""
        global loggers
        new_hash = hash(str(self._config["logging"]))
        if self._log_hash == new_hash:
            loggers["system"].debug("[配置数据]更新", extra={"event": "配置更新"})
            return  # 日志配置没变化
        self._log_hash = new_hash
        self.log_reset()
        try:
            dictConfig(self._config["logging"])  # 载入日志配置
        except Exception as e:
            loggers["system"].error(f"[配置数据]日志错误-> {type(e).__name__}: {e}", extra={"event": "配置更新"})
        logger_names = list(self._config["logging"]["loggers"].keys())
        loggers = {name: logging.getLogger(name) for name in logger_names}
        # 配置过滤器
        loggers["uvicorn"].addFilter(UvicornFilter())
        loggers["uvicorn.access"].addFilter(UvicornFilter())
        loggers["uvicorn.error"].addFilter(UvicornFilter())
        loggers["server"].addFilter(ServerFilter())
        loggers["napcat"].addFilter(NapcatFilter())

        loggers["system"].debug("[配置数据]更新", extra={"event": "配置更新"})

    def load(self):
        """数据载入"""
        try:
            with open(self._config_path / "storage.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def save(self, data):
        """数据保存"""
        save_path = self._config_path / "storage.yaml"
        tmp = save_path.with_suffix(".tmp")  # 写入临时文件避免写入错误
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            tmp.replace(save_path)
            loggers["system"].debug("[配置数据]临时数据保存成功", extra={"event": "配置更新"})
        except Exception:
            tmp.unlink(missing_ok=True)
            raise


class AutoConfigHandler(FileSystemEventHandler):
    """YAML 配置文件的监听类"""

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".yaml"):
            file_path = Path(event.src_path)
            if file_path.name.endswith("_copy.yaml") or file_path.name == "storage.yaml":
                return  # 忽略模板文件变动
            time.sleep(0.5)  # 防止修改 yaml 后未更新哈希
            new_hash = file_hash_get(file_path)
            if config.hash_get().get(file_path) == new_hash:
                return  # 内容未改变
            loggers["system"].debug(
                f"[配置数据]写入-> {file_path}",
                extra={"event": "配置更新"},
            )
            config.config_load()  # 重新加载


class ConsoleHandler(logging.Handler):
    """控制台日志输出"""
    def emit(self, record):
        """控制台输出格式化"""
        if record.name.startswith("uvicorn") or record.name == "server":
            record.levelno = logging.DEBUG  # 更改 web 和 server 日志等级
        log_color = COLORS.get(record.levelno, "")  # 添加日志颜色
        source = f"[{SOURCE_DICT.get(record.name, record.name)}]"  # 更新 source
        event = getattr(record, "event", "-")  # 获取 event，默认 '-'
        message = record.getMessage()
        message = (
            COLOR_PATTERN.sub("", message).replace("\n", " ").replace("\r", "")
        )  # 清除原始颜色、空格

        sys.stdout.write(
            f"{log_color}{time.strftime('%H:%M:%S')}{source}{event}: {message}{Style.RESET_ALL}\n"
        )


class DatabaseHandler(logging.Handler):
    """数据库日志写入"""
    def emit(self, record):
        """数据库日志数据格式化"""
        global _last_log_drop_report
        message = record.getMessage()
        message = COLOR_PATTERN.sub("", message)
        if len(message) > LOG_MESSAGE_MAX_CHARS:
            message = message[:LOG_MESSAGE_MAX_CHARS] + "\n…[日志已截断]"
            RUNTIME_METRICS["log_truncated"] += 1

        item = (
            record.levelname,
            SOURCE_DICT.get(record.name, record.name).strip(),
            getattr(record, "event", "-"),
            message,
        )
        try:
            log_queue.put_nowait(item)
            return
        except asyncio.QueueFull:
            pass

        # 队列已满时丢弃低级日志；高级日志可替换最旧的一条。
        if record.levelno >= logging.WARNING:
            try:
                log_queue.get_nowait()
                log_queue.task_done()
                RUNTIME_METRICS["log_evicted"] += 1
                log_queue.put_nowait(item)
            except (asyncio.QueueEmpty, asyncio.QueueFull):
                RUNTIME_METRICS["log_dropped"] += 1
        else:
            RUNTIME_METRICS["log_dropped"] += 1

        now = time.monotonic()
        if now - _last_log_drop_report >= 60:
            _last_log_drop_report = now
            sys.stderr.write(
                "[LRobot]日志队列已满，"
                f"累计丢弃 {RUNTIME_METRICS['log_dropped']} 条，"
                f"替换 {RUNTIME_METRICS['log_evicted']} 条\n"
            )


class UvicornFilter(logging.Filter):
    """uvicorn 的日志过滤器"""

    def filter(self, record):
        """过滤"""
        if record.levelno == logging.DEBUG:
            return False  # 过滤 debug 日志
        record.event = "运行日志"
        if (
                hasattr(record, "args")
                and isinstance(record.args, tuple)
                and len(record.args) >= 5
        ):  # 更改 ip 访问日志的格式
            ip, method, route, http_version, status_code = record.args[:5]
            STATUS_MAP = config["status_codes"]
            record.event = STATUS_MAP.get(str(status_code), f"未知状态{status_code}")
            record.msg = f"{method}[{ip}]{route}-> HTTP/{http_version}"
            record.args = ()  # 清空 args，避免格式化错误
        return True


class ServerFilter(logging.Filter):
    """ssh 连接的日志过滤器"""

    def filter(self, record):
        """过滤"""
        msg = record.getMessage()
        if not msg:
            return False
        if "debug1" in msg:
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
            record.levelno = logging.DEBUG
            record.msg = msg.replace("debug1:", "").strip()  # 去掉 debug1: 前缀
        return True


class NapcatFilter(logging.Filter):
    """napcat 日志过滤器"""

    def filter(self, record):
        """过滤"""
        record.event = "运行日志"
        msg = record.getMessage()
        if not msg:  # 去除空行
            return False
        if msg.startswith("[") and not msg.startswith(
                "[NapCat Backend]"
        ):  # 处理调试信息
            record.levelname = "DEBUG"
            record.levelno = logging.DEBUG
        match = NAPCAT_PATTERN.search(msg)
        if match:  # 提取 message 里自带的等级和信息
            record.levelname = match.group("level").upper()
            record.msg = match.group("info")
        return True


def file_hash_get(file):
    """计算文件的哈希值，避免重复加载"""
    with open(file, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


@asynccontextmanager
async def connect(use_proxy=False, use_agent=False):
    """代理/不代理连接"""
    if use_agent:
        try:
            import socket
            with socket.create_connection(("mihomo", 7891), timeout=1):
                transport = AsyncProxyTransport.from_url("socks5://mihomo:7891")
                client = httpx.AsyncClient(transport=transport)
        except OSError:
            client = httpx.AsyncClient()
    elif config["SERVER_IP"] and config["SERVER_USERNAME"] and use_proxy:
        transport = AsyncProxyTransport.from_url("socks5://command:5923")
        client = httpx.AsyncClient(transport=transport)
    else:
        client = httpx.AsyncClient()
    try:
        yield client
    finally:
        await client.aclose()


def monitor_adapter(source):
    """消息适配器监控（异步函数）"""
    def decorator(func):
        """装饰器"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """统计数据"""
            from logic.data.system import system_get, system_edit, system_command_add
            global MONITOR_METRICS
            if not MONITOR_METRICS:  # 首次加载数据库
                text = await system_get("monitor_metrics")
                MONITOR_METRICS.update(json.loads(text) if text else {})

            if source not in MONITOR_METRICS:
                MONITOR_METRICS[source] = {
                    "total": 0,
                    "success": 0,
                    "fail": 0,
                    "total_time": 0.0
                }

            start = time.perf_counter()
            MONITOR_METRICS[source]["total"] += 1
            try:
                result = await func(*args, **kwargs)
                MONITOR_METRICS[source]["success"] += 1
                if source.startswith("/"):
                    msg = args[0]
                    from message.handler.msg import Msg
                    await system_command_add(source, msg.user, msg.platform, Msg.content_join(msg.content), result)
                if source.startswith("#"):
                    account = kwargs.get("account") or "unknown"
                    raw_data = kwargs.get("data", {})
                    if isinstance(raw_data, str):
                        try:
                            raw_data = json.loads(raw_data)
                        except Exception:
                            raw_data = {}
                    data_str = "-".join(str(v) for v in raw_data.values()) if isinstance(raw_data, dict) else ""
                    result_str = f"{result.status}-{result.data}" if result.data is not None else result.status
                    await system_command_add(source, account, "web", data_str, result_str)
                return result
            except Exception as e:
                MONITOR_METRICS[source]["fail"] += 1
                raise  # 仅统计，不处理
            finally:
                elapsed = time.perf_counter() - start
                MONITOR_METRICS[source]["total_time"] += elapsed
                await system_edit("monitor_metrics", json.dumps(MONITOR_METRICS))

        return wrapper

    return decorator


async def chunk_sleep(seconds, chunk=3600):
    """分段睡眠"""
    remaining = seconds
    try:
        while remaining > 0:
            await asyncio.sleep(min(remaining, chunk))
            remaining -= chunk
    except asyncio.CancelledError:
        raise

async def scheduler_run(func, *args, interval=None, at_time=None, count=None, at_once=False, **kwargs):
    """定时任务执行"""
    executed = 0
    if interval is None and at_time is None:
        raise ValueError("必须提供 interval 或 at_time 其一")
    if interval is not None:
        next_run = time.monotonic()
        if not at_once:
            next_run += interval
        while True:
            if count is not None and executed >= count:
                break
            sleep_for = next_run - time.monotonic()
            if sleep_for > 0:
                await chunk_sleep(sleep_for)
            try:
                await func(*args, **kwargs)
            except Exception as e:
                loggers["system"].error(
                    f"[定时任务]{func.__name__} 异常-> {type(e).__name__}: {e}", extra={"event": "定时任务"}
                )
                loggers["system"].debug(f"[定时任务]-> 堆栈: {traceback.format_exc()}\n变量: {locals()}",
                                        extra={"event": "错误堆栈"})
            executed += 1
            next_run += interval
    else:
        while True:
            if count is not None and executed >= count:
                break
            now = datetime.datetime.now()
            target = datetime.datetime.combine(now.date(), at_time)
            if now >= target:  # 如果当前时间已过目标时间，调整到第二天
                target += datetime.timedelta(days=1)
            wait_time = (target - now).total_seconds()
            await chunk_sleep(wait_time)
            try:
                await func(*args, **kwargs)
            except Exception as e:
                loggers["system"].error(
                    f"[定时任务]{func.__name__} 异常-> {type(e).__name__}: {e}", extra={"event": "定时任务"}
                )
                loggers["system"].debug(f"[定时任务]-> 堆栈: {traceback.format_exc()}\n变量: {locals()}",
                                        extra={"event": "错误堆栈"})
            executed += 1




def scheduler_add(func, *args, interval=None, at_time=None, count=None, at_once=False, **kwargs):
    """定时任务(需添加异步函数)"""
    return create_background_task(
        scheduler_run(func, *args, interval=interval, at_time=at_time, count=count, at_once=at_once, **kwargs),
        name=f"scheduler:{func.__name__}",
    )

async def config_watcher():
    """开启配置自动更新"""
    if config["SYSTEM"] == "linux":
        observer = InotifyObserver()
    else:
        observer = PollingObserver()
    observer.schedule(AutoConfigHandler(), str(path / "storage/yml"), recursive=False)
    observer.start()

    try:
        await asyncio.Event().wait()
    except Exception as e:
        loggers["system"].error(f"[配置数据]自动更新异常-> {type(e).__name__}: {e}", extra={"event": "配置更新"})
    finally:
        observer.stop()
        observer.join()


def mongo_init(uri="mongodb://mongodb:27017/lrobot_log"):
    """初始化 MongoDB 数据库连接"""
    global mongo_client, mongo_db
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        mongo_db = mongo_client.get_default_database()
        loggers["system"].debug("[数据库]连接成功-> Mongodb", extra={"event": "运行日志"})
    except Exception as e:
        print(f"[数据库]连接失败-> Mongodb: {e}")


def mongo_get():
    """获取 MongoDB 数据库连接"""
    if mongo_db is None:
        raise RuntimeError("[数据库]mongodb 未初始化")
    return mongo_db


def runtime_metrics_snapshot():
    """汇总不包含用户内容的内存风险指标。"""
    from message.handler.msg_pool import MsgPool

    return {
        "future": future.stats(),
        "log_queue": log_queue.qsize(),
        "log_queue_max": log_queue.maxsize,
        "background_tasks": len(_background_tasks),
        "background_task_max": BACKGROUND_TASK_MAX,
        **MsgPool.stats(),
        **RUNTIME_METRICS,
    }


async def runtime_metrics_report():
    """定期输出有界队列/Future 指标，用于发现接近上限的趋势。"""
    loggers["system"].info(
        f"[资源边界]{json.dumps(runtime_metrics_snapshot(), ensure_ascii=False)}",
        extra={"event": "运行指标"},
    )


async def log_writer():
    """开启日志写入 MongoDB 数据库"""
    while True:
        level, source, event, message = await log_queue.get()
        text_index = (
                (source in ["system", "adapter", "message"])
                or (source == "website" and event == "网页日志")
        )
        document = {
            "time": datetime.datetime.now(),
            "level": level,
            "source": source,
            "event": event,
            "message": message,
            "hasTextIndex": text_index,
        }
        try:
            await mongo_db.system_log.insert_one(document)
        except Exception as e:
            print(f"[数据库]写入失败-> Mongodb: {e}")
        finally:
            log_queue.task_done()


async def mysql_init():
    """初始化 mysql 连接"""
    global mysql_db_pool
    mysql_db_pool = await aiomysql.create_pool(
        host="mysql",
        port=3306,
        user="root",
        password="",
        db="lrobot_data",
        minsize=5,
        maxsize=20,
        autocommit=False,  # 必须为 False 才能手动控制提交与回滚
    )
    loggers["system"].debug("[数据库]连接成功-> Mysql", extra={"event": "运行日志"})


async def connections_close():
    """关闭数据库连接和 Future，避免重启时遗留资源。"""
    global mysql_db_pool
    future.clear()
    if mysql_db_pool is not None:
        mysql_db_pool.close()
        await mysql_db_pool.wait_closed()
        mysql_db_pool = None
    if mongo_client is not None:
        mongo_client.close()


async def database_query(query: str, params: tuple = ()):
    """执行查询语句"""
    async with mysql_db_pool.acquire() as conn:
        await conn.commit()  # 先提交事务
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(query, params)
                result = await cur.fetchall()
                return result
            except Exception as e:
                raise RuntimeError(
                    f"[数据库]查询失败: {e} | SQL: {query} | 参数: {params}"
                ) from e


async def database_update(query: str, params: tuple = ()):
    """执行更新语句"""
    async with mysql_db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(query, params)
                await conn.commit()
                from web.backend.cab.database import broadcast_db_update

                await broadcast_db_update()
                return cur.lastrowid
            except Exception as e:
                await conn.rollback()
                raise RuntimeError(
                    f"[数据库]更新失败: {e} | SQL: {query} | 参数: {params}"
                ) from e


# 初始化配置信息
config = AutoConfig(path / "storage/yml")
# 初始化 future 变量管理器
future = FutureManager()
# 初始化 MongoDB 连接
mongo_init()
# 加载存储
storage = config.load()
