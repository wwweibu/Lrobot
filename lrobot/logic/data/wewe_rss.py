# # TODO
import requests

ORIGIN_URL = "http://0.0.0.0:4000"  # 替换为您的服务器 URL


def request_root():
    """请求根路由 `/`"""
    url = f"{ORIGIN_URL}/"
    response = requests.get(url)
    return response.text


def request_robots_txt():
    """请求 `/robots.txt`"""
    url = f"{ORIGIN_URL}/robots.txt"
    response = requests.get(url)
    return response.text


def request_favicon():
    """请求 `/favicon.ico`"""
    url = f"{ORIGIN_URL}/favicon.ico"
    response = requests.get(url)
    return response.content


def request_dash():
    """请求 `/dash` 路由"""
    url = f"{ORIGIN_URL}/dash"
    response = requests.get(url)
    return response.text


def request_feeds():
    """请求 `/feeds` 路由"""
    url = f"{ORIGIN_URL}/feeds"
    response = requests.get(url)
    return response.text


def request_feeds_all(format="atom", title_include=None, title_exclude=None):
    """
    请求 `/feeds/all.(json|rss|atom)` 路由
    :param format: 返回的格式，支持 "json"、"rss"、"atom"
    :param title_include: 用于过滤标题的包含关键字（支持多个，使用“|”分隔）
    :param title_exclude: 用于过滤标题的排除关键字（支持多个，使用“|”分隔）
    """
    url = f"{ORIGIN_URL}/feeds/all.{format}"
    params = {}
    if title_include:
        params["title_include"] = title_include
    if title_exclude:
        params["title_exclude"] = title_exclude
    response = requests.get(url, params=params)
    return response.text


def request_feed(feed_id, format="json", title_include=None, title_exclude=None):
    """
    请求 `/feeds/:feed` 路由，返回特定 feed 数据
    :param feed_id: feed 的 ID
    :param format: 返回的格式，支持 "json"、"rss"、"atom"
    :param title_include: 用于过滤标题的包含关键字（支持多个，使用“|”分隔）
    :param title_exclude: 用于过滤标题的排除关键字（支持多个，使用“|”分隔）
    """
    url = f"{ORIGIN_URL}/feeds/{feed_id}.{format}"
    params = {}
    if title_include:
        params["title_include"] = title_include
    if title_exclude:
        params["title_exclude"] = title_exclude
    response = requests.get(url, params=params)
    return response.text


def request_feed_update(feed_id):
    """
    请求 `/feeds/:feed` 路由触发单个 feed 更新，带有 `update=true` 参数
    :param feed_id: feed 的 ID
    """
    url = f"{ORIGIN_URL}/feeds/{feed_id}.rss"
    params = {"update": "true"}
    response = requests.get(url, params=params)
    return response.text


def request_feed_no_update(feed_id):
    """
    请求 `/feeds/:feed` 路由触发单个 feed 更新，并且不带有 `update=true` 参数
    :param feed_id: feed 的 ID
    """
    url = f"{ORIGIN_URL}/feeds/{feed_id}.rss"
    response = requests.get(url)
    return response.text


# 示例：调用函数
if __name__ == "__main__":
    # # 请求根路由
    # print(request_root())

    # # 请求 robots.txt
    # print(request_robots_txt())
    #
    # # 请求 favicon.ico
    # print(request_favicon())
    #
    # # 请求 dash 路由
    # print(request_dash())

    # # 请求 feeds 路由 （有用）
    # print(request_feeds())
    #
    # # 请求所有 feeds（Atom 格式，包含“张三”）
    # print(request_feeds_all(format="json", title_include="征文"))
    #
    # 请求特定 feed（MP_WXS_123，JSON 格式，包含“张三”，排除“张三丰”）
    print(
        request_feed(
            feed_id="MP_WXS_3897723490",
            format="json",
            title_include="诈骗",
            title_exclude="迷香",
        )
    )
    #
    # # 请求触发 feed 更新（带 update=true 参数）
    # print(request_feed_update(feed_id="MP_WXS_123"))
    #
    # # 请求触发 feed 更新（不带 update 参数）
    # print(request_feed_no_update(feed_id="MP_WXS_123"))
