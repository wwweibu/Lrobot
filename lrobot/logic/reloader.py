"""模块重载"""

import os
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
        """
        :param module_dir: 模块所在目录 Path
        :param package_base: 包名（如 "logic.command"）
        :param inject_target: 要注入的命名空间模块（如 sys.modules["logic.command"]）
        :param ignore_files: 忽略文件名列表
        """
        self.module_dir = module_dir
        self.package_base = package_base
        self.inject_target = inject_target or sys.modules[package_base]
        self.ignore_files = set(ignore_files or ["__init__.py"])
        self._load_all_modules()

    def _load_all_modules(self):
        for py_file in self.module_dir.glob("*.py"):
            if py_file.name in self.ignore_files:
                continue
            self._load_module(py_file.stem)

    def _load_module(self, stem: str):
        module_name = f"{self.package_base}.{stem}"
        try:
            module = importlib.import_module(module_name)
            self._inject_to_namespace(module)
            loggers["system"].info(f"{module_name}", extra={"event": "模块加载"})
        except Exception as e:
            loggers["system"].error(
                f"失败: {module_name} -> {e}", extra={"event": "模块加载"}
            )

    def _reload_module(self, module_name: str):
        try:
            module = importlib.reload(sys.modules[module_name])
            self._inject_to_namespace(module)
            loggers["system"].info(
                f"模块热重载: {module_name}", extra={"event": "模块加载"}
            )
        except Exception as e:
            loggers["system"].error(
                f"模块热重载失败: {module_name} -> {e}",
                extra={"event": "模块加载"},
            )

    def _inject_to_namespace(self, module):
        for attr in dir(module):
            if not attr.startswith("_"):
                setattr(self.inject_target, attr, getattr(module, attr))

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        filename = os.path.basename(event.src_path)
        if filename in self.ignore_files:
            return
        stem = Path(filename).stem
        module_name = f"{self.package_base}.{stem}"
        if module_name in sys.modules:
            self._reload_module(module_name)
        else:
            self._load_module(stem)

    def start(self):
        """开启监听"""
        observer = PollingObserver()
        observer.schedule(self, str(self.module_dir), recursive=False)
        observer.start()
