"""用户界面"""

from config import config, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Dict

router = APIRouter()


@router.get("/users")
async def get_users():
    """获取用户组"""
    return R(status="success", data={"private_users": config["private"], "group_users": config["public"]})


@router.put("/users")
@monitor_adapter("#内阁_用户更新")
async def update_users(data: Dict, account: str = Depends(cookie_account_get)):
    """更新用户组"""
    if not account:
        return
    try:
        private_users = data["private_users"]
        group_users = data["group_users"]
        private_diff = user_compare(config["private"], private_users)
        group_diff = user_compare(config["public"], group_users)
        config["private"] = private_users
        config["public"] = group_users
        website_logger.info(
            f"[用户组更新]{account}-> 私聊: {private_diff} | 群聊: {group_diff}",
            extra={"event": "网页日志"},
        )
        return R(status="success", data=f"私聊: {private_diff} | 群聊: {group_diff}")

    except Exception as e:
        website_logger.error(f"[用户页]更新失败-> {type(e).__name__}: {e}", extra={"event": "网页日志"})


def user_compare(old, new):
    """用户组前后对比"""
    old_keys, new_keys = set(old.keys()), set(new.keys())

    added = {k: new[k] for k in (new_keys - old_keys)}
    removed = {k: old[k] for k in (old_keys - new_keys)}

    changed = {}
    for k in old_keys & new_keys:
        old_values = set(old[k])
        new_values = set(new[k])
        if old_values != new_values:
            added_items = list(new_values - old_values)
            removed_items = list(old_values - new_values)
            changed[k] = {"新增项": added_items, "删除项": removed_items}

    return f"新增: {added} | 删除: {removed} | 变更: {changed}"
