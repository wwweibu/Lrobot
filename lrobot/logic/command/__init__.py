"""动态导入 command 中的模块"""

import sys
from pathlib import Path

from logic.reloader import ModuleManager

manager = ModuleManager(
    module_dir=Path(__file__).parent,
    package_base=__name__,  # logic.command
    inject_target=sys.modules[__name__],
)
manager.start()
