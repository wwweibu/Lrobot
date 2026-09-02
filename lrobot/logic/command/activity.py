"""活动相关"""

import re
import json
from datetime import datetime

from logic import data
from message.handler.msg import Msg
from config import (
    config,
    create_background_task,
    database_query,
    database_update,
    future,
    monitor_adapter,
    path,
)


NAVY_CONFIG_PATH = path / "storage/file/command/navy/config.json"

@monitor_adapter("/活动_日记_开始")
async def activity_diary_start(msg: Msg):
    """日记开始答题"""
    await data.status_add(msg.user, msg.platform, "日记", 1)
    content = f"[图片:{path}/storage/file/command/diary/1.png]"
    content += ("谨记答案格式：连续的小写字母、数字或中文，无空格\n"
                "陷入困境时，可调阅'/提示'获取指引\n"
                "进度已支持多平台同步\n"
                "独立发现的真相，往往更加甘美\n")

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_日记_提示")
async def activity_diary_prompt(msg: Msg):
    """日记提示"""
    id = await data.status_check(msg.user, msg.platform, "日记")
    try:
        id = int(id)
    except (ValueError, TypeError):
        content = "日记 ID 错误"
    else:
        diary_file = path / "storage/file/command/diary/answer.txt"
        if not diary_file.exists():
            content = "日记题目文件不存在"
        else:
            lines = diary_file.read_text(encoding="utf-8").splitlines()
            # 去除空行，保证每两行一组
            lines = [l.strip() for l in lines if l.strip()]
            # 按两行一组（提示, 答案）
            groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]

            if id < 1 or id > len(groups):
                content = f"未找到 ID 为 {id} 的日记题目"
            else:
                prompt = groups[id - 1][0]
                content = f"提示: {prompt}"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


async def activity_diary_judge(msg: Msg):
    """日记答题判断"""
    id = await data.status_check(msg.user, msg.platform, "日记")
    try:
        id = int(id)
    except (ValueError, TypeError):
        return False
    diary_file = path / "storage/file/command/diary/answer.txt"
    if not diary_file.exists():
        return False
    lines = diary_file.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in lines if l.strip()]
    groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]

    if id < 1 or id > len(groups):
        return False
    correct_answer = groups[id - 1][1].strip()
    user_answer = Msg.content_join(msg.content).strip()
    if user_answer == correct_answer:
        return True
    return False


@monitor_adapter("/活动_日记_答题")
async def activity_diary_answer(msg: Msg):
    """日记答题"""
    id = await data.status_check(msg.user, msg.platform, "日记")
    id = int(id)
    if id == 16:
        await data.status_delete(msg.user, msg.platform, "日记")
    else:
        await data.status_add(msg.user, msg.platform, "日记", id + 1)
    content = f"[图片:{path}/storage/file/command/diary/{id + 1}.png]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_七年之约_开始")
async def activity_appointment_start(msg: Msg):
    """七年之约开始答题"""
    await data.status_add(msg.user, msg.platform, "七年之约", 1)
    base = f"{path}/storage/file/command/appointment"
    content = (f"[图片:{base}/1.PNG]"
               "陷入困境时，可调阅'/提示'获取指引\n"
               "进度已支持多平台同步\n"
               "输入'七年之约'将重新开始\n"
               "独立发现的真相，往往更加甘美\n"
                "紧要关头再试着求助小推1326016706吧~\n"
                "注意答案中没有空格，标点符号，除第九题外无中文数字")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content

@monitor_adapter("/活动_七年之约_提示")
async def activity_appointment_prompt(msg: Msg):
    """七年之约提示"""
    from config import loggers
    id = await data.status_check(msg.user, msg.platform, "七年之约")
    try:
        id = int(id)
    except (ValueError, TypeError):
        content = "七年之约 ID 错误"
    else:
        if id == 15:
            content = "提示: 换句话说，没有数字存在的图片的信息，绝对绝对正确，绝对绝对可信，找出没数字存在的图片中的异常吧"
        else:
            answer_file = path / "storage/file/command/appointment/answer.txt"
            if not answer_file.exists():
                content = "题目文件不存在"
            else:
                lines = answer_file.read_text(encoding="utf-8").splitlines()
                lines = [l.strip() for l in lines if l.strip()]
                groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]
                if id < 1 or id > len(groups):
                    content = f"未找到 ID 为 {id} 的题目"
                else:
                    content = f"提示: {groups[id - 1][0]}"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content

