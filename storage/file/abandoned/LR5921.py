"""LLOneBot 原代码逻辑"""
import re
import os
import json
import asyncio
import traceback
import websockets
from datetime import datetime
from zoneinfo import ZoneInfo
from lrobot.config import config
from lrobot.log import robot_log
from lrobot.database import add_users, activities_edit
from lrobot.event.point import get_speakers, task_queue
from lrobot.msg import Msg, msg_log, msg_add, global_ws, set_global_ws


async def LR5921_start():
    websocket_url = "ws://localhost:5921"  # LLOneBot连接端口
    try:
        async with websockets.connect(websocket_url) as ws:
            set_global_ws(ws)  # 全局共享ws连接
            await on_open()
            await on_message()  # WebSocket 消息接收和处理
    except Exception:
        error_message = traceback.format_exc()
        log_event(
            "LRobot", "系统未知错误", f"WebSocket connection error: {error_message}"
        )


async def on_open():
    log_event("LR5921", "机器启动", "启动成功")
    asyncio.create_task(get_speakers())  # 每日发言逻辑


async def on_message():
    try:
        async for message in global_ws.get("ws"):
            data = json.loads(message)
            if "status" in data and data["status"] == "ok":
                await echo_deal(data)
            elif "post_type" in data:  # 收到 WS 事件
                if data.get("post_type") == "message":  # 消息事件
                    await message_deal(data)
                elif data.get("post_type") == "notice":  # 通知事件
                    log_event("LR5921", "通知事件调试", data)
                    is_group_recall = (
                        data.get("notice_type") == "group_recall"
                        and str(data.get("group_id")) == config["测试群"]
                    )  # 群聊撤回
                    is_friend_recall = (
                        data.get("notice_type") == "friend_recall"
                    )  # 私聊撤回
                    is_poked = data.get("sub_type") == "poke" and str(
                        data.get("target_id")
                    ) in [
                        config["LR5921"],
                        config["LR232"],
                    ]  # 戳戳
                    is_liked = (
                        data.get("notice_type") == "group_msg_emoji_like"
                    )  # 群消息被表态
                    if is_group_recall or is_friend_recall:
                        await revoke(data)
                    elif is_poked:
                        await get_poke(data)
                    elif is_liked:
                        await get_like(data)
            #  不处理请求事件和元事件
            else:
                # WS返回failed
                log_event("LR5921", "WS回应调试", data)
    except Exception:
        error_message = traceback.format_exc()
        log_event(
            "LRobot", "系统未知错误", f"WebSocket massage_deal error: {error_message}"
        )


async def echo_deal(data):
    # 处理 WS 回应的消息，echo为附属信息字段，收发一致
    log_event("LR5921", "WS回应调试", data)
    echo = data.get("echo", "")
    data = data.get("data")
    if echo.startswith("msg_send"):
        await echo_msg_send(echo, data)
    elif echo.startswith("msg_get"):
        await echo_msg_get(echo, data)
    elif echo.startswith("get_like"):
        await echo_get_like(echo, data)
    elif echo.startswith("revoke"):
        await echo_revoke(data)
    elif echo.startswith("flush_speak"):
        await echo_flush_speak(data)
    elif echo.startswith("get_speak"):
        await echo_get_speak(data)
    elif echo.startswith("get_talkative"):
        await echo_get_talkative(data)
    elif echo.startswith("get_users"):
        await echo_get_users(data)
    elif echo.startswith("get_file"):
        await echo_get_file(echo, data)
    elif echo.startswith("add_activities"):
        await echo_add_activities(echo, data)
    elif echo.startswith("add_activity_group"):
        await echo_add_activity_group(echo, data)
    else:
        log_event("LRobot", "系统未知错误", f"未知的WS回应{echo}|{data}")


