"""血字相关数据处理"""

import random
from datetime import datetime

from .user import user_name
from config import database_query, database_update


async def blood_state(blood_id: int, target: str, start_time):
    """血字状态改变"""
    # 查询玩家当前状态
    player_info = await database_query(
        "SELECT id, alive FROM user_blood_player WHERE blood_id=%s AND user=%s",
        (blood_id, target)
    )

    if not player_info:
        nick = await user_name(target, "LR5921")
        return f"{nick} 未参与本次血字。"

    alive = player_info[0]["alive"]
    now = datetime.now()

    # 已死亡 → 复活
    if alive == 0:
        await database_update(
            "UPDATE user_blood_player SET alive=1, survival_duration=NULL WHERE blood_id=%s AND user=%s",
            (blood_id, target)
        )
        nick = await user_name(target, "LR5921")
        return f"{nick} 已被复活，存活时间已重新开始计算。"

    # 存活 → 死亡
    else:
        duration = int((now - start_time).total_seconds())
        await database_update(
            "UPDATE user_blood_player SET alive=0, survival_duration=%s WHERE blood_id=%s AND user=%s",
            (duration, blood_id, target)
        )
        nick = await user_name(target, "LR5921")
        death_descriptions = [
            "影子从 {nick} 身边逃脱。等众人发现时，他早已没了声息。",
            "{nick} 的影子忽然与本体错开了一步，像脱离了控制。下一秒，本体便像被抽空了一样倒了下去。",
            "{nick} 的影子突然抖动了一下，像被什么东西拽住。他整个人随之被拉进一片无形的缝隙。",
            "空气像被谁按下了静音键，{nick} 的声音被迫停在喉间。随后，他的影子比身体先倒了下去。",
            "有什么在暗处轻轻唤了 {nick} 的名字。他回头的瞬间，像是看到了自己正在褪色。",
            "黑色从 {nick} 的眼底透出，像墨浸进了一张纸。他还未来得及说话，整个人便安静地崩散了。",
            "墙角的阴影伸来一只细长的手指，轻轻点在了 {nick} 的眉心。他像被关机的机器一样瞬间沉寂。",
            "{nick} 的呼吸开始倒流，像被拉回了影子里。他的胸膛只起伏了半次，就再也没有动静。",
            "影子里传来第二个 {nick} 的脚步声，与他重叠、靠近，然后与他合为一体。他立刻失去了生命迹象。",
            "影子把 {nick} 围住，像一张无形的网。他眼中的光一点点被抽走，仿佛整个人被抹掉了。",
            "影子把 {nick} 的意识按入黑暗深处。他的身体还站着，但灵魂已被取走。",
            "影子把 {nick} 的呼吸夺走，像捂住了一盏灯。等灯灭时，他的身体无力倒下。",
            "影子把 {nick} 从背后抱住，那拥抱冰冷得像要融进骨头。他的动作越来越慢，最终静止不动。",
            "影子把 {nick} 的声音吞没。他张了张口，却再也发不出任何声响，只剩下一具安静的躯壳。",
            "影子把 {nick} 推入了一个看不见的深处。他的眼神逐渐空洞，像是被彻底带离了这个世界。",
            "影子把 {nick} 的心跳压住了。那一下沉默之后，心再也没能重新跳动。",
            "影子把 {nick} 的意识撕成碎片。他的身体瞬间僵硬，就像被无形力量夺走了生命。",
            "影子像有生命的墨，慢慢地沿着 {nick} 的身体爬了上来。",
            "一团无脸的黑在背后拍了拍他的肩膀，{nick} 顺着那只手走进了空白。",
            "影子在 {nick} 耳后轻轻吹息，所有能反抗的念头都像火苗被吹灭了。",
        ]
        text = random.choice(death_descriptions)
        text = text.format(nick=nick)
        return text