async def activity_appointment_judge(msg: Msg):
    """七年之约答题判断"""
    id = await data.status_check(msg.user, msg.platform, "七年之约")
    try:
        id = int(id)
    except (ValueError, TypeError):
        return False
    user_answer = Msg.content_join(msg.content).strip()
    # 第15题：结局选择（AB按序排列组合）
    if id == 15:
        return user_answer.upper() in {
            "A", "B", "AB",
            "AC", "AD", "BC", "BD", "CD",
            "C", "D",
            "ABC", "ABD", "ACD", "BCD",
            "ABCD"
        }
    # 1-14题
    answer_file = path / "storage/file/command/appointment/answer.txt"
    if not answer_file.exists():
        return False
    lines = answer_file.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in lines if l.strip()]
    groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]
    if id < 1 or id > len(groups):
        return False
    return user_answer == groups[id - 1][1].strip()

@monitor_adapter("/活动_七年之约_答题")
async def activity_appointment_answer(msg: Msg):
    """七年之约答题"""
    id = await data.status_check(msg.user, msg.platform, "七年之约")
    id = int(id)
    base = f"{path}/storage/file/command/appointment"
    # 第15题：结局选择，不删除状态
    if id == 15:
        answer = Msg.content_join(msg.content).strip().upper()
        if answer == "AB":
            content = f"[图片:{base}/16-1.PNG]"
        elif answer == "A":
            content = f"[图片:{base}/16-2.PNG]"
        elif answer == "B":
            content = f"[图片:{base}/16-3.PNG]"
        else:
            content = f"[图片:{base}/16-4.PNG]"
        content+="您已游玩完全部题目！可以输入其它选项查看别的结局！也欢迎进群讨论！"
        Msg(
            platform=msg.platform,
            event="发送",
            kind=f"{msg.kind[:2]}发送",
            seq=msg.seq,
            content=content,
            user=msg.user,
            group=msg.group,
        )
        return content
    # 1-14题
    next_id = id + 1
    await data.status_add(msg.user, msg.platform, "七年之约", next_id)
    # 发送下一题图片
    if next_id in (2, 8, 12):
        content = f"[图片:{base}/{next_id}-1.PNG][图片:{base}/{next_id}-2.PNG]"
    elif next_id == 15:
        content = f"[图片:{base}/15-1.PNG][图片:{base}/15-2.PNG]"
    else:
        content = f"[图片:{base}/{next_id}.PNG]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


def _send(msg: Msg, content):
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_海军案_开始")
async def activity_navy_start(msg: Msg):
    """海军案开始"""
    state = {
        "unlocked": ["贝克街221B"],
        "places": [],
        "persons": [],
        "combinations": [],   # 形如 "A||B"，方向敏感（A+B 与 B+A 分别记录）
    }
    await data.status_add(msg.user, msg.platform, "海军案",
                          json.dumps(state, ensure_ascii=False))
    content = ("指令:\n"
               "地点/人物（当前解锁:地点[贝克街221B]）\n"
               "人物+人物\n"
               "调查完成+xxx\n"
               "解锁查询\n"
               "游戏规则:\n"
               "0.简洁版:从贝克街221B开始，你可以输入返回的信息中解锁的'人物'，'地点'，'人物+人物'三种信息，解锁新的信息(如输入人名'A'，解锁地名'B'，人名'C'、'D'，可以继续输入B\C\D\C+D\D+C\A+C\A+D\D+A\C+A)。忘记信息时可以输入'解锁查询'进行查询\n"
               "1.在这次的游戏中玩家们扮演的是福尔摩斯的助手华生医生。在委托人来访的故事中会有注明是关键字的词语，在后面的故事中这样的关键字依旧会出现。这些关键字包含了涉及进这起案件的所有人物以及一些可能让诸位生疑的话题或地点。在公众号中回复地点或者人物类的关键字即代表华生医生前往该地点或者这个人通常会出现的地方，而在遭遇了要拜访的人之后会进入对话的阶段，此时回复询问的人+想询问的话题（所有人物），如回复'福尔摩斯+布莱恩先生'就相当于向福尔摩斯聊起布莱恩先生的事。注意，加号前后的词语务必严格按照我们给出的关键词。只要关键词没有错误，即使被询问的人对此一无所知，也都会有相应的反应。\n"
               "2.福尔摩斯先生在调查的过程中一直保持着思考，因此往往快人一步。踏破每一条线索固然是解开谜题的一种方法，但我们更鼓励更谨慎地边思考边进行游戏。每使用一个要拜访的人或地点，即一级的关键字，记为5分，同时在对话开始后每询问一个话题（所有人物），即每使用一个二级的关键字额外再记一分。当同样解开案件时，分数越低即使用线索越少者则为表现得更出色。\n"
               "3.当线索齐全时，游戏不会给出明显的标志。当认为自己已经解开案件的真相时，即可向我们提交答案，输入'调查完成+xxx'要求必须包括凶手的身份以及推断的理由。")
    return _send(msg, content)


