# 基本的配置及常量（放在此处避免循环引用）
# 包含：全局路径、自定义路径加密、代理连接、future 变量、消息处理监控、定时任务、配置信息读写、日志记录器、 数据库写入查询操作
# 需要使用 mysql 数据库引入 init_mysql；日志写入需要 gather log_writer；配置自动更新需要 gather init_config
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
from pathlib import Path
import motor.motor_asyncio
from colorama import Fore, Style
from collections import defaultdict
from logging.config import dictConfig
from watchdog.observers import Observer
from httpx_socks import AsyncProxyTransport
from watchdog.events import FileSystemEventHandler


# 全局路径
path = Path(__file__).resolve().parent  # python 中为 /lrobot,dokcer 中为 /app

config = {}  # 配置信息
mongo_client = None  # mongo 连接
mongo_db = None
mysql_db_pool: aiomysql.Pool = None  # mysql 连接
log_queue = asyncio.Queue()  # 日志队列
loggers = {}  # 日志记录器

# 颜色匹配
color_pattern = re.compile(r"\x1b\[[0-9;]*m")
# napcat 日志匹配
napcat_pattern = re.compile(
    r"\[(\u001b\[\d+m(?P<level>[^\u001b]+)\u001b\[39m)\] (?P<info>.*)"
)
# 颜色设置
COLORS = {
    logging.DEBUG: Fore.LIGHTBLACK_EX,  # 灰色
    logging.INFO: Fore.BLACK,  # 黑色
    logging.WARNING: Fore.RED,  # 红色
    logging.ERROR: Fore.RED,  # 红色
}
# 日志来源替换映射
source_dict = {
    "system": "system ",
    "server": "server ",
    "uvicorn": "website",
    "uvicorn.access": "website",
    "uvicorn.error": "website",
}

# 适配器监控指标
monitor_metrics = defaultdict(
    lambda: {
        "total": 0,
        "success": 0,
        "fail": 0,
        "total_time": 0.0,
    }
)

# 自定义路径加密
def secret(text):
    key_values = [23, 5, 9, 2, 21]  # "weibu" 对应的数值

    def char_to_num(c):
        return ord(c) - ord("a") + 1

    def num_to_char(n):
        return chr((n - 1) % 26 + ord("a"))

    encrypted_text = ""
    for i, c in enumerate(text.lower()):
        if c.isalpha():
            shift = key_values[i % len(key_values)]
            new_char = num_to_char(char_to_num(c) + shift)
            encrypted_text += new_char
        else:
            encrypted_text += c

    return encrypted_text


# 代理/不代理连接
def connect(use_proxy=False, proxy_url="socks5://command:5923"):
    if use_proxy:
        transport = AsyncProxyTransport.from_url(proxy_url)
        return httpx.AsyncClient(transport=transport)
    else:
        # 创建标准客户端
        return httpx.AsyncClient()


# future 变量管理
class FutureManager:
    def __init__(self):
        self.futures = {}  # Future 对象字典
        self.loop = None  # 主事件循环

    def init(self, loop):
        self.loop = loop

    def get(self, key):
        """获取已有的 Future 对象，若不存在则创建一个新的"""
        if key not in self.futures:
            self.futures[key] = self.loop.create_future()
        return self.futures[key]

    def set(self, key, result):
        """设置 Future 对象的结果"""
        _future = self.get(key)
        if not _future.done():
            self.loop.call_soon_threadsafe(
                _future.set_result, result
            )  # 同步线程调用时可唤醒异步线程
            self.loop.call_soon_threadsafe(lambda: None)


