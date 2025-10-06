"""模块重载"""

import sys
import importlib
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from config import loggers


class ModuleManager(FileSystemEventHandler):
    def __init__(
            self, module_dir: Path, package_base: str, inject_target=None, ignore_files=None
    ):
        self.module_dir = module_dir  # 模块所在目录 Path
        self.package_base = package_base  # 包名,logic.command
        self.inject_target = inject_target or sys.modules[package_base]  # 命名空间模块 sys.modules["logic.command"]
        self.ignore_files = set(ignore_files or ["__init__.py"])  # 忽略文件名列表
        self._all_modules_load()

    def _all_modules_load(self):
        for py_file in self.module_dir.glob("*.py"):
            if py_file.name in self.ignore_files:
                continue
            self._module_load(py_file.stem)

    def _module_load(self, stem: str):
        module_name = f"{self.package_base}.{stem}"
        try:
            module = importlib.import_module(module_name)
            self._namespace_inject(module)
            loggers["system"].debug(f"[加载]-> {module_name}", extra={"event": "模块加载"})
        except Exception as e:
            loggers["system"].error(
                f"[加载]-> {module_name}: {type(e).__name__}: {e}", extra={"event": "模块加载"}
            )

    def _module_reload(self, module_name: str):
        try:
            module = importlib.reload(sys.modules[module_name])
            self._namespace_inject(module)
            loggers["system"].debug(
                f"[重载]-> {module_name}", extra={"event": "模块加载"}
            )
        except Exception as e:
            loggers["system"].error(
                f"[重载]-> {module_name}: {type(e).__name__}: {e}",
                extra={"event": "模块加载"},
            )

    def _namespace_inject(self, module):
        for attr in dir(module):
            if not attr.startswith("_"):
                setattr(self.inject_target, attr, getattr(module, attr))

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        filename = Path(event.src_path).name
        if filename in self.ignore_files:
            return
        stem = Path(filename).stem
        module_name = f"{self.package_base}.{stem}"
        if module_name in sys.modules:
            self._module_reload(module_name)
        else:
            self._module_load(stem)

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        filename = Path(event.src_path).name
        if filename in self.ignore_files:
            return
        stem = Path(filename).stem
        self._module_load(stem)

    def start(self):
        """开启监听"""
        observer = PollingObserver()
        observer.schedule(self, str(self.module_dir), recursive=False)
        observer.start()