async def activity_navy_judge(msg: Msg):
    """判断输入是否为海军案的有效关键字格式：
    地名 / 人名 / 人名+人名（A、B 均为人名）。允许任意位置含空格。
    其中 '调查完成…' 与 '解锁查询' 由静态指令优先匹配，这里无需排除。
    """
    raw = await data.status_check(msg.user, msg.platform, "海军案")
    if not raw or not NAVY_CONFIG_PATH.exists():
        return False
    config = json.loads(NAVY_CONFIG_PATH.read_text(encoding="utf-8"))
    places = config.get("places", {}) or {}
    persons = config.get("persons", {}) or {}
    text = re.sub(r"\s+", "", Msg.content_join(msg.content) or "")
    if not text:
        return False
    if re.search(r"[+＋]", text):
        a, b = re.split(r"[+＋]", text, maxsplit=1)
        return a in persons and b in persons
    return text in places or text in persons

@monitor_adapter("/活动_海军案_解锁查询")
async def activity_navy_query(msg: Msg):
    """解锁查询：列出当前已解锁的地点与人名"""
    raw = await data.status_check(msg.user, msg.platform, "海军案")
    if not raw or not NAVY_CONFIG_PATH.exists():
        return
    state = json.loads(raw)
    config = json.loads(NAVY_CONFIG_PATH.read_text(encoding="utf-8"))
    places = config.get("places", {}) or {}
    persons = config.get("persons", {}) or {}
    avail_places = [p for p in state["unlocked"] if p in places]
    avail_persons = [p for p in state["unlocked"] if p in persons]
    content = (
        "当前已解锁：\n"
        f"地点：{', '.join(avail_places) or '无'}\n"
        f"人物：{', '.join(avail_persons) or '无'}\n"
        "（任意两位已解锁人物均可使用'A+B'询问）\n"
        "也可询问'地名','人物'相关信息\n"
        "输入'调查完成+结论'进行结案并重置游戏"
    )
    return _send(msg, content)

@monitor_adapter("/活动_海军案_答题")
async def activity_navy_answer(msg: Msg):
    """海军案关键字应答"""
    raw = await data.status_check(msg.user, msg.platform, "海军案")
    if not raw or not NAVY_CONFIG_PATH.exists():
        return
    state = json.loads(raw)
    config = json.loads(NAVY_CONFIG_PATH.read_text(encoding="utf-8"))

    text = re.sub(r"\s+", "", Msg.content_join(msg.content) or "")
    unlocked = set(state["unlocked"])
    places = config.get("places", {}) or {}
    persons = config.get("persons", {}) or {}

    content = None

    if re.search(r"[+＋]", text):
        # ---- 二级：人名+人名 ----
        a, b = re.split(r"[+＋]", text, maxsplit=1)
        a, b = a.strip(), b.strip()
        # A、B 都必须是已解锁的"人名"（不接受地名）
        if a not in persons or a not in unlocked:
            content = "你尚未掌握这条线索。"
        elif b not in persons or b not in unlocked:
            content = "你尚未掌握这条线索。"
        else:
            combos_a = (persons[a] or {}).get("combinations", {}) or {}
            specific = b in combos_a
            info = combos_a.get(b) or combos_a.get("others") or {}
            dialogue = info.get("dialogue") or f"{a}对{b}的事一无所知。"
            # 若此前未直接触发过 A，隐含记一次（一级 5 分）
            if a not in state["persons"]:
                state["persons"].append(a)
            # 仅在精确匹配时计入二级 1 分；走 others 不计分
            # A+B 与 B+A 方向敏感，分别计分
            if specific:
                key = f"{a}||{b}"
                if key not in state["combinations"]:
                    state["combinations"].append(key)
            for k in info.get("unlocks", []) or []:
                if k not in state["unlocked"]:
                    state["unlocked"].append(k)
            content = dialogue
    else:
        # ---- 一级：地名 ----
        if text in places:
            if text not in unlocked:
                content = "你尚未掌握这条线索。"
            else:
                info = places[text] or {}
                if text not in state["places"]:
                    state["places"].append(text)
                for k in info.get("unlocks", []) or []:
                    if k not in state["unlocked"]:
                        state["unlocked"].append(k)
                content = info.get("dialogue", "")

        # ---- 一级：人名 ----
        if content is None and text in persons:
            if text not in unlocked:
                content = "你尚未掌握这条线索。"
            else:
                info = persons[text] or {}
                if text not in state["persons"]:
                    state["persons"].append(text)
                for k in info.get("unlocks", []) or []:
                    if k not in state["unlocked"]:
                        state["unlocked"].append(k)
                content = info.get("dialogue", "")

    if content is None:
        content = "（其他关键字）暂无相关信息。"

    await data.status_add(msg.user, msg.platform, "海军案",
                          json.dumps(state, ensure_ascii=False))
    return _send(msg, content)