# 消息适配器处理监控
def monitor_adapter(platform: str):
    """适配器监控装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            monitor_metrics[platform]["total"] += 1
            try:
                result = await func(*args, **kwargs)
                monitor_metrics[platform]["success"] += 1
                return result
            except Exception as e:
                monitor_metrics[platform]["fail"] += 1
                loggers["adapter"].error(
                    f"⌈{platform}⌋ 消息处理错误 -> {e}", extra={"event": "消息接收"}
                )
            finally:
                elapsed = time.perf_counter() - start
                monitor_metrics[platform]["total_time"] += elapsed

        return wrapper

    return decorator


# 定时任务添加
async def add_scheduler(func,*args, interval=None, at_time=None, count=None,**kwargs):
    """异步函数的定时任务"""
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
            await func(*args,**kwargs)  # 只能执行异步
        except Exception as e:
            loggers["system"].error(
                f"定时任务{func.__name__}异常 -> {e}", extra={"event": "定时任务"}
            )
            # traceback.print_exc()  # 调试用
        executed += 1


class SafeDict(dict):
    """支持多层嵌套访问的字典，访问不存在的键时返回空 SafeDict 而非抛异常"""
    def __getitem__(self, key):
        return super().get(key, SafeDict())

    def get(self, key, default=None):
        return super().get(key, default if default is not None else SafeDict())


def get_file_hash(file):
    """计算文件的哈希值，避免重复加载"""
    with open(file, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


#配置信息读写
class AutoConfig:
    """配置参数读写"""
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = {}
        self.config_sources = {}  # 记录每个 key 来自哪个文件
        self.config_hashes = {}  # 文件哈希，避免重复加载
        self.load_config()

    def __setitem__(self, key, value):
        """实现自动写回 YAML"""
        if key not in self.config_sources:
            raise Exception(f"配置项 {key} 不存在，无法确定其来源文件")

        file_path = self.config_sources[key]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            data[key] = value
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
            self.config[key] = value  # 同步更新内存中的值
            self.config_hashes[file_path] = get_file_hash(file_path)  # 更新哈希值
        except Exception as e:
            raise Exception(f"写入配置项 {key} 到 {file_path.name} 失败 -> {e}")

    def __getitem__(self, key):
        """实现多层访问"""
        value = self.config.get(key, {})
        if isinstance(value, dict):
            return SafeDict(value)
        return value

    def __str__(self):
        """返回配置的字符串，用于打印"""
        return f"config:{self.config}"

    def __contains__(self, key):
        """重载字典的 __contains__ 方法"""
        return key in self.config

    def load_config(self):
        """加载所有 YAML 文件记录到 config"""
        self.config.clear()
        self.config_sources.clear()
        for config_file in self.config_path.glob("*.yaml"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f) or {}
                    self.config.update(yaml_data)
                    for key in yaml_data:  # key : 最外层键
                        self.config_sources[key] = config_file  # 记录来源文件
                    self.config_hashes[config_file] = get_file_hash(config_file)
            except Exception as e:
                loggers["system"].error(
                    f"yaml 文件 {config_file.name} 格式错误 -> {e}",
                    extra={"event": "配置读取"},
                )
        set_log()  # 更新日志记录器


class AutoConfigHandler(FileSystemEventHandler):
    """YAML 配置文件的监听类"""
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".yaml"):
            file_path = Path(event.src_path)
            time.sleep(0.5)  # 防止修改 yaml 后未更新哈希
            new_hash = get_file_hash(file_path)
            if config.config_hashes.get(file_path) == new_hash:
                return  # 内容未改变
            loggers["system"].info(
                f"yaml 文件 {file_path} 更新",
                extra={"event": "配置读取"},
            )
            config.load_config()  # 重新加载


async def config_watcher():
    """开启配置自动更新"""
    global config
    config = AutoConfig(path / "storage/yml")
    observer = Observer()
    observer.schedule(AutoConfigHandler(), str(path / "storage/yml"), recursive=False)
    observer.start()

    try:
        await asyncio.Event().wait()
    finally:
        observer.stop()
        observer.join()


def init_mongo(uri: str = "mongodb://mongodb:27017/lrobot_log"):
    """初始化 MongoDB 数据库连接"""
    global mongo_client, mongo_db
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    mongo_db = mongo_client.get_default_database()
    loggers["system"].info("Mongodb 数据库连接成功", extra={"event": "运行日志"})


async def log_writer():
    """开启日志写入 MongoDB 数据库"""
    while True:
        time, level, source, event, message = await log_queue.get()
        document = {
            "time": time,
            "level": level,
            "source": source,
            "event": event,
            "message": message
        }
        try:
            await mongo_db.system_log.insert_one(document)
        except Exception as e:
            loggers["system"].error(f"Mongodb 日志写入错误 -> {e}", extra={"event": "运行日志"})


class ConsoleHandler(logging.Handler):
    """控制台日志输出"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        if self.formatter:
            self.format(record)  # 添加 asctime 属性
        if record.name.startswith("uvicorn") or record.name == "server":
            record.levelno = logging.DEBUG  # 更改 web 和 server 日志等级
        log_color = COLORS.get(record.levelno, Fore.RESET)  # 添加日志颜色
        source = f"[{source_dict.get(record.name, record.name)}]"  # 更新 source
        event = getattr(record, "event", "-")  # 获取 event，默认 '-'
        message = record.getMessage()
        message = (
            color_pattern.sub("", message).replace("\n", " ").replace("\r", "")
        )  # 清除原始颜色

        sys.stdout.write(
            f"{log_color}{record.asctime}{source}{event}: {message}{Style.RESET_ALL}\n"
        )


