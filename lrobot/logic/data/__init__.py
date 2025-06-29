import sys
from pathlib import Path
from logic.reloader import ModuleManager

manager = ModuleManager(
    module_dir=Path(__file__).parent,
    package_base=__name__,  # 即 logic.data
    inject_target=sys.modules[__name__]
)
manager.start()

from .ip import check_and_update_ip
from .user import user_codename
