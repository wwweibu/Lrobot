"""工具"""

import re
import time
import jionlp as jio
from datetime import datetime

from logic import data
from message.handler.msg import Msg
from config import database_update, monitor_adapter, path, future, temp_key


@monitor_adapter("/工具_待办")
async def tool_pending(msg: Msg):
    """设置待办"""
    user = await data.status_lr5921_get(msg.user, msg.platform)
    if not user:
        content = "阁下，此功能专为 LR5921 平台或已绑定该平台的平台所设。请您确认当前使用的身份凭证。"
    else:
        parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
        content = "指令格式似乎有误。正确的范例应为'/待办，明天晚六点，用餐'，烦请您依此格式重新下达指令。"
        if len(parts) == 3:
            try:
                pending_time = jio.parse_time(parts[1].strip(), time_base=time.time(), time_type="time_point")
                if pending_time["type"] == "time_point" or pending_time["type"] == "time_span":
                    pending_time = pending_time["time"][0]
                    target_time = datetime.strptime(pending_time, "%Y-%m-%d %H:%M:%S")
                    content = f"已为您在 {pending_time} 设置提醒：{parts[2].strip()}。届时我会准时提醒您，阁下。"
                    Msg(
                        platform=msg.platform,
                        event="发送",
                        kind=f"{msg.kind[:2]}发送",
                        seq=msg.seq,
                        content=content,
                        user=msg.user,
                        group=msg.group,
                    )
                    sql = "INSERT INTO system_remind (time, content, user) VALUES (%s, %s, %s)"
                    id = await database_update(sql, (target_time, parts[2].strip(), user))
                    await data.remind_send(id, target_time, parts[2].strip(), user)
                    return
                else:
                    content = "时间格式需要调整，阁下。请勿使用'7.1'表示日期，请勿使用'h'、'm'、's'分别表示时、分、秒。"
            except Exception:
                content = "时间格式需要调整，阁下。请勿使用'7.1'表示日期，请勿使用'h'、'm'、's'分别表示时、分、秒。"
        elif len(parts) == 1:
            content = "阁下，请告知我需要提醒的具体事项。"
            await data.status_add(msg.user, msg.platform, "待办1")
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


@monitor_adapter("/工具_待办_事项")
async def tool_pending_1(msg: Msg):
    """待办输入事项"""
    content = Msg.content_join(msg.content).strip()
    await data.status_delete(msg.user, msg.platform, "待办1")
    await data.status_add(msg.user, msg.platform, "待办2", content)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content="请以中文方式提供提醒时间，若系统无法识别，则无返回消息，说明时间格式需要调整。",
        user=msg.user,
        group=msg.group,
    )
    return content


async def tool_pending_2_judge(msg: Msg):
    """待办时间判断"""
    content = Msg.content_join(msg.content)
    try:
        pending_time = jio.parse_time(content, time_base=time.time(), time_type="time_point")
        if pending_time["type"] == "time_point" or pending_time["type"] == "time_span":
            return True
        else:
            return False
    except Exception:
        return False


@monitor_adapter("/工具_待办_时间")
async def tool_pending_2(msg: Msg):
    """待办时间设置"""
    pending_time = jio.parse_time(Msg.content_join(msg.content), time_base=time.time(), time_type="time_point")
    item = await data.status_check(msg.user, msg.platform, "待办2")
    pending_time = pending_time["time"][0]
    target_time = datetime.strptime(pending_time, "%Y-%m-%d %H:%M:%S")
    content = f"已为您在 {pending_time} 设置提醒：{item}。届时我会准时提醒您，阁下。"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    sql = "INSERT INTO system_remind (time, content, user) VALUES (%s, %s, %s)"
    user = await data.status_lr5921_get(msg.user, msg.platform)
    id = await database_update(sql, (target_time, item, user))
    await data.remind_send(id, target_time, item, user)
    await data.status_delete(msg.user, msg.platform, "待办2")
    return content


