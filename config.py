# 基本的配置及常量
# 包含：全局路径、代理连接、future 变量、消息处理监控、定时任务、配置信息读写、日志记录器、 数据库写入查询操作
# 需要使用 mysql 数据库引入 mysql_init；日志写入需要 gather log_writer；配置自动更新需要 gather config_watcher
import re
import sys
import time
import yaml
import httpx
import asyncio
import hashlib
import logging
import aiomysql
import datetime
import functools
import traceback
from pathlib import Path
import motor.motor_asyncio
from colorama import Fore, Style
from collections import defaultdict
from logging.config import dictConfig
from httpx_socks import AsyncProxyTransport
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

# 颜色匹配
COLOR_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
# napcat 日志匹配
NAPCAT_PATTERN = re.compile(
    r"\[(\u001b\[\d+m(?P<level>[^\u001b]+)\u001b\[39m)] (?P<info>.*)"
)
# 颜色设置
COLORS = {
    logging.DEBUG: Fore.LIGHTBLACK_EX,  # 灰色
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
}
# 适配器监控指标
MONITOR_METRICS = defaultdict(
    lambda: {
        "total": 0,
        "success": 0,
        "fail": 0,
        "total_time": 0.0,
    }
)

path = Path(__file__).resolve().parent  # 全局路径,python 中为 /lrobot,dokcer 中为 /app
mongo_client = None  # mongo 连接
mongo_db = None
mysql_db_pool = None  # mysql 连接
log_queue = asyncio.Queue()  # 日志队列
loggers = {}  # 日志记录器


class FutureManager:
    """
    管理 future 变量，用于协程间通信
    创建
    try:
        _future = future.get(seq)
        response = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
    设值
    future.set(seq, response)
    """

    def __init__(self):
        self._futures = {}  # Future 对象字典
        self._loop = None  # 主事件循环

    def init(self, loop):
        """传入主事件循环"""
        self._loop = loop

    def get(self, key):
        """获取已有的 Future 对象，若不存在则创建一个新的"""
        if key not in self._futures:
            self._futures[key] = self._loop.create_future()
        return self._futures[key]

    def set(self, key, result):
        """设置 Future 对象的结果"""
        _future = self.get(key)
        if not _future.done():
            self._loop.call_soon_threadsafe(
                _future.set_result, result
            )  # 同步线程调用时可唤醒异步线程
            self._loop.call_soon_threadsafe(lambda: None)


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
        self.config_load()

    def __setitem__(self, key, value):
        """自动写回 YAML"""
        if key not in self._config_sources:
            raise Exception(f"配置项 {key} 不存在，无法确定其来源文件")

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
            raise Exception(f"写入配置项 {key} 至 {file_path.name} 失败 -> {e}")

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
            if config_file.name.endswith("_copy.yaml"):
                continue  # 跳过模板文件
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f) or {}
                    self._config.update(yaml_data)
                    for key in yaml_data:  # key : 最外层键
                        self._config_sources[key] = config_file  # 记录来源文件
                    self._config_hashes[config_file] = file_hash_get(config_file)
            except Exception as e:
                loggers["system"].error(
                    f"yaml 文件 {config_file.name} 格式错误 -> {e}",
                    extra={"event": "配置读取"},
                )
        self.log_set()  # 更新日志记录器

    @staticmethod
    def log_reset():
        """重置 logging 模块"""
        logging.shutdown()  # 关闭当前所有日志
        for name in list(
                logging.root.manager.loggerDict.keys()
        ):  # 获取所有 Logger 名称
            logging.getLogger(name).handlers.clear()  # 清空 handlers
            logging.getLogger(name).filters.clear()  # 清空 filters
            logging.getLogger(name).setLevel(logging.NOTSET)  # 重置 level

    def log_set(self):
        """应用日志配置"""
        global loggers
        self.log_reset()
        try:
            dictConfig(self._config["logging"])  # 载入日志配置
        except Exception as e:
            loggers["system"].error(f"日志配置错误 -> {e}", extra={"event": "运行日志"})
        logger_names = list(self._config["logging"]["loggers"].keys())
        loggers = {name: logging.getLogger(name) for name in logger_names}
        # 配置过滤器
        loggers["uvicorn"].addFilter(UvicornFilter())
        loggers["uvicorn.access"].addFilter(UvicornFilter())
        loggers["uvicorn.error"].addFilter(UvicornFilter())
        loggers["server"].addFilter(ServerFilter())
        loggers["system"].info("配置数据更新", extra={"event": "配置读取"})

    def load(self, key):
        """数据载入"""
        value = self._config.get(key)
        self._storage[key] = value  # 注册引用
        return value

    def save(self):
        """数据保存"""
        for key, ref in self._storage.items():
            self[key] = ref


class AutoConfigHandler(FileSystemEventHandler):
    """YAML 配置文件的监听类"""

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".yaml"):
            file_path = Path(event.src_path)
            if file_path.name.endswith("_copy.yaml"):
                return  # 忽略模板文件变动
            time.sleep(0.5)  # 防止修改 yaml 后未更新哈希
            new_hash = file_hash_get(file_path)
            if config.hash_get().get(file_path) == new_hash:
                return  # 内容未改变
            loggers["system"].info(
                f"yaml 文件 {file_path} 更新",
                extra={"event": "配置读取"},
            )
            config.config_load()  # 重新加载


