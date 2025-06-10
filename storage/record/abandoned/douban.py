# TODO
import requests

api_key = "0ac44ae016490db2204ce0a042db2916"

api_key1 = "0b2bdeda43b5688921839c8ecb20399b"

api_key2 = "0ab215a8b1977939201640fa14c66bab"

api_key3 = "054022eaeae0b00e0fc068c0c0a2102a"


def search_books(q=None, tag=None, start=0, count=20):
    """
    查询豆瓣书籍信息的函数。

    参数:
        api_url (str): API 基础 URL，例如 "https://api.douban.com/v2/book/search"。
        q (str): 查询关键字 (可选, q 和 tag 必须传一个)。
        tag (str): 查询标签 (可选, q 和 tag 必须传一个)。
        start (int): 查询结果的起始位置，默认 0。
        count (int): 查询结果的条数，默认 20，最大 100。

    返回:
        dict: 返回包含查询结果的 JSON 数据。
    """
    api_url = "https://api.douban.com/v2/book/search"
    if not q and not tag:
        raise ValueError("参数 'q' 和 'tag' 至少需要一个！")
    if count > 100:
        raise ValueError("参数 'count' 最大值为 100！")

    # 构造请求参数
    params = {
        "q": q,
        "tag": tag,
        "start": start,
        "count": count,
        "apikey": api_key,
        "User-Agent": "MicroMessenger/",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
    }
    # 发送请求
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # 检查 HTTP 响应是否成功
        return response.json()  # 返回 JSON 数据
    except requests.RequestException as e:
        print(f"请求失败：{e}")
        return None


def get_rank():
    url = "https://frodo.douban.com/api/v2/book/rank_list?apiKey=0ac44ae016490db2204ce0a042db2916"

    # 请求头
    headers = {
        "User-Agent": "MicroMessenger/",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
    }

    # 发送 GET 请求
    response = requests.get(url, headers=headers)

    # 检查响应
    if response.status_code == 200:
        print("请求成功：")
        print(response.json())  # 打印 JSON 数据
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.text)


def get_user():
    url = "https://api.douban.com/v2/user/264446444"
    params = {
        "apikey": api_key,
        "User-Agent": "MicroMessenger/",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
    }
    try:
        # 发起请求
        response = requests.get(url, params=params)
        response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError 异常
    except requests.exceptions.HTTPError as e:
        # 捕获异常，提取错误信息中的 URL
        error_message = str(e)
        print("捕获异常：", error_message)

        # 提取 URL（如果异常中包含 URL）
        if "for url:" in error_message:
            error_url = error_message.split("for url:")[1].strip()
            print("提取到的 URL:", error_url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
                "Accept": "application/json, text/html",
            }
            try:
                response = requests.get(error_url, headers=headers)
                response.raise_for_status()  # 处理 2xx 范围以外的状态码
                print("返回内容：")
                print(response.text)
            except requests.exceptions.HTTPError as e:
                print(f"请求失败，状态码：{response.status_code}")
                print("返回的 HTML 内容：", response.text)

        else:
            print("未找到 URL 信息")


def get_note():
    url = "https://api.douban.com/v2/note/user_created/264446444"
    params = {
        "apikey": api_key3,
        "User-Agent": "MicroMessenger/",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
    }
    try:
        # 发起请求
        response = requests.get(url, params=params)
        response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError 异常
    except requests.exceptions.HTTPError as e:
        # 捕获异常，提取错误信息中的 URL
        error_message = str(e)
        print("捕获异常：", error_message)

        # 提取 URL（如果异常中包含 URL）
        if "for url:" in error_message:
            error_url = error_message.split("for url:")[1].strip()
            print("提取到的 URL:", error_url)


if __name__ == "__main__":
    get_note()