@monitor_adapter("/工具_网址")
async def tool_web(msg: Msg):
    """获取网址"""
    content = ("临时网址(有效期10分钟):\n"
               f"主页: whumystery.cn/{temp_key['uuid']}\n"
               f"wiki页: whumystery.cn/{temp_key['uuid']}/wiki\n"
               f"功能页: whumystery.cn/{temp_key['uuid']}/firefly\n"
               f"网盘页: whumystery.cn/{temp_key['uuid']}/file\n"
               f"时间轴页: whumystery.cn/{temp_key['uuid']}/timeline\n"
               "长期使用:\n"
               "1.添加LR5921\n"
               "2.访问 whumystery.cn/cmd,输入代号\n"
               "3.输入对应验证码，等待跳转\n"
               "4.下次可直接访问 whumystery.cn/cab\n"
               "QQ上只能用临时网址,微信上可以登录"
               )
    if msg.platform == "WECHAT":
        content = content.replace("\n", "    ")
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


@monitor_adapter("/工具_直播开启")
async def tool_live_start(msg: Msg):
    """B 站开启直播"""
    content = "请输入直播标题"
    await data.status_add(msg.user, msg.platform, "直播1")
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


@monitor_adapter("/工具_直播标题")
async def tool_live_title(msg: Msg):
    """B 站设置直播标题"""
    title = Msg.content_join(msg.content)
    msg1 = Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播开启",
    )
    addr, code = await future.wait(msg1.num, "[消息]直播推流获取超时")
    await data.status_delete(msg.user, msg.platform, "直播1")
    await data.status_add(msg.user, msg.platform, "直播2", title)
    content = f"推流地址:{addr}\n推流码:{code}\n如需更改直播间封面则直接发送图片,沿用上次封面则回复'否'"
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


@monitor_adapter("/工具_直播封面")
async def tool_live_cover(msg: Msg):
    """B 站设置直播"""
    title = await data.status_check(msg.user, msg.platform, "直播2")
    if msg.content[0].get("type") == "text":
        content = title
    else:
        file_path = path / f"storage/file/user/{msg.user}/{msg.content[0]['data']['file']}"
        file_url = msg.content[0]['data'].get('url')
        if file_url:
            await data.file_download(file_path, msg.content[0]['data']['url'])
        else:
            msg.content[0]['data']['file_path'] = str(file_path)
            msg1 = Msg(
                platform="LR5921",
                event="发送",
                kind="文件下载",
                content=msg.content
            )
            await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
        content = f"{title}|{file_path}"
    msg1 = Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播标题",
        content=content
    )

    await future.wait(msg1.num, "[消息]直播标题设置超时")

    await data.status_delete(msg.user, msg.platform, "直播2")
    content = "设置成功"
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


@monitor_adapter("/工具_直播关闭")
async def tool_live_close(msg: Msg):
    """B 站关闭直播"""
    Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播关闭",
    )
    content = "关闭成功"
    await data.status_delete(msg.user, msg.platform, "直播")
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


@monitor_adapter("/工具_直播公告")
async def tool_live_notice(msg: Msg):
    """B 站设置直播公告"""
    await data.status_add(msg.user, msg.platform, "直播3")
    content = "请发送公告"
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


@monitor_adapter("/工具_直播公告_回答")
async def tool_live_notice_answer(msg: Msg):
    """B 站设置直播公告回答"""
    notice = Msg.content_join(msg.content).strip()
    Msg(
        platform="BILI",
        event="发送",
        kind=f"私聊直播公告",
        content=notice
    )
    content = f"设置成功，公告为{notice}"
    await data.status_delete(msg.user, msg.platform, "直播3")
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


@monitor_adapter("/工具_wiki")
async def tool_wiki(msg: Msg):
    """wiki 上传图片"""
    await data.status_add(msg.user, msg.platform, "wiki")
    content = "请上传图片"
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


@monitor_adapter("/工具_wiki_链接")
async def tool_wiki_answer(msg: Msg):
    """wiki 生成链接"""
    wiki_dir = path / "storage/file/resource/wiki"
    existing_numbers = []
    for file in wiki_dir.glob("*.png"):
        if file.stem.isdigit():  # 检查文件名是否为纯数字
            existing_numbers.append(int(file.stem))
    next_number = max(existing_numbers, default=0) + 1
    file_path = wiki_dir / f"{next_number}.png"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, msg.content[0]['data']['url'])
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        msg1 = Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
        await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
    content = f"https://whumystery.cn/hjd/static/wiki/{next_number}.png"
    await data.status_delete(msg.user, msg.platform, "wiki")
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