async def blood_person_query(player):
    """血字个人查询"""
    records = await database_query("""
                    SELECT 
                        b.name AS blood_name,
                        b.dm,
                        b.start_time,
                        p.survival_duration,
                        p.alive,
                        CASE WHEN b.mvp = p.user THEN 1 ELSE 0 END AS is_mvp
                    FROM user_blood_player p
                    JOIN user_blood b ON p.blood_id = b.id
                    WHERE p.user = %s AND b.duration > 0
                    ORDER BY b.id DESC
                """, (player,))

    if not records:
        return 0, f"用户 {player} 暂无已结束的血字记录。"

    headers = ["日期", "血字名称", "DM", "存活时长(分钟)", "状态/存活率", "MVP"]
    rows = []
    total_count = len(records)
    total_time = 0
    survive_count = 0
    mvp_count = 0
    for r in records:
        if r["start_time"]:
            date_str = r["start_time"].strftime("%Y.%m.%d")
        else:
            date_str = "--"
        duration_min = int((r["survival_duration"] or 0) // 60)
        total_time += r["survival_duration"] or 0
        status = "存活" if r["alive"] else "死亡"
        if r["alive"]:
            survive_count += 1
        if r["is_mvp"]:
            mvp_count += 1
        dm = await user_name(r["dm"], "LR5921")
        rows.append([
            date_str, r["blood_name"], dm, duration_min, status, "★" if r["is_mvp"] else ""
        ])
    avg_time_min = int((total_time / total_count) // 60) if total_count else 0
    survival_rate = survive_count / total_count * 100 if total_count else 0
    # 汇总行
    rows.append([
        "总计",
        f"{total_count}",
        "",
        f"{avg_time_min}",
        f"{survival_rate:.1f}%",
        f"{mvp_count}"
    ])
    return headers, rows


async def blood_person_query_all():
    """查询所有玩家总体血字表现"""
    records = await database_query("""
        SELECT 
            p.user,
            COUNT(*) AS total_games,
            SUM(p.alive) AS survived,
            SUM(CASE WHEN b.mvp = p.user THEN 1 ELSE 0 END) AS mvp_count,
            AVG(p.survival_duration) AS avg_survival
        FROM user_blood_player p
        JOIN user_blood b ON p.blood_id = b.id
        WHERE b.duration > 0
        GROUP BY p.user
        ORDER BY total_games DESC,survived DESC
    """)

    if not records:
        return 0, "暂无玩家参与记录。"

    headers = ["住户", "参与次数", "存活次数", "存活率(%)", "MVP次数", "平均生存时长(分钟)"]
    rows = []

    for r in records:
        name = await user_name(r["user"], "LR5921")
        total = r["total_games"]
        survived = r["survived"] or 0
        survival_rate = (survived / total) * 100 if total else 0
        avg_time = int((r["avg_survival"] or 0) // 60)
        rows.append([
            name,
            total,
            survived,
            f"{survival_rate:.1f}",
            r["mvp_count"] or 0,
            avg_time
        ])

    return headers, rows


async def blood_blood_query_all():
    """查询所有血字"""
    records = await database_query("""
                            SELECT 
                                b.name, b.dm,b.start_time,
                                GROUP_CONCAT(CASE WHEN p.alive=1 THEN p.user END) AS alive_users,
                                GROUP_CONCAT(CASE WHEN p.alive=0 THEN p.user END) AS dead_users,
                                SUM(p.alive)/COUNT(p.id)*100 AS survival_rate,
                                b.duration, b.mvp
                            FROM user_blood b
                            LEFT JOIN user_blood_player p ON b.id=p.blood_id
                            WHERE b.duration>0
                            GROUP BY b.id
                            ORDER BY b.id DESC
                        """)
    if not records:
        return 0, "暂无已结束血字。"

    headers = ["日期", "血字", "DM", "存活住户", "死亡住户", "存活率(%)", "总时长(分)", "MVP"]
    rows = []
    for r in records:
        if r["start_time"]:
            date_str = r["start_time"].strftime("%Y.%m.%d")
        else:
            date_str = "--"
        dm = await user_name(r['dm'], "LR5921")
        alive_users = "无"
        dead_users = "无"
        if r["alive_users"]:
            alive_ids = [u for u in r["alive_users"].split(",") if u]
            alive_names = [await user_name(uid, "LR5921") for uid in alive_ids]
            alive_users = "、".join(alive_names) if alive_names else "无"

        if r["dead_users"]:
            dead_ids = [u for u in r["dead_users"].split(",") if u]
            dead_names = [await user_name(uid, "LR5921") for uid in dead_ids]
            dead_users = "、".join(dead_names) if dead_names else "无"
        mvp_name = ""
        if r["mvp"]:
            mvp_name = await user_name(r["mvp"], "LR5921")
        rows.append([
            date_str,
            r["name"],
            dm,
            alive_users,
            dead_users,
            f"{float(r['survival_rate'] or 0):.1f}",
            f"{(r['duration'] or 0) // 60}",
            mvp_name
        ])
    return headers, rows


async def blood_blood_query(name):
    """查询某个血字"""
    if name.isdigit():
        records = await database_query("""
                    SELECT 
                        b.name, b.dm, b.start_time,
                        GROUP_CONCAT(CASE WHEN p.alive=1 THEN p.user END) AS alive_users,
                        GROUP_CONCAT(CASE WHEN p.alive=0 THEN p.user END) AS dead_users,
                        SUM(p.alive)/COUNT(p.id)*100 AS survival_rate,
                        b.duration, b.mvp
                    FROM user_blood b
                    LEFT JOIN user_blood_player p ON b.id=p.blood_id
                    WHERE b.dm=%s AND b.duration>0
                    GROUP BY b.id
                    ORDER BY b.id DESC
                """, (name,))
        if records:

            headers = ["日期", "血字名称", "存活住户", "死亡住户", "存活率(%)", "总时长(分)", "MVP"]
            rows = []
            for r in records:
                # 格式化日期
                date_str = r["start_time"].strftime("%Y.%m.%d") if r["start_time"] else "--"

                alive_users = "无"
                dead_users = "无"

                if r["alive_users"]:
                    alive_ids = [u for u in r["alive_users"].split(",") if u]
                    alive_names = [await user_name(uid, "LR5921") for uid in alive_ids]
                    alive_users = "、".join(alive_names) if alive_names else "无"

                if r["dead_users"]:
                    dead_ids = [u for u in r["dead_users"].split(",") if u]
                    dead_names = [await user_name(uid, "LR5921") for uid in dead_ids]
                    dead_users = "、".join(dead_names) if dead_names else "无"

                mvp_name = await user_name(r["mvp"], "LR5921") if r["mvp"] else "无"

                rows.append([
                    date_str,
                    r["name"],
                    alive_users,
                    dead_users,
                    f"{float(r['survival_rate'] or 0):.1f}",
                    f"{(r['duration'] or 0) // 60}",
                    mvp_name
                ])
            return headers, rows
    record = await database_query("""
                            SELECT b.id, b.name, b.dm, b.duration, b.mvp,b.start_time
                            FROM user_blood b
                            WHERE b.name=%s AND b.duration>0
                            ORDER BY b.id DESC LIMIT 1
                        """, (name,))
    if not record:
        return 0, f"未找到与⌈{name}⌋相关的已结束血字。"

    b = record[0]
    players = await database_query("""
                            SELECT user, alive, survival_duration FROM user_blood_player
                            WHERE blood_id=%s
                        """, (b["id"],))
    for p in players:
        p["user"] = await user_name(p["user"], "LR5921")
    headers = ["住户", "状态"]
    rows = [[p["user"], "存活" if p["alive"] else "死亡"] for p in players]
    total = len(players)
    survive = len([p for p in players if p["alive"]])
    survival_rate = survive / total * 100 if total else 0
    avg_time = int(sum(p["survival_duration"] or 0 for p in players) / total // 60) if total else 0
    mvp = await user_name(b['mvp'], "LR5921") if b['mvp'] else "无"
    date_str = b["start_time"].strftime("%Y.%m.%d") if b["start_time"] else "--"
    rows.append(["日期", date_str])
    rows.append(["参与住户", f"{total}"])
    rows.append(["存活率", f"{survival_rate:.1f}%"])
    rows.append(["总时长", f"{b['duration'] // 60}分"])
    rows.append(["平均存活", f"{avg_time}分"])
    rows.append(["MVP", mvp])
    return headers, rows
