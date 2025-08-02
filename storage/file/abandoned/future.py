# 关于 future 的一项测试，上半部分是不能成功唤醒等待协程的代码，下半部分是可以唤醒的代码，使用需安装 flask
# import asyncio
# from flask import Flask
#
#
# class FutureManager:
#     def __init__(self):
#         self.futures = {}  # 用于存储 Future 对象的字典
#
#     def get(self, key):
#         # 获取已有的 Future 对象，若不存在则创建一个新的
#         if key not in self.futures:
#             self.futures[key] = asyncio.Future()
#         return self.futures[key]
#
#     def set(self, key, result):
#         # 设置 Future 对象的结果
#         _future = self.get(key)
#         if not _future.done():
#             _future.set_result(result)
#
#
# future = FutureManager()
#
#
# def a():
#     app = Flask(__name__)
#     future.set("a", "b")
#     app.run("0.0.0.0", 5922, debug=False)
#
#
# async def b():
#     f = future.get("a")
#     await f
#     print(11111111)
#
#
# async def c():
#     f = future.get("a")
#     while True:
#         await asyncio.sleep(10)
#         print(f"Future status before await: {f.done()}")
#
#
# async def d():
#     tasks = [
#         asyncio.to_thread(a()),
#         b(),
#         # c(),
#     ]
#     await asyncio.gather(*tasks)
#
#
# if __name__ == "__main__":
#     asyncio.run(d())


import asyncio
from flask import Flask


class FutureManager:
    def __init__(self):
        self.futures = {}
        self.loop = None

    def bind_loop(self, loop):
        self.loop = loop

    def get(self, key):
        if key not in self.futures:
            # 使用主循环创建Future
            self.futures[key] = self.loop.create_future()
        return self.futures[key]

    def set1(self, key, result):
        _future = self.get(key)
        if not _future.done():
            self.loop.call_soon_threadsafe(_future.set_result, result)
            self.loop.call_soon_threadsafe(lambda: None)


future = FutureManager()


def a():
    app = Flask(__name__)
    future.set1("a", "b")  # 现在可以安全执行
    app.run("0.0.0.0", 5922, debug=False)


async def b():
    f = future.get("a")
    await f
    print("11111111 成功输出！")


async def d():
    loop = asyncio.get_running_loop()
    future.bind_loop(loop)
    tasks = [
        asyncio.to_thread(a),
        b(),
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(d())
