"""适配器函数导入"""

from .acess_token import refresh_tokens
from .bili_dispatch import *
from .bili_receive import bili_receive, bili_fan_get, bili_msg_get
from .lr232_dispatch import *
from .lr232_receive import router as LR232_router
from .lr5921_dispatch import *
from .lr5921_receive import router as LR5921_router
from .wechat_dispatch import *
from .wechat_receive import router as WECHAT_router