@monitor_adapter("/活动_海军案_结束")
async def activity_navy_end(msg: Msg):
    """海军案结束（'调查完成+答案'触发）。
    将"调查完成"之外的内容（含凶手身份与推断理由）转发给管理员，
    然后回复用户结算结果并清状态。
    分数越低越好：地名/人名各扣 5，二级组合每次扣 1。"""
    raw = await data.status_check(msg.user, msg.platform, "海军案")
    if not raw:
        return
    state = json.loads(raw)

    text = Msg.content_join(msg.content).strip()
    m = re.match(r"^调查完成[\+＋]?(.*)$", text, flags=re.S)
    answer = m.group(1).strip() if m else ""
    name = await data.user_name(msg.user, msg.platform)

    places = state["places"]
    persons = state["persons"]
    combos = state["combinations"]
    combo_show = [c.replace("||", "+") for c in combos]
    clues_text = (
        f"地名（{len(places)}）：{', '.join(places) or '无'}\n"
        f"人名（{len(persons)}）：{', '.join(persons) or '无'}\n"
        f"问询（{len(combos)}）：{', '.join(combo_show) or '无'}"
    )

    # 转发到管理员（参考 base.py base_word 留言转发模式），含使用线索（无分数）
    if answer:
        forward = (
            "来自" + name + "的调查完成--" + answer
            + "\n【使用线索】\n" + clues_text
        ).replace("[", "").replace("]", "")
        Msg(
            platform="LR5921",
            event="发送",
            kind="私聊发送",
            content=forward,
            user=config["private"]["微部"][0],
        )

    score = len(places) * 5 + len(persons) * 5 + len(combos)
    content = (
        f"侦探 {name} 的调查结案\n"
        + clues_text + "\n"
        + f"使用线索分数：{score}（分数越低越出色）\n"
        "已将结案报告呈递给管理员，如有需要可联系小推qq1326016706商量后续事宜"
    )
    await data.status_delete(msg.user, msg.platform, "海军案")
    return _send(msg, content)


@monitor_adapter("/活动_血字_帮助")
async def activity_blood_help(msg: Msg):
    """血字帮助"""
    content = ("在玩耍地和水群中可开血字，限内阁成员使用。\n"
               "输入'/血字开始'开始血字，随后输入血字名称，随后输入'/血字@张三@李四……'(必须连续)\n"
               "血字中某人死亡时，使用'/血字死亡@张三@李四……'(可以是回复张三的消息，那样会自动@张三，只需要包含/血字死亡，可以在后面向张三描述死亡过程)\n"
               "或者主持人戳一戳对方即可标记其为死亡\n"
               "血字结束时，使用'/血字结束'结束当前血字\n"
               "使用'/血字MVP@张三'来设置血字MVP(限一个，可结束后设置)\n"
               "使用'/血字查询'可查询血字记录\n"
               "血字死亡可以反复死亡，MVP也可以反复设置\n"
               "注意：同一时间只能开启一个血字")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

    return content

