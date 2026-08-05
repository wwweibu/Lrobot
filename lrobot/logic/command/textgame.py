"""文字博弈相关"""

import re

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter, config

QUESTION_PATTERN = re.compile(r"^\s*第\s*(\d+)\s*题")
VOTE_PATTERN = re.compile(r"^\s*(改)?\s*(\d+)\s*([A-Za-z])\s*$")


def _send(msg: Msg, content):
    """回复消息"""
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


def _group_send(game, content):
    """向开局所在群发送消息"""
    Msg(
        platform=game["platform"],
        event="发送",
        kind="群聊发送",
        content=content,
        group=game["group_id"],
    )
    return content


async def _dm_game(msg: Msg):
    """取当前这局,要求 msg 来自本局主持人且在开局的那个群,返回 (局, 错误提示)"""
    game = await data.textgame_get()
    if not game:
        return None, "阁下,当前没有正在进行的文字博弈。"
    if str(msg.group) != str(game["group_id"]):
        return None, "阁下,本场文字博弈不在此群进行。"
    if str(msg.user) != str(game["dm"]):
        dm_name = await data.user_name(game["dm"], game["platform"])
        return None, f"阁下,本场文字博弈由 {dm_name} 主持,该指令仅限主持人使用。"
    return game, None


@monitor_adapter("/文字博弈_帮助")
async def textgame_help(msg: Msg):
    """文字博弈帮助"""
    content = (
        "文字博弈(主持人指令,均在开局的群里发):\n"
        "/开始文字博弈  开局并开放报名\n"
        "第N题xxxxx     发题即开始收集第 N 题的答案\n"
        "/截止          截止当前题并公布分布\n"
        "/报名截止      提前关闭报名(默认发第2题时自动关)\n"
        "/游戏结束      封盘并公布总分排名\n"
        "/文字博弈名单  查看当前报名名单(仅主持人)\n"
        "/文字博弈进度  查看当前题还差谁没交(仅主持人)\n"
        "\n"
        "发题须知:选项请各占一行、以 A、B、C… 开头,我会据此自动识别本题选项集,\n"
        "并据此校验玩家提交的字母。题面里请勿出现多余的大写字母,以免干扰识别。\n"
        "\n"
        "玩家(私聊我):\n"
        "报名           加入本场文字博弈\n"
        "2F             提交第 2 题的答案 F\n"
        "改2A           修改答案,每题只能改一次\n"
        "我的答案       查看自己本题已提交的答案"
    )
    return _send(msg, content)


@monitor_adapter("/文字博弈_开始")
async def textgame_start(msg: Msg):
    """开局"""
    game = await data.textgame_get()
    if game:
        dm_name = await data.user_name(game["dm"], game["platform"])
        content = (
            f"阁下,已有一场文字博弈在进行中(主持人 {dm_name},当前第 {game['round']} 题)。"
            "同一时间只能开一场,请先'/游戏结束'。"
        )
        return _send(msg, content)
    await data.textgame_create(msg.user, msg.platform, msg.group)
    content = (
        "文字博弈开局,报名开放。\n"
        "各位请私聊我发'报名'加入。\n"
        "主持人发'第1题xxxxx'即开始第一题;报名将在发出第 2 题时自动关闭。"
    )
    return _send(msg, content)


@monitor_adapter("/文字博弈_报名")
async def textgame_signup(msg: Msg):
    """玩家报名"""
    game = await data.textgame_get()
    if not game:
        return _send(msg, "阁下,当前没有正在进行的文字博弈。")
    if not game["signup_open"]:
        return _send(msg, "阁下,本场文字博弈的报名已经关闭了。")
    name = await data.user_name(msg.user, msg.platform)
    added, total = await data.textgame_player_add(game["id"], msg.user, name)
    if not added:
        return _send(msg, f"阁下已在名单之中,当前共 {total} 人。")
    return _send(msg, f"报名成功,阁下是第 {total} 位。答题时请私聊我发'题号+选项',如'1A'。")


@monitor_adapter("/文字博弈_报名截止")
async def textgame_signup_close(msg: Msg):
    """主持人提前关闭报名"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    await data.textgame_edit(game["id"], signup_open=0)
    players = await data.textgame_players(game["id"])
    return _send(msg, f"报名已关闭,本场共 {len(players)} 人参与。")


async def textgame_question_judge(msg: Msg):
    """判断是否为本局主持人在发题"""
    if not QUESTION_PATTERN.match(Msg.content_join(msg.content)):
        return False
    game, _ = await _dm_game(msg)
    return bool(game)


@monitor_adapter("/文字博弈_发题")
async def textgame_question(msg: Msg):
    """主持人发题,开始收集本题答案"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    round = int(QUESTION_PATTERN.match(Msg.content_join(msg.content)).group(1))
    current = game["round"] or 0

    if round == current:
        exist = await data.textgame_round_get(game["id"], round)
        votes = await data.textgame_votes(game["id"], round)
        if exist and exist["status"] == "收集中":
            return _send(msg, f"第 {round} 题已在收集中,已收 {len(votes)} 份答案,未做改动。")
        return _send(msg, f"第 {round} 题已经截止过了(分布 {exist['dist'] if exist else '无'}),如需重开请先联系开发。")
    if round != current + 1:
        return _send(msg, f"阁下,当前进行到第 {current} 题,下一题应当是第 {current + 1} 题。")

    previous = await data.textgame_round_get(game["id"], current) if current else None
    if previous and previous["status"] == "收集中":
        return _send(msg, f"阁下,第 {current} 题尚未截止,请先发'/截止'公布分布。")

    text = Msg.content_join(msg.content)
    options = data.textgame_options_parse(text)
    title = text.strip().splitlines()[0][:500]
    await data.textgame_round_open(game["id"], round, options, title)
    players = await data.textgame_players(game["id"])
    if options:
        scope = f"本题选项 {'/'.join(options)}"
    else:
        scope = "未能从题面识别出选项(题面里的选项请以 A、B、C… 开头另起一行),本题将不校验选项字母"
    content = (
        f"第 {round} 题开始收集,共 {len(players)} 人参与,{scope}。\n"
        f"请私聊我提交答案,格式'{round}X'(X 为选项字母),每题可修改一次'改{round}X'。"
    )
    if round >= 2 and game["signup_open"]:
        await data.textgame_edit(game["id"], signup_open=0)
        content += "\n报名已自动关闭。"
    return _send(msg, content)


