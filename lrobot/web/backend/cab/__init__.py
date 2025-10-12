# 路由导入

from .command import router as command_router
from .database import router as database_router
from .file import router as file_router
from .home import router as home_router
from .joke import router as joke_router, ip_cache
from .log import router as log_router
from .login import router as login_router
from .metrics import router as metrics_router
from .panel import router as panel_router
from .static import router as static_router
from .timeline import router as time_router
from .user import router as user_router
from .wiki import router as wiki_router