@monitor_adapter("/活动_血字_开始_1")
async def activity_blood_start1(msg: Msg):
    """血字开始"""
    if msg.group not in config["public"]["公测群"] and msg.group not in config["public"]["内测群"]:
        identity_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" not in identity_list:
            content = "阁下，开启血字的权限仅限于内阁成员。"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
                user=msg.user,
                group=msg.group,
            )

            return content
    ongoing = await database_query(
        "SELECT id, name, dm, start_time FROM user_blood WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
    )
    if ongoing:
        b = ongoing[0]
        dm_name = await data.user_name(b["dm"], msg.platform)
        start_time = b["start_time"].strftime("%m-%d %H:%M")
        content = f"阁下，血字⌈{b['name']}⌋仍在进行中，由 {dm_name} 主持（开始于 {start_time}）。请先结束该血字后再开启新的。"
    else:
        content = "请请您为本次血字命名，系统将自动记录您为主持人。"
        await data.status_add(msg.user, msg.platform, "血字1")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

    return content


@monitor_adapter("/活动_血字_开始_2")
async def activity_blood_start2(msg: Msg):
    """血字名称"""
    content = "请输入'/血字'并@所有住户以完成召集。建议您先单独@一次，确认诸位住户均已就位。"
    await data.status_add(msg.user, msg.platform, "血字2", f"{Msg.content_join(msg.content)}|{msg.user}")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_开始_3")
async def activity_blood_start3(msg: Msg):
    """血字参与者"""
    info = await data.status_check(msg.user, msg.platform, "血字2")
    name, dm = info.split("|", 1)

    # 提取 @ 用户
    players = [seg["data"]["qq"] for seg in msg.content if seg["type"] == "at"]

    # 去重
    seen = set()
    unique_players = []
    for p in players:
        if p not in seen:
            seen.add(p)
            unique_players.append(p)

    if not unique_players:
        content = "一场血字至少需要一位住户，请重新确认名单。"
    else:
        start_time = datetime.now()

        # 创建血字记录
        blood_id = await database_update(
            "INSERT INTO user_blood (name, dm, start_time) VALUES (%s, %s, %s)",
            (name, msg.user, start_time)
        )

        # 插入参与者
        for u in unique_players:
            await database_update(
                "INSERT INTO user_blood_player (blood_id, user, alive) VALUES (%s, %s, 1)",
                (blood_id, u)
            )

        # 输出玩家名称
        player_names = []
        for u in unique_players:
            n = await data.user_name(u, msg.platform)
            player_names.append(n or u)
        dm = await data.user_name(dm, msg.platform)
        content = (
            f"血字⌈{name}⌋现已开幕\n"
            f"主持人：{dm}\n"
            f"与会侦探：{', '.join(player_names)}"
        )

        await data.status_delete(msg.user, msg.platform, "血字2")

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_死亡")
async def activity_blood_die(msg: Msg):
    """标记玩家死亡"""
    if msg.group not in config["public"]["公测群"] and msg.group not in config["public"]["内测群"]:
        identity_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" not in identity_list:
            content = "阁下，调整血字状态的权限仅限于内阁成员。"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
                user=msg.user,
                group=msg.group,
            )
            return content

    players = []
    for seg in msg.content:
        if seg["type"] == "at":
            players.append(seg["data"]["qq"])
    if not players:
        content = "请@需要被记录为死亡的住户。"
    else:
        blood = await database_query(
            "SELECT id, start_time FROM user_blood WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
        )
        if not blood:
            content = "目前未有进行中的血字。"
        else:
            blood_id = blood[0]["id"]
            start_time = blood[0]["start_time"]
            content = []
            for u in players:
                result = await data.blood_state(blood_id, u, start_time)
                content.append(result)
            content = "\n".join(content)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_死亡_戳戳")
async def activity_blood_die_poke(msg: Msg):
    """戳戳标记玩家死亡"""
    text = Msg.content_join(msg.content)

    match = re.search(r"(\d+)\D+(\d+)", text)
    if not match:
        return

    actor = match.group(1)
    target = match.group(2)

    # 找最新血字
    blood = await database_query(
        "SELECT id, dm, start_time FROM user_blood WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
    )
    if not blood:
        return

    blood_id = blood[0]["id"]
    dm = str(blood[0]["dm"])
    start_time = blood[0]["start_time"]

    # 只有主持人才能触发死亡判定
    if msg.user != dm:
        return

    content = await data.blood_state(blood_id, target, start_time)

    # 发送消息
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

    return content

