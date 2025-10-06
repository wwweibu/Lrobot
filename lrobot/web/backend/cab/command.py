"""指令列表"""

from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Request, Dict
from config import config, monitor_adapter

router = APIRouter()


@router.get("/commands")
async def commands_get():
    """获取指令"""
    commands = config["commands"]
    chat_users = config["private"]
    chat_groups = config["public"]
    events = config["kind"]
    states = config["status"]
    users = list(chat_users.keys())  # 只获取键
    groups = list(chat_groups.keys())

    return R(status="success", data={
        "commands": commands,
        "events": events,
        "states": states,
        "users": users,
        "groups": groups,
    })


@router.put("/commands")
@monitor_adapter("#内阁_指令上传")
async def commands_update(data: Dict, account: str = Depends(cookie_account_get)):
    """更新指令"""
    if not account:
        return
    try:
        new_commands = data["commands"]
        if not isinstance(new_commands, list):
            return R(status="fail", data=f"指令集更新错误 | 数据:{new_commands}")
        old_commands = config["commands"]
        config["commands"] = new_commands
        diff = command_compare(old_commands, new_commands)
        website_logger.info(
            f"[指令更新]{account}-> {diff})", extra={"event": "网页日志"}
        )
        return R(status="success", data=diff)
    except Exception as e:
        website_logger.error(f"[指令页]更新错误-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
        return R(status="fail", data=f"指令集更新错误 | {e}")


def command_compare(old: list, new: list):
    """比较新旧字典的差异"""
    old_map = {cmd["func"]: cmd for cmd in old}
    new_map = {cmd["func"]: cmd for cmd in new}

    added = [new_map[func] for func in new_map if func not in old_map]
    removed = [old_map[func] for func in old_map if func not in new_map]
    modified = []

    # 检查修改的指令
    for func in (set(old_map) & set(new_map)):
        old_cmd = old_map[func]
        new_cmd = new_map[func]
        if old_cmd != new_cmd:
            modified.append({
                "func": func,
                "changes": diff_find(old_cmd, new_cmd)
            })

    return f"新增: {added} | 删除: {removed} | 修改: {modified}"


def diff_find(d1: dict, d2: dict):
    """找出两个字典的差异字段"""
    keys = set(d1) | set(d2)
    diff = {}
    for k in keys:
        v1 = d1.get(k)
        v2 = d2.get(k)
        if v1 != v2:
            diff[k] = {"old": v1, "new": v2}
    return diff
