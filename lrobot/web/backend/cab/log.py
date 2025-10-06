"""日志查询界面"""

import re
from datetime import datetime

from config import mongo_get
from .base import APIRouter, Dict, R, website_logger

router = APIRouter()
mongo_db = mongo_get()


@router.post("/logs")
async def log_get(data: Dict):
    """日志获取"""
    try:
        page = max(int(data.get("page", 1)), 1)
        page_size = min(max(int(data.get("page_size", 100)), 1), 500)
        level = data.get("level", "base")
        source = data.get("source", "all")
        event = data.get("event")
        keyword = data.get("keyword", "")
        regex_pattern = data.get("regex", "")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        query = {}

        if level:
            level_upper = level.upper()
            if level_upper == "BASE":
                query["level"] = {"$in": ["INFO", "ERROR"]}
            elif level_upper == "ALL":
                pass
            else:
                query["level"] = level_upper
        if source:
            if source == "all":
                pass
            elif source == "base":
                query["source"] = {"$in": ["system", "website", "adapter", "message"]}
            elif source == "msg":
                query["source"] = {"$in": ["adapter", "message"]}
            else:
                query["source"] = source
        if event:
            if event == "消息处理&堆栈":
                query.clear()
                query["$or"] = [
                    {"level": "DEBUG", "event": "错误堆栈", "source": "system",
                     "message": {"$regex": "^[消息处理]"}},
                    {"event": "消息处理", "source": "message"}
                ]
            elif event == "消息接收&消息去重&消息超时":
                query["event"] = {"$in": ["消息接收", "消息去重", "消息超时"]}
            elif event == "定时任务&堆栈":
                query.clear()
                query["source"] = "system"
                query["$or"] = [
                    {"level": "DEBUG", "event": "错误堆栈",
                     "message": {"$regex": "^[定时任务]"}},
                    {"level": "ERROR", "event": "定时任务"}
                ]
            elif event == "!网页日志&错误堆栈":
                query.clear()
                query["$or"] = [
                    {"level": "DEBUG", "event": "错误堆栈", "source": "system",
                     "message": {"$regex": "^[后端运行]"}},
                    {"event": {"$ne": "网页日志"}, "source": "website"}
                ]
            elif event == "!错误堆栈&定时任务":
                query["event"] = {"$nin": ["错误堆栈", "定时任务"]}
            else:
                query["event"] = event
        if start_time or end_time:
            query_time = {}
            try:
                if start_time:
                    query_time["$gte"] = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                if end_time:
                    query_time["$lte"] = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                if query_time:
                    query["time"] = query_time
            except ValueError as ve:
                return R(status="fail", data=f"时间格式错误: {ve}")
        if regex_pattern:
            try:
                re.compile(regex_pattern)
                query["message"] = {"$regex": regex_pattern}
            except re.error:
                return R(status="fail", data="非法正则表达式")
        elif keyword:
            safe_keyword = re.escape(keyword.strip())
            if safe_keyword:
                query["$text"] = {"$search": safe_keyword}
                query["hasTextIndex"] = True
        website_logger.debug(
            f"[日志页]查询字段-> {query}", extra={"event": "网页日志"}
        )

        projection = {"_id": 1, "time": 1, "source": 1, "level": 1, "event": 1, "message": 1}

        coll = mongo_db.system_log
        skip = (page - 1) * page_size
        total = await coll.count_documents(query)
        cursor = coll.find(query, projection).sort("time", -1).skip(skip).limit(page_size)
        explanation = await cursor.explain()
        website_logger.debug(
            f"[日志页]查询结果-> {explanation['queryPlanner']['winningPlan']}", extra={"event": "网页日志"}
        )
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
    except Exception as e:
        website_logger.error(
            f"[日志页]查询错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"}
        )
        return R(status="fail", data=f"查询错误: {e}")

    return R(status="success", data={"data": results, "total": total})