class ConsoleHandler(logging.Handler):
    """控制台日志输出"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        """控制台输出格式化"""
        if record.name.startswith("uvicorn") or record.name == "server":
            record.levelno = logging.DEBUG  # 更改 web 和 server 日志等级
        log_color = COLORS.get(record.levelno, Fore.RESET)  # 添加日志颜色
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

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        """数据库日志数据格式化"""
        message = record.getMessage()
        message = COLOR_PATTERN.sub("", message)

        log_queue.put_nowait(
            (
                record.levelname,
                SOURCE_DICT.get(record.name, record.name),
                getattr(record, "event", "-"),
                message,
            )
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
            record.msg = f"[{ip}]{method} {route} -> HTTP/{http_version}"
            record.args = ()  # 清空 args，避免格式化错误
        return True


class ServerFilter(logging.Filter):
    """ssh 连接的日志过滤器"""

    def filter(self, record):
        """过滤"""
        if not record.getMessage():
            return False
        if "debug1" in record.getMessage():
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
            record.levelno = logging.DEBUG
            record.msg = record.msg.replace("debug1:", "").strip()  # 去掉 debug1: 前缀
        return True


class LR5921Filter(logging.Filter):
    """napcat 的日志过滤器，暂时不用"""

    def filter(self, record):
        """过滤"""
        if not record.getMessage():  # 去除空行
            return False
        if record.getMessage().startswith("[") and not record.getMessage().startswith(
                "[NapCat Backend]"
        ):  # 处理调试信息
            record.levelname = "DEBUG"
            record.levelno = logging.DEBUG
        match = NAPCAT_PATTERN.search(record.getMessage())
        if match:  # 提取 message 里自带的等级和信息
            record.levelname = match.group("level").upper()
            record.msg = match.group("info")
        return True


def file_hash_get(file):
    """计算文件的哈希值，避免重复加载"""
    with open(file, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def connect(use_proxy=False, proxy_url="socks5://command:5923"):
    """
    代理/不代理连接，代理用 connect(True)，不代理用 connect()
    调用方式:
    client = connect(True)
    response = await client.delete(url, headers=headers)
    if response.status_code == 200:
    else:
    """
    if use_proxy:
        transport = AsyncProxyTransport.from_url(proxy_url)
        return httpx.AsyncClient(transport=transport)
    else:
        return httpx.AsyncClient()


def monitor_adapter(platform: str):
    """
    消息适配器监控
    TODO 用于统计消息处理总数，成功数，失败数，总时间
    """

    def decorator(func):
        """装饰器"""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            """统计数据"""
            start = time.perf_counter()
            MONITOR_METRICS[platform]["total"] += 1
            try:
                result = await func(*args, **kwargs)
                MONITOR_METRICS[platform]["success"] += 1
                return result
            except Exception as e:
                MONITOR_METRICS[platform]["fail"] += 1
                raise  # 仅统计，不处理
            finally:
                elapsed = time.perf_counter() - start
                MONITOR_METRICS[platform]["total_time"] += elapsed

        return wrapper

    return decorator


async def scheduler_add(func, *args, interval=None, at_time=None, count=None, **kwargs):
    """
    添加定时任务（异步函数），使用时需要设置为新协程，逗号传入函数参数
    如 asyncio.create_task(add_scheduler(clean_messages,86400,interval=86400))
    interval是间隔时间（首次执行在间隔后）；at_time是固定时间（datetime.time(8, 30, 0)），count是执行次数
    """
    executed = 0
    while True:
        if count is not None and executed >= count:
            break
        if interval:
            await asyncio.sleep(interval)
        else:
            now = datetime.datetime.now()
            target = datetime.datetime.combine(now.date(), at_time)
            if now > target:  # 如果当前时间已过目标时间，调整到第二天
                target += datetime.timedelta(days=1)
            wait_time = (target - now).total_seconds()
            await asyncio.sleep(wait_time)
        try:
            await func(*args, **kwargs)  # 只能执行异步
        except Exception as e:
            loggers["system"].error(
                f"定时任务 {func.__name__} 异常 -> {e}", extra={"event": "定时任务"}
            )
            loggers["system"].error(traceback.format_exc(), extra={"event": "错误堆栈"})
        executed += 1


async def config_watcher():
    """开启配置自动更新"""
    observer = PollingObserver()
    observer.schedule(AutoConfigHandler(), str(path / "storage/yml"), recursive=False)
    observer.start()

    try:
        await asyncio.Event().wait()
    finally:
        observer.stop()
        observer.join()


def mongo_init(uri="mongodb://mongodb:27017/lrobot_log"):
    """初始化 MongoDB 数据库连接"""
    global mongo_client, mongo_db
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        mongo_db = mongo_client.get_default_database()
        loggers["system"].info("Mongodb 数据库连接成功", extra={"event": "运行日志"})
    except Exception as e:
        print(f"[数据库连接失败] Mongodb 异常: {e}")


def mongo_get():
    """获取 MongoDB 数据库连接"""
    if mongo_db is None:
        raise RuntimeError("MongoDB 尚未初始化，请先调用 init_mongo()")
    return mongo_db


async def log_writer():
    """开启日志写入 MongoDB 数据库"""
    while True:
        level, source, event, message = await log_queue.get()
        document = {
            "time": datetime.datetime.now(),
            "level": level,
            "source": source,
            "event": event,
            "message": message,
        }
        try:
            await mongo_db.system_log.insert_one(document)
        except Exception as e:
            print(f"[日志写入失败] Mongodb 异常: {e}")


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
    loggers["system"].info("Mysql 数据库连接成功", extra={"event": "运行日志"})


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
                    f"数据库查询失败: {e} | SQL: {query} | 参数: {params}"
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
                    f"数据库更新失败: {e} | SQL: {query} | 参数: {params}"
                ) from e


# 初始化配置信息
config = AutoConfig(path / "storage/yml")
# 初始化 future 变量管理器
future = FutureManager()
# 初始化 MongoDB 连接
mongo_init()
