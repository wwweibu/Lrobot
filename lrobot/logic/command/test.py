"""测试相关"""

import asyncio
from config import path, future, config
from message.handler.msg import Msg



async def test_1(msg: Msg):
    """测试函数"""
    record = path / f"storage/file/command/morning_20251025.wav"
    msg = Msg(
        platform=msg.platform,
        kind=f"群聊发送",
        event="发送",
        content=f"欢迎找小推[at:1326016706]或小推·人机版(me)入会。可以不用加好友直接私聊我，发送'/入会'，注意去掉引号，保留'/'哦~\n对协会活动有疑问也可以找我发送'/常见问题'。\n注：仅支持固定指令",
        seq=msg.seq,
        group=config["public"]["水群"][0]
    )

    # response = await future.wait(msg.num, "测试超时!")
    #
    # response = await future.wait(msg.num, "测试超时!")
    # print(response)

# 小型音频识别
# async def sparkle_record_deal(bv, today):
#     """获取花火视频并处理"""
#     today_wav = path / f"storage/file/command/sparkle_{today}.wav"
#     if today_wav.exists():
#         return str(today_wav)
#     # 清理旧文件
#     for file in (path / "storage/file/command").glob("sparkle_*.wav"):
#         if file != today_wav:
#             try:
#                 file.unlink()
#             except Exception as e:
#                 msg_logger.error(
#                     f"⌈文件处理⌋: 音频转换 -> 删除旧文件失败: {file} - {e}",
#                     extra={"event": "消息处理"},
#                 )
#     # 下载视频
#     msg = Msg(
#         platform="BILI",
#         kind="私聊视频下载",
#         event="发送",
#         content=bv,
#     )
#     try:
#         _future = future.get(msg.num)
#         dash = await asyncio.wait_for(_future, timeout=20)
#     except asyncio.TimeoutError:
#         raise Exception("私聊视频下载链接获取超时")
#
#     url = dash.get("audio", [])[0].get("baseUrl") if dash.get("audio", []) else None
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
#         "Referer": "https://www.bilibili.com"
#     }
#     today_m4s = path / f"storage/file/command/sparkle_{today}.m4s"
#     client = connect()
#     async with client.stream("GET", url, headers=headers) as r:
#         if r.status_code != 200:
#             raise Exception(f"下载失败:{r.status_code}")
#         with open(today_m4s, "wb") as f:
#             async for chunk in r.aiter_bytes():
#                 f.write(chunk)
#     # 截取视频头部
#     head_wav = str(today_m4s).replace(".m4s", "_head.wav")
#     try:
#         (
#             ffmpeg
#             .input(str(today_m4s), t=10)  # 截取前 10 秒
#             .output(
#                 head_wav,
#                 format="wav",  # 指定容器为 wav
#                 acodec="pcm_s16le",  # 16-bit PCM
#                 ac=1,  # 单声道
#                 ar="16000",  # 16kHz 采样率
#             )
#             .overwrite_output()
#             .run(quiet=True, capture_stdout=True, capture_stderr=True)
#         )
#     except ffmpeg.Error as e:
#         err_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
#         msg_logger.error(f"⌈文件处理⌋: 音频转换 -> ffmpeg 失败 : {err_msg}", extra={"event": "消息处理"})
#         raise
#
#     # 语音识别
#     try:
#         model = Model(str(path / "storage/file/command/vosk-model-small-cn-0.22"))
#         wf = wave.open(head_wav, "rb")
#         rec = KaldiRecognizer(model, wf.getframerate())
#         rec.SetWords(True)
#
#         results = []
#         while True:
#             data = wf.readframes(4000)
#             if len(data) == 0:
#                 break
#             if rec.AcceptWaveform(data):
#                 results.append(json.loads(rec.Result()))
#         results.append(json.loads(rec.FinalResult()))
#
#         target_end = None
#         prev_word = None
#         for res in results:
#             if "result" not in res:
#                 continue
#             msg_logger.info(f"⌈文件处理⌋: 语音识别 -> 识别分段 : {res}", extra={"event": "消息处理"})
#             for w in res["result"]:
#                 word = w["word"]
#                 # 如果上一个是 "过"，当前是 "呀/啊/牙"
#                 if prev_word == "过" and any(ch in word for ch in ["呀", "啊", "牙"]):
#                     target_end = w["end"]
#                     break
#                 prev_word = word
#             if target_end:
#                 break
#
#         if target_end is None:
#             raise RuntimeError("未找到 '过呀' 相关位置")
#
#         msg_logger.info(
#             f"⌈文件处理⌋: 识别完成 -> '过呀' 结束时间 {target_end:.2f}s",
#             extra={"event": '消息处理'}
#         )
#     except Exception as e:
#         msg_logger.error(
#             f"⌈文件处理⌋: 语音识别失败 {e}",
#             extra={"event": "消息处理"}
#         )
#         raise
#     # 裁剪
#     try:
#         (
#             ffmpeg
#             .input(head_wav)
#             .output(
#                 str(today_wav),
#                 t=target_end + 0.2,  # 保留“过呀”稍后一点
#                 acodec="pcm_s16le",
#                 ac=1,
#                 ar=16000
#             )
#             .overwrite_output()
#             .run(quiet=True)
#         )
#     except ffmpeg.Error as e:
#         err_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
#         msg_logger.error(
#             f"⌈文件处理⌋: mp3 裁剪失败 : {err_msg}",
#             extra={"event": "消息处理"}
#         )
#         raise
#
#     # 清理临时文件
#     for tmp_file in [today_m4s, head_wav]:
#         try:
#             if os.path.exists(tmp_file):
#                 os.remove(tmp_file)
#         except Exception as e:
#             msg_logger.error(
#                 f"⌈文件处理⌋: 临时文件删除失败 {tmp_file} - {e}",
#                 extra={"event": "消息处理"},
#             )
#     return str(today_wav)
