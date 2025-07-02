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
from .user import change_codename_to_user,identify_user
from .status import check_status
from .user_test import get_user_test_group_password
