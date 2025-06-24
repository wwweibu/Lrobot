import os
import sys
import importlib
from pathlib import Path
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from config import loggers


# 命令模块路径
command_dir = Path(__file__).parent
package_base = __name__  # 即 "logic.command"

# 模块缓存：module_name -> module object
_loaded_modules = {}

def _load_all_modules():
    for py_file in command_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        module_name = f"{package_base}.{py_file.stem}"
        module = importlib.import_module(module_name)
        _loaded_modules[module_name] = module

        # 自动将模块中的所有函数提升到 logic.command 命名空间
        for attr in dir(module):
            if not attr.startswith("_"):
                globals()[attr] = getattr(module, attr)

def _reload_module(module_name: str):
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)

    module = sys.modules[module_name]
    _loaded_modules[module_name] = module

    # 更新当前命名空间中的函数引用
    for attr in dir(module):
        if not attr.startswith("_"):
            globals()[attr] = getattr(module, attr)
    loggers["system"].info(f"模块热重载: {module_name}", extra={"event": "配置读取"})


class CommandModuleEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        filename = os.path.basename(event.src_path)
        if filename == "__init__.py":
            return
        module_name = f"{package_base}.{Path(filename).stem}"
        _reload_module(module_name)


def _start_watchdog():
    observer = PollingObserver()
    handler = CommandModuleEventHandler()
    observer.schedule(handler, str(command_dir), recursive=False)
    observer.start()


# 初始化模块与监听器
_load_all_modules()
_start_watchdog()