async def message_deal(data):
    # 消息处理
    msg_content = data.get("message")  # 原始消息段格式（数组）
    log_event("LR5921", "消息接收调试", msg_content)
    content, info, name, url, at = await segment_join(msg_content)
    if not content and not name:  # 不处理空格消息
        return

    if data.get("message_type") == "private":  # 私聊消息
        if info:
            kind = 13  # 好友回复
        else:
            if content:
                if name:
                    kind = 11
                else:
                    kind = 10
            else:
                kind = 12
    else:  # 群聊消息
        if info:
            if at == 1:
                kind = 33  # 配对消息
            elif at == 2:
                kind = 23  # 群聊回复
            else:
                content = "[回复消息]" + content
                kind = 34
        else:
            if at == 1:
                kind = 33  # 配对消息
            elif at == 2:
                if content:
                    if name:
                        kind = 11
                    else:
                        kind = 10
                else:
                    kind = 12
            else:
                kind = 34

    # # 内阁管家特殊处理，不用@快捷使用指令
    # keywords = ["记：", "等：", "催：", "示：", "删："]
    # if kind == 12 and str(data.get('group_id')) == config["内阁"] and any(keyword in content for keyword in keywords):
    #     kind = 2

    msg = Msg(
        robot="LR5921",
        content=content,
        kind=kind,
        info=info,
        file_name=name,
        file_url=url,
        group=None if data.get("message_type") == "private" else data.get("group_id"),
        qq=data.get("user_id"),
        seq=data.get("message_id"),
    )
    await msg_add(msg)


async def segment_join(content):
    content_parts = []
    # 支持识别表情混合文字、图片混合文字、语音、视频、文件、掷骰子、猜拳、合并转发
    # 目前推荐好友、群聊、位置分享、链接分享、音乐分享都是json格式，视频是文件格式
    info_updated = False  # 只识别第一个文件
    info = ""
    name = ""
    url = ""
    at = 0
    for item in content:
        msg_type = item.get("type")
        msg_data = item.get("data", {})
        if msg_type == "text":
            content_parts.append(msg_data.get("text", ""))
        elif msg_type == "face":
            face_id = msg_data.get("id")
            face_id = config["emojis"].get(int(face_id), "未知表情")
            content_parts.append(f"[{face_id}]")
        elif msg_type == "mface":
            face_id = msg_data.get("summary")
            content_parts.append(face_id)
        elif msg_type == "rps":
            rps_id = msg_data.get("result")
            rps_mapping = {"1": "布", "2": "剪刀", "3": "石头"}
            rps_result = rps_mapping.get(
                rps_id, "未知结果"
            )  # 默认值为'未知结果'，如果rps_id不在映射中
            content_parts.append(f"[猜拳:{rps_result}]")
        elif msg_type == "dice":
            dice_id = msg_data.get("result")
            content_parts.append(f"[掷骰子{dice_id}点]")
        elif msg_type == "forward":
            content_parts.append(f"[合并转发消息]")
        elif msg_type == "node":
            content_parts.append(f"[合并转发节点]")
        elif msg_type == "image" and not info_updated:
            name = msg_data.get("file")
            url = msg_data.get("url")
        elif msg_type == "record" and not info_updated:
            name = msg_data.get("file")
            url = msg_data.get("url")
        elif msg_type == "file" and not info_updated:
            name = msg_data.get("file")
            # 此处是未下载的msg_id
            url = msg_data.get("file_id")
        elif msg_type == "reply":
            # 回复的消息
            info = msg_data.get("id")
        elif msg_type == "at":
            qq = msg_data.get("qq")
            if qq == config["LR232"]:
                at = 1
            elif qq == config["LR5921"] and at != 1:
                at = 2
            else:
                user = msg_data.get("name")
                content_parts.append(f"[@{user}]")
        else:
            log_event("LRobot", "系统未知错误", f"收到无法解析的消息：{item}")
    content_join = "".join(content_parts)
    return content_join, info, name, url, at


