"""订阅查询相关"""
import asyncio
import datetime

from .file import bv_download
from message.handler.msg import Msg
from .system import system_get, system_edit
from config import database_update, database_query, scheduler_add, future, path, loggers, config

up = []


async def subscribe_data(user, sub, info):
    """订阅"""
    query = """
                    INSERT INTO user_subscribe (user, sub,info)
                    VALUES (%s, %s,%s) AS new
                    ON DUPLICATE KEY UPDATE info = new.info
                """
    await database_update(query, (user, sub, info))


async def subscribe_delete(user, sub_id):
    """删除某个用户的订阅"""
    rows = await database_query(
        "SELECT id, info FROM user_subscribe WHERE user = %s AND id = %s",
        (user, sub_id)
    )
    if not rows:
        return f"未找到订阅 {sub_id}，请检查编号是否正确"

    await database_update(
        "DELETE FROM user_subscribe WHERE id = %s AND user = %s",
        (sub_id, user)
    )
    return f"已取消订阅：{rows[0]['info']}"


async def subscribe_check(user):
    """列出用户当前订阅"""
    rows = await database_query(
        "SELECT id, info FROM user_subscribe WHERE user = %s",
        (user,)
    )
    if not rows:
        return "您还没有订阅任何内容"

    return "\n".join(f"{row['id']}: {row['info']}" for row in rows)


async def subscribe_activity():
    """订阅活动提醒"""
    rows = await database_query(
        "SELECT user FROM user_subscribe WHERE sub = %s",
        ("activity",)
    )

    for row in rows:
        content = await system_get("activity")
        content = "活动更新\n\n" + content
        Msg(
            platform="LR5921",
            kind="私聊发送",
            event="发送",
            user=row["user"],
            content=content
        )


async def subscribe_up(user, mid, name):
    """订阅 b 站 up"""
    sub = f"up_{mid}"
    query = """
            INSERT INTO user_subscribe (user, sub,info)
            VALUES (%s, %s,%s) AS new
            ON DUPLICATE KEY UPDATE info = new.info
        """
    await database_update(query, (user, sub, name))

    # 更新其他订阅的 up 名称
    await database_update(
        "UPDATE user_subscribe SET info = %s WHERE sub = %s",
        (name, sub)
    )

    if mid not in up:
        scheduler_add(subscribe_up_query, mid, interval=600, at_once=True)
        up.append(mid)


async def subscribe_up_query(mid):
    """定期查询 up 视频"""
    sub = f"up_{mid}"
    msg = Msg(
        platform="BILI",
        kind="私聊用户视频",
        event="发送",
        user=mid,
    )
    response = await future.wait(msg.num, f"[消息]用户视频获取超时-> {mid}")
    bv = response[0].get("bvid")
    title = response[0].get("title")
    last_bv = await system_get(sub)
    if last_bv and bv != last_bv:
        await system_edit(sub, bv)

        rows = await database_query(
            "SELECT user, info FROM user_subscribe WHERE sub = %s",
            (sub,)
        )

        for row in rows:
            user = row["user"]
            name = row["info"]

            content = f"[{name}]最新视频->\n\n{title}"
            Msg(
                platform="LR5921",
                kind="私聊发送",
                event="发送",
                user=user,
                content=content
            )


async def subscribe_up_init():
    """加载所有 up 订阅"""
    global up
    # 早上好
    scheduler_add(subscribe_core, "morning", 6, 15, interval=600)
    # 晚安
    scheduler_add(subscribe_core, "evening", 21, 23, interval=600)

    # 其他
    rows = await database_query("SELECT DISTINCT sub FROM user_subscribe")

    for row in rows:
        sub = row["sub"]
        if sub.startswith("up_"):
            mid = sub[3:]
            up.append(mid)
            scheduler_add(subscribe_up_query, mid, interval=600)


async def subscribe_core(phase, start_h, end_h):
    """查询并下载"""
    now = datetime.datetime.now()
    if not (start_h <= now.hour <= end_h):
        return

    time = await system_get(f"subscribe_{phase}")
    today_str = now.strftime("%Y%m%d")
    if time == today_str:
        return  # 今天已发过

    response = await subscribe_collection_fetch(phase, "true")
    bv = response[0].get("bvid")
    ctime = response[0].get("pubdate")  # 发表时间不等于上传时间

    today_zero = int(datetime.datetime.combine(now.date(), datetime.time.min).timestamp())
    valid = today_zero <= ctime < today_zero + 86400 and start_h <= datetime.datetime.fromtimestamp(ctime).hour <= end_h
    if not valid:
        # 不是今天发的/不在时段
        response = await subscribe_collection_fetch(phase, "false")
        bv = response[0].get("bvid")
        ctime = response[0].get("pubdate")
        valid = today_zero <= ctime < today_zero + 86400 and start_h <= datetime.datetime.fromtimestamp(
            ctime).hour <= end_h

    if not valid:
        return

    record = path / f"storage/file/command/{phase}_{today_str}.wav"
    for file in (path / "storage/file/command").glob(f"{phase}_*.wav"):
        try:
            file.unlink()
        except Exception as e:
            loggers["message"].error(
                f"[文件删除]旧文件删除失败-> {file}: {e}",
                extra={"event": "文件处理"},
            )
    await bv_download(bv, record)

    rows = await database_query(
        "SELECT user FROM user_subscribe WHERE sub = %s",
        (phase,)
    )
    for r in rows:
        Msg(
            platform="LR5921",
            kind="私聊发送",
            event="发送",
            user=r["user"],
            content=f"[语音:{record}]"
        )
        await asyncio.sleep(2)
        
    await system_edit(f"subscribe_{phase}", today_str)


async def subscribe_collection_fetch(phase, order):
    """获取合集"""
    if phase == "morning":
        user = "4729816"
        collection = "4600896"
    else:
        user = "484322035"
        collection = "4417802"
    msg = Msg(
        platform="BILI",
        kind="私聊用户合集",
        event="发送",
        content=f"{collection}|{order}",
        user=user
    )
    response = await future.wait(msg.num, f"[消息]订阅视频获取超时-> {phase}")
    return response