@monitor_adapter("/活动_血字_结束")
async def activity_blood_end(msg: Msg):
    """血字结束"""
    blood = await database_query(
        "SELECT id, start_time FROM user_blood WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
    )
    if not blood:
        content = "目前未有进行中的血字。"
    else:
        blood_id = blood[0]["id"]
        start_time = blood[0]["start_time"]
        now = datetime.now()
        duration = int((now - start_time).total_seconds())
        # 更新血字结束时间
        await database_update(
            "UPDATE user_blood SET end_time=%s, duration=%s WHERE id=%s",
            (now, duration, blood_id)
        )

        # 更新所有仍存活的玩家的存活时长
        await database_update(
            "UPDATE user_blood_player SET survival_duration=%s, alive=1 WHERE blood_id=%s AND survival_duration IS NULL",
            (duration, blood_id)
        )

        content = f"本次血字已落幕，历时 {duration // 60} 分钟。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_MVP")
async def activity_blood_mvp(msg: Msg):
    """设置血字 MVP"""
    if msg.group not in config["public"]["公测群"] and msg.group not in config["public"]["内测群"]:
        identity_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" not in identity_list:
            content = "阁下，提名杰出表现者的权限仅限于内阁成员。"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
                user=msg.user,
                group=msg.group,
            )
            return content
    players = [seg["data"]["qq"] for seg in msg.content if seg["type"] == "at"]
    if not players:
        content = "请@一位住户，以提名其为本次血字的杰出表现者。"
    else:
        mvp_user = players[0]

        # 获取最近一场血字（进行中或刚结束）
        blood = await database_query(
            "SELECT id, name FROM user_blood ORDER BY id DESC LIMIT 1"
        )
        if not blood:
            content = "目前未有可设置的血字。"
        else:
            blood_id = blood[0]["id"]
            blood_name = blood[0]["name"]

            player_check = await database_query(
                "SELECT id FROM user_blood_player WHERE blood_id=%s AND user=%s",
                (blood_id, mvp_user),
            )

            if not player_check:
                nick = await data.user_name(mvp_user, msg.platform)
                content = f"阁下，{nick} 并未参与血字『{blood_name}』，无法设为 MVP。"
            else:
                # 更新数据库
                await database_update(
                    "UPDATE user_blood SET mvp=%s WHERE id=%s",
                    (mvp_user, blood_id)
                )
                nick = await data.user_name(mvp_user, msg.platform)
                content = f"血字⌈{blood_name}⌋的杰出住户已记录为：{nick}"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )

    return content


@monitor_adapter("/活动_血字_查询_1")
async def activity_blood_search1(msg: Msg):
    """血字查询选择类型"""
    if msg.kind.startswith("群聊") and msg.group not in config["public"]["公测群"] and msg.group not in \
            config["public"]["内测群"]:
        identity_list = await data.user_identify(msg.user, msg.platform)
        if "内阁" not in identity_list:
            content = "阁下，查询血字记录请通过私聊进行。"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
                user=msg.user,
                group=msg.group,
            )
            return content
    parts = re.split(r"[，,]", Msg.content_join(msg.content))
    if len(parts) == 1:
        content = "请指定查询类型：'个人'或'血字'"
        await data.status_add(msg.user, msg.platform, "血字查询1")
    elif len(parts) == 3:
        output_path = path / f"storage/file/command/blood/user_{msg.seq}.png"
        query_type, target = parts[1].strip(), parts[2].strip()
        if query_type == "个人":
            if target == "所有":
                headers, rows = await data.blood_person_query_all()
            else:
                headers, rows = await data.blood_person_query(target)
        elif query_type == "血字":
            if target == "所有":
                headers, rows = await data.blood_blood_query_all()
            else:
                # 查询单个血字
                headers, rows = await data.blood_blood_query(target)
        else:
            content = "类型无效，请选择'个人'或'血字'。"
            Msg(
                platform=msg.platform,
                event="发送",
                kind=f"{msg.kind[:2]}发送",
                seq=msg.seq,
                content=content,
                user=msg.user,
                group=msg.group,
            )
            return content
        if headers == 0:
            content = rows
        else:
            await data.table_to_image(headers, rows, output_path)
            content = f"[图片:{output_path}]"
            create_background_task(data.remove_later(output_path), name="remove-activity-image")
    else:
        content = "阁下，指令格式有误。请遵循'/血字查询,个人,[玩家QQ号]'或'/血字查询,个人,所有'或'/血字查询,血字,[血字名称]'或'/血字查询,血字,[dmQQ号]'或'/血字查询,血字,所有'的规范。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_查询_2")