async def array_join(content):
    # 获取发送的消息、撤回的消息、回应的消息（get_file的数组格式)
    # 使用re.split将内容按[CQ:...]格式切分
    items = re.split(r"(\[CQ:.*?\])", content)
    content_parts = []

    for item in items:
        if not item:  # 跳过空字符串
            continue
        if item.startswith("[CQ:"):
            if "CQ:text" in item:
                match = re.search(r"text=([^]]+)]", content)
                content_parts.append(match.group(1))
            elif "CQ:face" in item:
                match = re.search(r"id=([^]]+)]", content)
                face_id = config["emojis"].get(int(match.group(1)), "未知表情")
                content_parts.append(f"[{face_id}]")
            elif "CQ:mface" in item:
                match = re.search(r"summary=([^,]+),", content)
                content_parts.append(match.group(1))
            elif "CQ:rps" in item:
                match = re.search(r"result=([^]]+)]", content)
                rps_mapping = {"1": "布", "2": "剪刀", "3": "石头"}
                rps_result = rps_mapping.get(match.group(1), "未知结果")
                content_parts.append(f"[猜拳:{rps_result}]")
            elif "CQ:mface" in item:
                match = re.search(r"result=([^]]+)]", content)
                content_parts.append(f"[掷骰子{match.group(1)}点]")
            elif "CQ:forward" in item:
                content_parts.append(f"[合并转发消息]")
            elif "CQ:node" in item:
                content_parts.append(f"[合并转发节点]")
            elif "CQ:image" in item:
                match = re.search(r"file=([^,]+),", content)
                content_parts.append(f"[图片{match.group(1)}]")
            elif "CQ:record" in item:
                match = re.search(r"file=([^,]+),", content)
                content_parts.append(f"[音频{match.group(1)}]")
            elif "CQ:file" in item:
                match = re.search(r"file=([^,]+),", content)
                content_parts.append(f"[文件{match.group(1)}]")
            elif "CQ:reply" in item:
                content_parts.append(f"[回复消息]")
            elif "CQ:at" in item:
                match = re.search(r"qq=([^]]+)]", content)
                content_parts.append(f"[@{match.group(1)}]")
            else:
                log_event("LRobot", "系统未知错误", f"收到无法解析的消息：{item}")
        else:
            content_parts.append(item)

    content_join = "".join(content_parts)
    return content_join


async def revoke(data):
    #  获取撤回消息
    info = {
        "action": "get_msg",
        "params": {
            "message_id": data.get("message_id"),
        },
        "echo": "revoke",
    }
    await global_ws.get("ws").send(json.dumps(info))


async def get_poke(data):
    # 被戳了
    msg = Msg(
        robot="LR5921" if str(data.get("target_id")) == config["LR5921"] else "LR232",
        content="戳戳",
        kind=24 if data.get("group_id") else 14,
        group=data.get("group_id"),
        qq=data.get("user_id"),
    )
    await msg_add(msg)


async def get_like(data):
    # 被点赞了
    user_id = data.get("user_id")
    like_id = data.get("likes")[0].get("emoji_id")
    info = {
        "action": "get_msg",
        "params": {
            "message_id": data.get("message_id"),
        },
        "echo": "get_like" + "|" + str(like_id) + "|" + str(user_id),
    }
    await global_ws.get("ws").send(json.dumps(info))


async def echo_msg_send(echo, data):
    # 发送消息的回应
    parts = echo.split("|")
    if len(parts) == 2:
        user_id = parts[1]
        info = {
            "action": "get_msg",
            "params": {
                "message_id": data.get("message_id"),
            },
            "echo": f"msg_get|{user_id}",
        }
        await global_ws.get("ws").send(json.dumps(info))


async def echo_msg_get(echo, data):
    # 获取发送的消息并记录
    parts = echo.split("|")
    if len(parts) == 2:
        user_id = parts[1]
        content = await array_join(data.get("raw_message"))
        msg = Msg(
            robot="LR5921",
            content=content,
            kind=31 if data.get("message_type") == "private" else 32,
            group=data.get("group_id"),
            qq=user_id,
        )
        await msg_log(msg)


