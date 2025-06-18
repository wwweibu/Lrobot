# 微信公众号发送
import json
import httpx
from .acess_token import access_tokens
from config import config, future, loggers


adapter_logger = loggers["adapter"]


async def wechat_dispatch(id, seq, content):
    """微信发送消息"""
    content = content.replace("\n", "\u2028")  # 替换换行符
    response = f"""<xml>
    <ToUserName><![CDATA[{id}]]></ToUserName>
    <FromUserName><![CDATA[{config['WECHAT_SELF']}]]></FromUserName>
    <CreateTime>{seq}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    </xml>"""
    future.set(seq, response)


async def up_image():
    """TODO 传入图片"""
    # 本地文件路径
    file_path = "test.jpg"

    # 准备文件数据（media 是字段名）
    files = {"media": open(file_path, "rb")}  # 打开文件并作为二进制上传

    # 请求参数
    params = {"access_token": access_tokens["LR232"]["token"], "type": "image"}

    # 发起 POST 请求
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.weixin.qq.com/cgi-bin/media/upload", params=params, files=files
        )
        if response.status_code == 200:
            adapter_logger.debug(
                f"[WECHAT][成功]{response.text}", extra={"event": "消息发送"}
            )
        else:
            raise Exception(f"图片上传失败 -> [{response.status_code}]{response.text}")


async def up_new():
    """TODO 上传公众号文章"""
    Articles = {
        "articles": [
            {
                "article_type": "news",
                "title": "新年祝福",
                "digest": "新年快乐吖！",
                "content": "蛇年到，小推祝大家：灵蛇献瑞，智慧生辉；妙解难题，喜气盈门！",
                "thumb_media_id": media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 1,
            },
        ]
    }
    # 请求参数
    params = {"access_token": access_tokens["LR232"]["token"]}
    json_data = json.dumps(Articles, ensure_ascii=False)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.weixin.qq.com/cgi-bin/draft/add", params=params, data=json_data
        )
        if response.status_code == 200:
            adapter_logger.debug(
                f"[WECHAT][成功]{response.text}", extra={"event": "消息发送"}
            )
        else:
            raise Exception(f"文章上传失败 -> [{response.status_code}]{response.text}")


async def get_image():
    """TODO 获取公众号图片"""
    params = {"access_token": access_tokens["LR232"]["token"]}
    data = {"type": "image", "offset": 0, "count": 20}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.weixin.qq.com/cgi-bin/material/batchget_material",
            params=params,
            json=data,
        )
        if response.status_code == 200:
            adapter_logger.debug(
                f"[WECHAT][成功]{response.text}", extra={"event": "消息发送"}
            )
        else:
            raise Exception(f"图片获取失败 -> [{response.status_code}]{response.text}")


async def update_acticle():
    """TODO TONOTDO 发布文章"""
    data = {"media_id": article}
    params = {"access_token": access_tokens["LR232"]["token"]}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.weixin.qq.com/cgi-bin/freepublish/submit",
            params=params,
            json=data,
        )
        if response.status_code == 200:
            adapter_logger.debug(
                f"[WECHAT][成功]{response.text}", extra={"event": "消息发送"}
            )
        else:
            raise Exception(f"文章发布失败 -> [{response.status_code}]{response.text}")


async def group_send():
    """TODO TONOTDO 群发"""
    data = {
        "filter": {
            "is_to_all": True,
        },
        "text": {
            "content": "蛇年到，小推祝大家：灵蛇献瑞，智慧生辉；妙解难题，喜气盈门！"
        },
        "msgtype": "text",
    }
    json_data = json.dumps(data, ensure_ascii=False)
    params = {"access_token": access_tokens["LR232"]["token"]}
    # 使用 POST 方法发送请求
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.weixin.qq.com/cgi-bin/message/mass/sendall",
            params=params,
            json=data,
        )
        if response.status_code == 200:
            adapter_logger.debug(
                f"[WECHAT][成功]{response.text}", extra={"event": "消息发送"}
            )
        else:
            raise Exception(f"消息群发失败 -> [{response.status_code}]{response.text}")
