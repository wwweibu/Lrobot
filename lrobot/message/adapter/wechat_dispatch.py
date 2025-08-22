"""WECHAT API 调用"""

import os
import mimetypes
from datetime import datetime, timedelta

from .acess_token import access_tokens
from logic import image_compress, video_compress, record_compress, file_name_overwrite
from config import (
    config,
    future,
    loggers,
    connect,
    database_query,
    database_update,
)

base_url = "https://api.weixin.qq.com/cgi-bin/"
adapter_logger = loggers["adapter"]


async def request_deal(url, data, tag, files=None):
    """请求统一处理"""
    data["access_token"] = access_tokens["WECHAT"]["token"]
    client = connect(True)
    try:
        response = await client.post(f"{base_url}{url}", params=data, files=files, timeout=60 if files else 15)
    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  {type(e).__name__}: {e} | data: {data}")

    if response.status_code != 200:
        raise Exception(
            f"{tag} 请求失败 -> [{response.status_code}]{response.text} | data: {data}"
        )

    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type or response.text.strip().startswith("{"):
        json_resp = response.json()
        if "errcode" in json_resp:
            errmsg = json_resp.get("errmsg", "未知错误")
            raise Exception(
                f"{tag} 请求失败 -> errcode: {json_resp['errcode']} | errmsg: {errmsg} | data: {data}"
            )

    adapter_logger.info(
        f"[WECHAT] {tag} 成功 -> {data} | {response}",
        extra={"event": "消息发送"},
    )
    return response


async def wechat_dispatch(
        content, kind=None, user=None, group=None, num=None, seq=None, order=None
):
    """消息发送"""
    msg_type = content[0].get("type")
    data = content[0].get("data", {})
    base = f"""<xml>
    <ToUserName><![CDATA[{user}]]></ToUserName>
    <FromUserName><![CDATA[{config['WECHAT_SELF']}]]></FromUserName>
    <CreateTime>{seq[:-2] if kind.endswith("添加发送") else seq}</CreateTime>"""

    if msg_type == "text":
        content = data.get("text", "").replace("\n", "。")  # 替换换行符  "\u2028"
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Content><![CDATA[{content}]]></Content>\n"""

    elif msg_type == "image":
        file = data.get("file", "")
        media_id = await wechat_file_upload(file, type=msg_type)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Image><MediaId><![CDATA[{media_id}]]></MediaId></Image>\n"""

    elif msg_type == "record":
        msg_type = "voice"
        file = data.get("file", "")
        media_id = await wechat_file_upload(file, type=msg_type)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Voice><MediaId><![CDATA[{media_id}]]></MediaId></Voice>\n"""

    elif msg_type == "video":
        file = data.get("file", "")
        title = data.get("title", "")
        desc = data.get("description", "")
        media_id = await wechat_file_upload(file, type=msg_type)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Video><MediaId><![CDATA[{media_id}]]></MediaId>
        <Title><![CDATA[{title}]]></Title>
        <Description><![CDATA[{desc}]]></Description>
        </Video>\n"""

    elif msg_type == "json":
        data = data.get("data")
        prompt = data.get("prompt")
        # TODO,1:将这个改为本地文件挂载；2：测试如果文件被移动（url无效）微信消息能否正常读取/播放
        if prompt == "微信-音乐":
            msg_type = "music"
            title = data.get("title")
            description = data.get("description")
            url = data.get("url")
            base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
            <Music><Title><![CDATA[{title}]]></Title>
            <Description><![CDATA[{description}]]></Description>
            <MusicUrl><![CDATA[{url}]]></MusicUrl>
            <HQMusicUrl><![CDATA[{url}]]></HQMusicUrl>
            </Music>\n"""
        elif prompt == "微信-图文":
            msg_type = "news"
            title = data.get("title")
            description = data.get("description")
            picurl = data.get("picurl")
            url = data.get("url")
            base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
                    <ArticleCount>1</ArticleCount>
                    <Articles><item>
                    <Title><![CDATA[{title}]]></Title>
                    <Description><![CDATA[{description}]]></Description>
                    <PicUrl><![CDATA[{picurl}]]></PicUrl>
                    <Url><![CDATA[{url}]]></Url>
                    </item></Articles>\n"""
    base += "</xml>"
    future.set(seq, base)


async def wechat_file_upload(file, type=None, url=None):
    """文件上传"""
    query = "SELECT media_id, wechat FROM user_media WHERE filepath = %s"
    result = await database_query(query, (file,))
    if result:
        media_id, t = result[0]["uploaded_at"], result[0]["wechat"]
        if media_id and t and datetime.now() < t + timedelta(days=3):
            return media_id

    url = "media/upload"
    params = {"type": type}
    file_stream = ""
    if type == "image":
        file_stream = await image_compress(file)
    elif type == "voice":
        file_stream = await record_compress(file, duration_limit_sec=60)
    elif type == "video":
        file_stream = await video_compress(file)
    elif type == "thumb":
        file_stream = await image_compress(file, target_size_mb=64 / 1024)
    mime_type, _ = mimetypes.guess_type(file)
    files = {
        "media": (
            file,
            file_stream,
            mime_type,
        )
    }
    response = await request_deal(url, params, "文件上传", files)
    media_id = (
        response.json().get("thumb_media_id")
        if type == "thumb"
        else response.json().get("media_id")
    )
    if not media_id:
        raise Exception("wechat upload failed")
    query = """
                INSERT INTO user_media (filepath, media_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE 
                    media_id = VALUES(media_id),
                    wechat = CURRENT_TIMESTAMP
            """
    await database_update(query, (file, media_id))
    return media_id


async def wechat_file_download(file, path):
    """文件下载"""
    url = "media/get"
    params = {"media_id": file}
    response = await request_deal(url, params, "文件下载")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    path = file_name_overwrite(path)
    with open(path, "wb") as f:
        f.write(response.content)
    loggers["message"].info(
        f"⌈文件处理⌋: 文件下载 -> 下载成功 {path}",
        extra={"event": "消息处理"},
    )