async def textgame_vote_judge(msg: Msg):
    """判断是否为玩家在私聊提交答案"""
    if not VOTE_PATTERN.match(Msg.content_join(msg.content)):
        return False
    game = await data.textgame_get()
    if not game or not game["round"]:
        return False
    if not await data.textgame_player_get(game["id"], msg.user):
        return False
    return True


@monitor_adapter("/文字博弈_答题")
async def textgame_vote(msg: Msg):
    """玩家提交答案"""
    game = await data.textgame_get()
    if not game:
        return
    match = VOTE_PATTERN.match(Msg.content_join(msg.content))
    round, choice = int(match.group(2)), match.group(3).upper()

    if round != game["round"]:
        return _send(msg, f"阁下,当前是第 {game['round']} 题,你提交的是第 {round} 题。")
    current = await data.textgame_round_get(game["id"], round)
    if not current or current["status"] != "收集中":
        return _send(msg, f"阁下,第 {round} 题已经截止,不再接受答案。")
    options = current["options"] or ""
    if options and choice not in options:
        return _send(msg, f"阁下,第 {round} 题只有 {'/'.join(options)} 这几个选项。")

    result, final = await data.textgame_vote_set(game["id"], round, msg.user, choice)
    if result == "收到":
        return _send(msg, "收到")
    if result == "已改":
        return _send(msg, f"收到,已改为 {final}。本题的修改机会已用完。")
    return _send(msg, f"阁下本题已用过一次修改机会,答案仍为 {final}。")


@monitor_adapter("/文字博弈_我的答案")
async def textgame_mine(msg: Msg):
    """玩家查询自己本题的答案"""
    game = await data.textgame_get()
    if not game:
        return _send(msg, "阁下,当前没有正在进行的文字博弈。")
    if not await data.textgame_player_get(game["id"], msg.user):
        return _send(msg, "阁下不在本场名单之中。")
    if not game["round"]:
        return _send(msg, "本场尚未开始第一题。")
    vote = await data.textgame_vote_get(game["id"], game["round"], msg.user)
    if not vote or not vote["choice"]:
        return _send(msg, f"阁下第 {game['round']} 题尚未提交答案。")
    changed = "已用过修改机会" if vote["changed"] else "还可以修改一次"
    return _send(msg, f"阁下第 {game['round']} 题的答案是 {vote['choice']},{changed}。")


@monitor_adapter("/文字博弈_截止")
async def textgame_round_end(msg: Msg):
    """主持人截止当前题并公布分布"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    if not game["round"]:
        return _send(msg, "阁下,本场尚未开始第一题。")
    current = await data.textgame_round_get(game["id"], game["round"])
    if not current or current["status"] != "收集中":
        return _send(msg, f"阁下,第 {game['round']} 题已经截止过了,分布为 {current['dist'] if current else '无'}。")

    dist, counter, absent = await data.textgame_round_close(game["id"], game["round"])
    content = f"第 {game['round']} 题分布:{dist or '无人提交'}"
    if absent:
        names = "、".join(p["name"] or p["user"] for p in absent)
        content += f"\n未交票 {len(absent)} 人:{names}"
    return _send(msg, content)


@monitor_adapter("/文字博弈_名单")
async def textgame_roster(msg: Msg):
    """查看报名名单,仅主持人"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    players = await data.textgame_players(game["id"])
    if not players:
        return _send(msg, "尚无人报名。")
    names = "、".join(p["name"] or p["user"] for p in players)
    return _send(msg, f"本场共 {len(players)} 人:\n{names}")


@monitor_adapter("/文字博弈_进度")
async def textgame_progress(msg: Msg):
    """查看当前题的提交进度,仅主持人"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    if not game["round"]:
        return _send(msg, "本场尚未开始第一题。")
    players = await data.textgame_players(game["id"])
    _, _, absent = await data.textgame_dist(game["id"], game["round"])
    content = f"第 {game['round']} 题已交 {len(players) - len(absent)}/{len(players)}。"
    if absent:
        names = "、".join(p["name"] or p["user"] for p in absent)
        content += f"\n还差:{names}"
    return _send(msg, content)


@monitor_adapter("/文字博弈_结束")
async def textgame_over(msg: Msg):
    """主持人结束本场并公布排名"""
    game, err = await _dm_game(msg)
    if err:
        return _send(msg, err)
    await data.textgame_finish(game["id"])
    rank = await data.textgame_rank(game["id"])
    if not rank:
        return _send(msg, "本场文字博弈已结束,无人参与。")
    lines = [f"{r['rank']}. {r['name'] or r['user']}  {r['total']:g}" for r in rank]
    return _send(msg, "本场文字博弈已结束,总分排名:\n" + "\n".join(lines))