class DatabaseHandler(logging.Handler):
    """数据库日志写入"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        if self.formatter:
            self.format(record)
        message = record.getMessage()
        message = color_pattern.sub("", message)
        try:
            log_queue.put_nowait((record.asctime,record.levelname,source_dict.get(record.name, record.name),getattr(record, "event", "-"),message))
        except Exception as e:
            loggers["system"].error(f"Mysql 日志入队失败 -> {e}", extra={"event": "运行日志"})


class UvicornFilter(logging.Filter):
    """uvicorn 的日志过滤器"""

    def filter(self, record):
        if record.levelno == logging.DEBUG:
            return False  # 过滤 debug 日志
        record.event = "运行日志"
        if (
            hasattr(record, "args")
            and isinstance(record.args, tuple)
            and len(record.args) >= 5
        ):  # 更改 ip 访问日志的格式
            ip, method, path, http_version, status_code = record.args[:5]
            STATUS_MAP = config["status_codes"]
            record.event = STATUS_MAP.get(str(status_code), f"未知状态{status_code}")
            record.msg = f"[{ip}]{method} {path} -> HTTP/{http_version}"
            record.args = ()  # 清空 args，避免格式化错误
        return True


class ServerFilter(logging.Filter):
    """ssh 连接的日志过滤器"""

    def filter(self, record):
        if not record.getMessage():
            return False
        if "debug1" in record.getMessage():
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
            record.levelno = logging.DEBUG
            record.msg = record.msg.replace("debug1:", "").strip()  # 去掉 debug1: 前缀
        return True


class LR5921Filter(logging.Filter):
    """LR5921 的日志过滤器，暂时不用"""

    def filter(self, record):
        if not record.getMessage():
            return False
        if record.getMessage().startswith("[") and not record.getMessage().startswith(
            "[NapCat Backend]"
        ):  # 处理调试信息
            record.levelname = "DEBUG"  # 设置为 DEBUG 级别
            record.levelno = logging.DEBUG
        match = napcat_pattern.search(record.getMessage())
        if match:  # 提取 message 里自带的等级和信息
            record.levelname = match.group("level").upper()
            record.msg = match.group("info")
        return True


def reset_log():
    """重置 logging 模块"""
    logging.shutdown()  # 关闭当前所有日志
    for name in list(logging.root.manager.loggerDict.keys()):  # 获取所有 Logger 名称
        logging.getLogger(name).handlers.clear()  # 清空 handlers
        logging.getLogger(name).filters.clear()  # 清空 filters
        logging.getLogger(name).setLevel(logging.NOTSET)  # 重置 level


def set_log():
    """应用日志配置"""
    global loggers
    reset_log()
    try:
        dictConfig(config["logging"])  # 载入日志配置
    except Exception as e:
        loggers["system"].error(f"日志配置错误 -> {e}", extra={"event": "运行日志"})
    logger_names = list(config["logging"]["loggers"].keys())
    loggers = {name: logging.getLogger(name) for name in logger_names}
    # 配置过滤器
    loggers["uvicorn"].addFilter(UvicornFilter())
    loggers["uvicorn.access"].addFilter(UvicornFilter())
    loggers["uvicorn.error"].addFilter(UvicornFilter())
    loggers["server"].addFilter(ServerFilter())
    loggers["system"].info("配置数据更新", extra={"event": "配置读取"})


async def init_mysql():
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


async def query_database(query: str, params: tuple = ()):
    """执行查询语句"""
    async with mysql_db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(query, params)
                result = await cur.fetchall()
                return result
            except Exception as e:
                loggers["system"].error(f"Mysql 查询语句异常 -> {e} | 查询: {query} | 参数: {params}", extra={"event": "运行日志"})


async def update_database(query: str, params: tuple = ()):
    """执行更新语句"""
    async with mysql_db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(query, params)
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                loggers["system"].error(f"Mysql 更新语句异常 -> {e} | 更新: {query} | 参数: {params}",
                                        extra={"event": "运行日志"})


# 初始化 future 变量管理器
future = FutureManager()
# 初始化 config
for file in (path / "storage/yml").glob("*.yaml"):
    with open(file, "r", encoding="utf-8") as f:
        config.update(yaml.safe_load(f) or {})
# 初始化日志记录器
set_log()
# 初始化 MongoDB 连接
init_mongo()
