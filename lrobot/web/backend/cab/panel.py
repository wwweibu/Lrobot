"""功能展板"""

import json

from logic import docs_merge
from config import database_update, database_query, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Dict


router = APIRouter()
PANEL_CONFIGS = [
    ("测试说明", "此页面功能说明与测试要求", "/hjd/static/panel/1.jpg"),
    ("系统", "用户和系统", "/hjd/static/panel/2.png"),
    ("基础", "基础指令", "/hjd/static/panel/3.png"),
    ("入会", "入会流程", "/hjd/static/panel/4.png"),
    ("收集表", "用户反馈及活动收集", "/hjd/static/panel/5.png"),
    ("游戏", "小游戏", "/hjd/static/panel/6.png"),
    ("工具", "实用", "/hjd/static/panel/7.png"),
    ("订阅", "订阅提醒", "/hjd/static/panel/8.png"),
    ("活动", "线上活动/活动助手", "/hjd/static/panel/9.png"),
    ("待办", "待办事项汇总", "/hjd/static/panel/1.gif"),
    ("官网", "官网主页", "/hjd/static/panel/20.png"),
    ("登录页", "登录", "/hjd/static/panel/21.png"),
    ("wiki页", "内阁wiki", "/hjd/static/panel/22.png"),
    ("网盘页", "内阁网盘", "/hjd/static/panel/23.png"),
    ("时间轴页", "协会活动时间", "/hjd/static/panel/24.png"),
    ("指令页", "系统指令面板", "/hjd/static/panel/25.png"),
    ("数据库页", "系统数据库", "/hjd/static/panel/26.png"),
    ("日志页", "系统日志", "/hjd/static/panel/27.png"),
    ("用户页", "系统用户组配置", "/hjd/static/panel/28.png")
]

@router.get("/firefly")
async def firefly_get():
    """获取展板信息"""
    panels = []
    all_funcs = []
    panel_meta = []

    for idx, panel_config in enumerate(PANEL_CONFIGS, start=1):
        name, description, url = panel_config
        func_docs = docs_merge(name, help_mode=False)
        tasks_meta = []
        for func_name, info in func_docs.items():
            tasks_meta.append({
                "func": func_name,
                "title": info.get("title", func_name),
                "lines": info.get("lines", []),
            })
            all_funcs.append(func_name)
        panel_meta.append((idx, name, description, url, tasks_meta))

    unique_funcs = list(dict.fromkeys(all_funcs))
    answers_map = {}
    if unique_funcs:
        placeholders = ",".join(["%s"] * len(unique_funcs))
        query = f"SELECT func, answer FROM system_panel WHERE func IN ({placeholders})"
        rows = await database_query(query, tuple(unique_funcs))
        for r in rows:
            answers_map[r["func"]] = json.loads(r["answer"])

    for (idx, name, description, url, tasks_meta) in panel_meta:
        panels.append({
            "id": idx,
            "name": name,
            "description": description,
            "imageUrl": url,
            "tasks": tasks_meta
        })

    return R(status="success", data={"panels": panels, "answers": answers_map})


@router.post("/firefly")
@monitor_adapter("#内阁_功能评论")
async def firefly_update(data: Dict, account: str = Depends(cookie_account_get)):
    """上传展板评论"""
    if not account:
        return

    updates = data.get("updates")
    funcs = [u["func"] for u in updates if "func" in u]
    if not funcs:
        return R(status="fail", data="没有有效的 func")
    placeholders = ",".join(["%s"] * len(funcs))
    select_q = f"SELECT func, answer FROM system_panel WHERE func IN ({placeholders})"
    rows = await database_query(select_q, tuple(funcs))
    old_map = {r["func"]: json.loads(r["answer"]) for r in rows}
    diffs = []

    insert_q = "INSERT INTO system_panel (func, answer) VALUES (%s, %s) ON DUPLICATE KEY UPDATE answer = %s"
    for u in updates:
        func = u.get("func")
        title = u.get("title", func)
        new_answers = u.get("answers", [])
        if not isinstance(new_answers, list):
            new_answers = [new_answers]

        old_answers = old_map.get(func, [])
        added = [a for a in new_answers if a not in old_answers]
        removed = [a for a in old_answers if a not in new_answers]

        if added or removed:
            diffs.append({"func": func, "title": title, "added": added, "removed": removed})

        # upsert（新存在则插入，已存在则更新）
        answer_json = json.dumps(new_answers, ensure_ascii=False)
        await database_update(insert_q, (func, answer_json, answer_json))

    for d in diffs:
        if d["added"] and not d["removed"]:
            action = "新增"
            change = d["added"]
        elif d["removed"] and not d["added"]:
            action = "删除"
            change = d["removed"]
        else:
            action = "修改"
            change = {"added": d["added"], "removed": d["removed"]}
        website_logger.info(f"[{action}评论]{account}-> {d['title']}: {change}", extra={"event": "网页日志"})

    return R(status="success", data={"diffs": diffs})
