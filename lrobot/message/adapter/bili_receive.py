import json
import time
from message.handler.msg import Msg
from config import config,loggers,connect,monitor_adapter

adapter_logger = loggers["adapter"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Origin": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
}


async def bili_msg_get(interval=None):
    """获取会话列表"""
    client = connect()
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions"
    cookies = {
        "SESSDATA": config["BILI_SESSDATA"]
    }
    params = {
        **({"begin_ts": int((time.time()-interval) * 1_000_000)} if interval is not None else {}),
    }  # 增加开始时间
    response = await client.get(url, headers=headers, params=params,cookies=cookies)
    if response.status_code == 200:
        adapter_logger.debug(f"⌈BILI⌋{response.json()}", extra={"event": "消息接收"})
        msg_list = response.json()["data"]["session_list"]
        if not isinstance(msg_list, list):  # 无消息
            return
        for msg in msg_list:
            if msg['unread_count'] == 0:
                pass
            elif msg['unread_count'] == 1:
                await bili_msg_read(msg['talker_id'])
                await bili_msg_deal(msg['last_msg'])
            else:
                await bili_msg_read(msg['talker_id'])
                msg_get_list = await bili_msg_list_get(msg['talker_id'],msg['ack_seqno'])
                for msg_get in msg_get_list:
                    await bili_msg_deal(msg_get)
    else:
        adapter_logger.error(
            f"[BILI]网络异常 -> {response.text}", extra={"event": "消息接收"}
        )


async def bili_msg_list_get(talker_id,begin_seqno):
    """获取指定对话"""
    client = connect()
    url = "https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs"
    cookies = {
        "SESSDATA": config["BILI_SESSDATA"]
    }
    params = {
        "talker_id": talker_id,
        "session_type": 1,
        "size": 20,
        "begin_seqno": begin_seqno  # 设置开始序号
    }
    response = await client.get(url, headers=headers, params=params, cookies=cookies)
    if response.status_code == 200:
        msg_list = response.json()["data"]["messages"]
        return msg_list


async def bili_msg_read(talker_id):
    """设置会话已读"""
    client = connect()
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack"
    cookies = {
        "SESSDATA": config["BILI_SESSDATA"]
    }
    data = {
        "talker_id": talker_id,
        "session_type": 1,
        "csrf_token": config["BILI_JCT"],
        "csrf": config["BILI_JCT"]
    }
    response = await client.post(url, headers=headers, data=data, cookies=cookies)
    if response.status_code == 200:
        return
    else:
        adapter_logger.error(
            f"[BILI]网络异常 -> {response.text}", extra={"event": "消息接收"}
        )

@monitor_adapter("BILI")
async def bili_msg_deal(msg):
    """消息处理，对应私信主体对象"""
    print(msg)
    content = json.loads(msg["content"])
    files = []
    kind = "私聊文字消息"
    if msg['msg_type'] == 1:
        content = content["content"]
    elif msg['msg_type'] == 2 or msg['msg_type'] == 6:
        kind = "私聊文件消息"
        file_name = f"{msg['msg_key']}.{content['imageType']}"
        file_url = content["url"]
        files.append((file_name,file_url))
        content = "[文件]"
    elif msg['msg_type'] == 5:
        kind = "私聊撤回消息"
        content = f"{msg['sender_uid']}撤回了一条消息{content}"
    elif msg['msg_type'] == 7:
        source_type_map = {
            2: "相簿",
            3: "纯文字",
            5: "视频",
            6: "专栏",
            7: "番剧",
            8: "音乐",
            9: "国产动画",
            10: "图片",
            11: "动态",
            16: "番剧",
            17: "番剧"
        }
        type = source_type_map.get(content["source"], "未知类型")
        id = content['bvid'] if type == "视频" else content['id']
        content = f"来自{content['author']}的{type}{id}：{content['title']}"
    elif msg['msg_type'] == 10:
        kind = "私聊系统消息"
        content = f"{content['title']}{content['text']}"
    elif msg['msg_type'] == 13:
        content = content['title']
    elif msg['msg_type'] == 14:
        content = f"来自{content['author']}的{content['source']}：{content['desc']} {content['title']}"
    else:
        adapter_logger.error(
            f"[BILI]未定义的消息类型 -> {msg}", extra={"event": "消息接收"}
        )
        return
    Msg(
        robot="BILI",
        kind=kind,
        event="处理",
        source=msg['sender_uid'],
        seq=msg['msg_seqno'],
        content=content,
        files=files
    )