async def echo_get_like(echo, data):
    # 获取回应的原消息
    parts = echo.split("|")
    if len(parts) == 3:  # 确保分割后的数组有 3 部分
        like_id = parts[1]  # 提取 like_id
        user_id = parts[2]  # 提取 user_id
        content = await array_join(data.get("raw_message"))
        msg = Msg(
            robot="LR5921",
            content=content,
            kind=35,
            info=config["emojis"].get(int(like_id), "未知表情"),
            group=data.get("group_id"),
            qq=user_id,
        )
        await msg_add(msg)


async def echo_revoke(data):
    # 获取撤回的原消息
    content = await array_join(data.get("raw_message"))
    msg = Msg(
        robot="LR5921",
        content=content,
        kind=19 if data.get("message_type") == "private" else 29,
        group=data.get("group_id"),
        qq=data.get("user_id"),
    )
    await msg_add(msg)


async def echo_flush_speak(data):
    # 刷新群成员最后发言时间
    asia_tz = ZoneInfo("Asia/Shanghai")
    today_start = datetime.now(asia_tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_start = int(today_start.timestamp())

    for user in data:
        last_sent_time = user["last_sent_time"]
        if last_sent_time < today_start:  # 只刷新未显示今日发言的
            info = {
                "action": "get_group_member_info_rate_limited",
                "params": {
                    "group_id": config["水群"],
                    "user_id": user["user_id"],
                    "no_cache": True,  # 强制刷新缓存
                },
            }
            await task_queue.put(info)


async def echo_get_speak(data):
    #  获取今日发言的人
    asia_tz = ZoneInfo("Asia/Shanghai")
    today_start = datetime.now(asia_tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )  # 获取今天的开始时间戳（从零点开始）
    today_start = int(today_start.timestamp())

    today_speakers = []
    for user in data:
        last_sent_time = user["last_sent_time"]
        if last_sent_time >= today_start:
            today_speakers.append(
                {"nickname": user["nickname"], "user_id": user["user_id"]}
            )

    content = "今日水群发言:" + ",".join(
        speaker["nickname"] for speaker in today_speakers
    )

    # 发送至内阁
    info = {
        "action": "send_msg",
        "params": {"group_id": config["内阁"], "message": content},
        "echo": "msg_send",
    }
    await global_ws.get("ws").send(json.dumps(info))


async def echo_get_talkative(data):
    user_id = data["current_talkative"]["user_id"]
    nickname = data["current_talkative"]["nickname"]

    # 发送至内阁
    content = "今日水群龙王:" + nickname

    info = {
        "action": "send_msg",
        "params": {"group_id": config["内阁"], "message": content},
        "echo": "msg_send",
    }
    await global_ws.get("ws").send(json.dumps(info))


async def echo_get_users(data):
    # 获取群成员
    if data[0]["group_id"] == 920712228:
        # 水群和平台群
        i = 1
    else:
        # 社员群
        i = 2
    user_list = [(user["user_id"], user["nickname"]) for user in data]
    await add_users(user_list, i)


async def echo_get_file(echo, data):
    parts = echo.split("|")
    if len(parts) == 2:
        qq = parts[1]
        url = data.get("file")
        content = os.path.basename(url)
        msg = Msg(
            robot="LR5921",
            content=content,
            kind=5,
            file_url=url,
            qq=qq,
            seq=data.get("message_id"),
        )
        await msg_add(msg)


async def echo_add_activities(echo, data):
    # 添加活动的消息序号
    parts = echo.split("|")
    if len(parts) == 2:
        task_id = parts[1]
        msg_id = data.get("message_id")
        await activities_edit(task_id, "msg_id", msg_id)


async def echo_add_activity_group(echo, data):
    print(1)
    # 添加活动的二维码图片序号
    parts = echo.split("|")
    if len(parts) == 2:
        task_id = parts[1]
        pic_id = data.get("message_id")
        print(pic_id)
        await activities_edit(task_id, "pic_id", pic_id)