async def activity_blood_search2(msg: Msg):
    """血字查询输入目标"""
    query_type = Msg.content_join(msg.content)
    if query_type == "个人":
        content = "请输入您要查询的玩家QQ号或者输入'所有'。"
    else:
        # 查询所有血字名称
        blood_list = await database_query(
            "SELECT name FROM user_blood WHERE duration > 0 ORDER BY id DESC"
        )
        if not blood_list:
            name_list_text = "暂无已结束的血字记录。"
        else:
            # 将血字名与主持人显示出来更直观
            blood_display = await database_query(
                "SELECT name, dm FROM user_blood WHERE duration > 0 ORDER BY id DESC"
            )
            for b in blood_display:
                b['dm'] = await data.user_name(b['dm'], "LR5921")
            name_list_text = "\n".join(
                [f"{b['name']}（DM：{b['dm']}）" for b in blood_display]
            )
        content = "请输入您要查询的血字名称或者输入dm的QQ号或者输入'所有'\n\n可选血字如下：\n" + name_list_text
    await data.status_add(msg.user, msg.platform, "血字查询2", query_type)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_血字_查询_3")
async def activity_blood_search3(msg: Msg):
    """血字查询"""
    query_type = await data.status_check(msg.user, msg.platform, "血字查询2")
    output_path = path / f"storage/file/command/blood/user_{msg.seq}.png"

    if query_type == "个人":
        player = Msg.content_join(msg.content)
        if player == "所有":
            headers, rows = await data.blood_person_query_all()
        else:
            headers, rows = await data.blood_person_query(player)
    else:
        name = Msg.content_join(msg.content).strip()
        if name == "所有":
            headers, rows = await data.blood_blood_query_all()
        else:
            # 查询单个血字
            headers, rows = await data.blood_blood_query(name)
    if headers == 0:
        content = rows
    else:
        await data.table_to_image(headers, rows, output_path)
        content = f"[图片:{output_path}]"
    await data.status_delete(msg.user, msg.platform, "血字查询2")
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    create_background_task(data.remove_later(output_path), name="remove-activity-image")
    return content

async def merge_img():
    """生成合并后的寻宝群总图"""
    group_data = await data.system_get("hunt_group")
    if not group_data:
        return None

    group_list = json.loads(group_data)
    groups = group_list.get("groups", [])
    if not groups:
        return None

    temp_images = []
    for g in groups:
        gid = g["id"]
        info = g["info"]

        text_img_path = path / f"storage/file/command/hunt/tmp_text_{gid}.jpg"
        await data.text_to_image(f"群{gid}: {info}", text_img_path, font_size=30, max_width=400)

        qr_img_path = path / f"storage/file/command/hunt/{gid}.jpg"
        if not qr_img_path.exists():
            continue

        merged_single_path = path / f"storage/file/command/hunt/tmp_merge_{gid}.jpg"
        await data.image_merge([qr_img_path, text_img_path], merged_single_path, direction="vertical")

        temp_images.append(merged_single_path)

    if not temp_images:
        return None

    # 最终合并所有单群图
    final_output = path / "storage/file/command/hunt/merge.jpg"
    await data.image_merge(temp_images, final_output, direction="vertical", padding=30)
    await database_update(
        "DELETE FROM user_media WHERE filepath = %s",
        (final_output,)
    )
    for platform in ["WECHAT", "BILI"]:
        Msg(
            platform=platform,
            event="发送",
            kind="私聊发送",
            content=f"[图片:{final_output}]",
        )

    return final_output


@monitor_adapter("/活动_寻宝_群")
async def activity_hunt_group(msg: Msg):
    """获取寻宝群二维码"""
    group_data = await data.system_get("hunt_group")
    if not group_data:
        content = "当前没有设置寻宝群"
    else:
        if msg.platform == "LR5921":
            group_list = json.loads(group_data)
            nodes = []
            for g in group_list.get("groups", []):
                gid = g["id"]
                info = g["info"]
                text_node = f"[节点:3502644244|LR5921|{gid}:{info}]"
                img_path = path / f"storage/file/command/hunt/{gid}.jpg"
                img_node = f"[节点:3889270613|LR232|[图片:{img_path}]]"

                nodes.append(text_node)
                nodes.append(img_node)

            content = "".join(nodes)
            content = f"[节点:3502644244|LR5921|{content}]"
        else:
            final_output = path / "storage/file/command/hunt/merge.jpg"
            content = f"[图片:{final_output}]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/活动_寻宝_群设置")
