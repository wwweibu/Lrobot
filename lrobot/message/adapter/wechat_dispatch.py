"""微信公众号调用 API"""

import mimetypes
from datetime import datetime, timedelta

from .acess_token import access_tokens
from config import (
    config,
    future,
    loggers,
    connect,
    path,
    database_query,
    database_update,
)

base_url = "https://api.weixin.qq.com/cgi-bin"
adapter_logger = loggers["adapter"]
save_dir = path / "storage/file/user/wechat"
save_dir.mkdir(parents=True, exist_ok=True)


async def request_deal(url, data, tag, file=None):
    """请求统一处理"""
    data.update({"access_token": access_tokens["WECHAT"]["token"]})
    client = connect(True)
    try:
        response = await client.post(url, params=data, files=file, timeout=20)
    except Exception as e:
        raise Exception(f"{tag} 请求异常 ->  e: {e} | data: {data}")

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
                f"{tag} 请求失败 -> errcode: {json_resp['errcode']} | errmsg: {errmsg} | data: {data} | {file if file else ''}"
            )

    adapter_logger.info(
        f"[WECHAT] {tag} 成功 -> {data}",
        extra={"event": "消息发送"},
    )
    return response


async def wechat_file_upload(filepath, type=None, url=None):
    """文件上传"""
    query = "SELECT media_id, uploaded_at FROM user_media WHERE filepath = %s"
    result = await database_query(query, (filepath,))
    if result:
        uploaded_at = result[0]["uploaded_at"]
        expire_time = uploaded_at + timedelta(days=3)
        if datetime.now() < expire_time:
            return result[0]["media_id"]

    url = f"{base_url}/media/upload"
    params = {"type": type}
    mime_type, _ = mimetypes.guess_type(filepath)
    files = {
        "media": (
            filepath,
            open(filepath, "rb"),
            mime_type,
        )
    }
    response = await request_deal(url, params, "文件上传", files)
    media_id = (
        response.json().get("thumb_media_id")
        if type == "thumb"
        else response.json().get("media_id")
    )
    if media_id:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
               INSERT INTO user_media (filepath, media_id, uploaded_at)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE media_id = VALUES(media_id), uploaded_at = VALUES(uploaded_at)
           """
        await database_update(query, (filepath, media_id, now_str))
    return media_id


async def wechat_file_download(media_id):
    """文件下载"""
    # TODO 改为用户路径
    url = f"{base_url}/media/get"
    params = {"media_id": media_id}
    response = await request_deal(url, params, "文件下载")
    content_type = response.headers.get("content-type", "")
    if content_type == "audio/amr":
        with open(f"{save_dir}/{media_id}.amr", "wb") as f:
            f.write(response.content)
    elif content_type == "video/mpeg4":
        with open(f"{save_dir}/{media_id}.mp4", "wb") as f:
            f.write(response.content)


async def wechat_dispatch(
        content, kind=None, user=None, group=None, num=None, order=None, seq=None
):
    """消息发送"""
    msg_type = content[0].get("type")
    data = content[0].get("data", {})
    base = f"""<xml>
    <ToUserName><![CDATA[{user}]]></ToUserName>
    <FromUserName><![CDATA[{config['WECHAT_SELF']}]]></FromUserName>
    <CreateTime>{seq[:-2]}</CreateTime>"""

    if msg_type == "text":
        content = data.get("text", "").replace("\n", "\u2028")  # 替换换行符
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Content><![CDATA[{content}]]></Content>\n"""

    elif msg_type == "image":
        file = data.get("file", "")
        media_id = await wechat_file_upload(msg_type, file)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Image><MediaId><![CDATA[{media_id}]]></MediaId></Image>\n"""

    elif msg_type == "record":
        msg_type = "voice"
        file = data.get("file", "")
        media_id = await wechat_file_upload(msg_type, file)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Voice><MediaId><![CDATA[{media_id}]]></MediaId></Voice>\n"""

    elif msg_type == "video":
        file = data.get("file", "")
        title = data.get("title", "")
        desc = data.get("description", "")
        media_id = await wechat_file_upload(msg_type, file)
        base += f"""<MsgType><![CDATA[{msg_type}]]></MsgType>
        <Video><MediaId><![CDATA[{media_id}]]></MediaId>
        <Title><![CDATA[{title}]]></Title>
        <Description><![CDATA[{desc}]]></Description>
        </Video>\n"""

    elif msg_type == "json":
        data = data.get("data")
        # TODO,1:将这个改为本地文件挂载；2：测试如果文件被移动（url无效）微信消息能否正常读取/播放
        if data.get("prompt") == "微信-音乐":
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
        elif data.get("prompt") == "微信-图文":
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
    base = f"""<xml>
      <ToUserName><![CDATA[orHObs--jF-OZjwOu0NLmd6MIox8]]></ToUserName>
      <FromUserName><![CDATA[gh_a0180524f340]]></FromUserName>
      <CreateTime>1753166758</CreateTime>
      <MsgType><![CDATA[text]]></MsgType>
      <Content><![CDATA[你
      好]]></Content>
    </xml>"""
    future.set(seq, base)
