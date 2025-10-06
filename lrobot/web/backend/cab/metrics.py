"""指令监控指标"""

import jieba
from collections import Counter

from .base import APIRouter, R, Query
from config import MONITOR_METRICS, database_query

router = APIRouter()


@router.get("/metrics/adapter")
async def adapter_data_get():
    """适配器监控数据"""
    adapters = {k: v for k, v in MONITOR_METRICS.items() if k in ["LR232", "LR5921", "WECHAT", "BILI"]}
    return R(status="success", data=adapters)


@router.get("/metrics/command")
async def command_list_get():
    """指令列表"""
    commands = {k: v for k, v in MONITOR_METRICS.items() if k not in ["LR232", "LR5921", "WECHAT", "BILI"]}
    return R(status="success", data=commands)


@router.get("/metrics/user")
async def user_list_get():
    """用户数据列表"""
    query = """
            SELECT user, COUNT(id) AS count
            FROM system_command
            GROUP BY user
            ORDER BY count DESC
        """
    results = await database_query(query)
    return R(status="success", data=[{"user": r["user"], "count": r["count"]} for r in results])


@router.get("/metrics/platform")
async def platform_list_get():
    """平台数据列表"""
    query = """
            SELECT command, platform, COUNT(id) AS count
            FROM system_command
            GROUP BY command, platform
        """

    results = await database_query(query)

    # 处理结果为嵌套字典
    data = {}
    for row in results:
        cmd = row["command"]
        platform = row["platform"]
        count = row["count"]
        if cmd not in data:
            data[cmd] = {}
        data[cmd][platform] = count

    return R(status="success", data=data)


@router.get("/metrics/word")
async def wordcloud_get():
    """获取词云"""
    top_n = 50
    query = "SELECT send_content FROM system_command"

    results = await database_query(query)

    # 分词处理
    words = []
    for row in results:
        if row['send_content']:
            words.extend(jieba.lcut(row['send_content']))

    # 统计词频
    counter = Counter(words)
    most_common = counter.most_common(top_n)

    # 返回格式化的结果
    return R(status="success", data=[{"word": w, "count": c} for w, c in most_common])


@router.get("/metrics/trend")
async def command_trend_get(command: str = Query(...)):
    """获取指令折线数据"""
    query = """
            SELECT 
                DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:00') AS hour,
                COUNT(id) AS count
            FROM system_command
            WHERE command = %s
            GROUP BY hour
            ORDER BY hour
        """
    results = await database_query(query, (command,))

    return R(status="success", data=[{"hour": r["hour"], "count": r["count"]} for r in results])