async def activity_hunt_group_set(msg: Msg):
    """设置寻宝群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    group_data = await data.system_get(f"hunt_group")
    if group_data:
        group_list = json.loads(group_data)
    else:
        group_list = {"max_id": 0, "groups": []}
    new_id = group_list["max_id"] + 1

    if len(parts) == 2:
        info = parts[1].strip()
    else:
        info = f"寻宝组队群，可自行加入"
    group_list["groups"].append({"id": new_id, "info": info})
    group_list["max_id"] = new_id
    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
    content = f"设置成功，本群为 {new_id} 群，请上传二维码"
    await data.status_add(msg.user, msg.platform, "寻宝添加群", new_id)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/活动_寻宝_群上传")
async def activity_hunt_group_upload(msg: Msg):
    """寻宝群上传"""
    group_id = await data.status_check(msg.user, msg.platform, "寻宝添加群")
    file_path = path / f"storage/file/command/hunt/{group_id}.jpg"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, file_url)
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        msg1 = Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
        await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
    await merge_img()
    await data.status_delete(msg.user, msg.platform, "寻宝添加群")
    content = "添加成功"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group
    )
    return content


@monitor_adapter("/活动_寻宝_群介绍")
async def activity_hunt_group_info(msg: Msg):
    """修改群介绍"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        try:
            group_id = int(parts[1].strip())
        except ValueError:
            content = "群 ID 错误，请输入数字"
        else:
            new_info = parts[2].strip()
            group_data = await data.system_get("hunt_group")
            if not group_data:
                content = "当前没有任何寻宝群"
            else:
                group_list = json.loads(group_data)
                target = None
                for g in group_list.get("groups", []):
                    if g["id"] == group_id:
                        target = g
                        break
                if not target:
                    content = f"未找到 ID 为 {group_id} 的寻宝群"
                else:
                    target["info"] = new_info
                    # 写回数据库
                    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
                    content = f"设置成功，群 {group_id} 的介绍已修改为：{new_info}"
                    await merge_img()
    else:
        content = "格式错误，请使用'/寻宝群介绍,1,这是介绍'类似格式"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_寻宝_群删除")
async def activity_hunt_group_delete(msg: Msg):
    """删除群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 2:
        try:
            group_id = int(parts[1].strip())
        except ValueError:
            content = "群 ID 错误，请输入数字"
        else:
            group_data = await data.system_get("hunt_group")
            if not group_data:
                content = "当前没有任何寻宝群"
            else:
                group_list = json.loads(group_data)
                groups = group_list.get("groups", [])

                new_groups = [g for g in groups if g["id"] != group_id]

                if len(new_groups) == len(groups):
                    content = f"未找到 ID 为 {group_id} 的寻宝群"
                else:
                    group_list["groups"] = new_groups
                    # 写回数据库
                    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
                    content = f"已删除 ID 为 {group_id} 的寻宝群"
                    await merge_img()
    else:
        content = "格式错误，请使用'/寻宝群删除,1'类似格式"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_寻宝_题目")
async def activity_hunt_problem(msg: Msg):
    """获取指定题目"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    user_list = await data.user_identify(msg.user, msg.platform)
    if "内阁" not in user_list:
        return
    if len(parts) != 2:
        content = "格式错误，请使用 '/寻宝题目,数字'"
    else:
        try:
            ans_id = int(parts[1].strip())
        except ValueError:
            content = "答案 ID 错误，请输入数字"
        else:
            answer_file = path / "storage/file/command/hunt/answer.txt"

            if not answer_file.exists():
                content = "答案文件不存在"
            else:
                raw = answer_file.read_text(encoding="utf-8")
                # 按空行分割段落，保留多行内容
                answers = [a.strip() for a in re.split(r"\n\s*\n", raw) if a.strip()]

                if ans_id < 1 or ans_id > len(answers):
                    content = f"未找到 ID 为 {ans_id} 的答案"
                else:
                    answer_text = answers[ans_id - 1]
                    img_path = path / f"storage/file/command/hunt/answer_{ans_id}.png"

                    if img_path.exists():
                        content = f"{answer_text}[图片:{img_path}]"
                    else:
                        content = answer_text

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


