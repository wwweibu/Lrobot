"""动态导入 data 中的模块"""

import sys
from pathlib import Path

from logic.reloader import ModuleManager

manager = ModuleManager(
    module_dir=Path(__file__).parent,
    package_base=__name__,  # logic.data
    inject_target=sys.modules[__name__],
)
manager.start()

# 静态引入，用于非 command 模块
from .ip import ip_check
from .wiki import wiki_get
from .firefly import firefly_password_get
from .backup import backup_mysql, backup_mongo
from .user import user_codename_change, user_identify
from .status import status_check, status_add, status_delete
from .file import record_convert, image_compress, record_compress, video_compress, file_download, file_name_overwrite
