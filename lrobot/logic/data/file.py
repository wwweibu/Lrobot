"""文件相关"""

import av
import os
import pilk
import base64
import ffmpeg
import asyncio
import tempfile
from PIL import Image
from io import BytesIO

from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=2)

from config import connect


async def file_download(path, url):
    """文件下载"""
    client = connect()
    response = await client.get(url)
    response.raise_for_status()  # 如果失败抛出异常
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(response.content)


def to_pcm(path):
    """任意媒体文件转 pcm"""
    out_path = os.path.splitext(path)[0] + ".pcm"
    with av.open(path) as in_container:
        in_stream = in_container.streams.audio[0]
        sample_rate = in_stream.codec_context.sample_rate
        with av.open(out_path, "w", "s16le") as out_container:
            out_stream = out_container.add_stream(
                "pcm_s16le", rate=sample_rate, layout="mono"
            )
            try:
                for frame in in_container.decode(in_stream):
                    frame.pts = None
                    for packet in out_stream.encode(frame):
                        out_container.mux(packet)
            except:
                pass
    return out_path, sample_rate


def record_convert(media_path):
    """任意媒体文件转 silk, 返回silk路径"""
    base_path = os.path.splitext(media_path)[0]
    silk_path = base_path + ".silk"

    if os.path.exists(silk_path):
        return silk_path

    pcm_path, sample_rate = to_pcm(media_path)
    pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
    os.remove(pcm_path)
    return silk_path


def image_compress(image_path, max_size_kb=10240, max_width=None):
    """图片压缩至 10MB"""
    img = Image.open(image_path).convert("RGB")
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))

    quality = 85
    buffer = BytesIO()
    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = buffer.tell() // 1024
        if size_kb <= max_size_kb or quality <= 30:
            break
        quality -= 5
    buffer.seek(0)
    return buffer


def record_compress(
        input_path,
        target_size_mb=2,
        duration_limit_sec=None,
        max_retry=5,
        min_bitrate=32000,  # 最低32kbps，防止压到失真
):
    """压缩音视频到指定大小，返回 BytesIO 文件流（必须小于 target_size_mb，否则返回 None）"""
    probe = ffmpeg.probe(input_path)
    duration = float(probe['format']['duration'])
    if duration_limit_sec:
        duration = min(duration, duration_limit_sec)

    bitrate = (target_size_mb * 8 * 1024 * 1024) / duration  # bits/sec

    for i in range(max_retry):
        output = BytesIO()
        stream = ffmpeg.input(input_path)
        kwargs = {
            "format": "mp3",
            "audio_bitrate": str(int(bitrate)),  # ffmpeg 要字符串类型
        }
        if duration_limit_sec:
            kwargs["t"] = duration_limit_sec

        stream = stream.output('pipe:', **kwargs)
        try:
            out, err = stream.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print("FFmpeg stderr:", e.stderr.decode())
            raise
        output.write(out)
        output.seek(0)

        size_mb = len(output.getbuffer()) / (1024 * 1024)
        if size_mb <= target_size_mb:
            print(f"[compress] 成功压缩至 {size_mb:.2f}MB")
            return output
        else:
            print(f"[compress] 第 {i + 1} 次尝试大小为 {size_mb:.2f}MB，继续压缩...")
            bitrate = max(int(bitrate * 0.8), min_bitrate)

    print("[compress] 无法压缩至目标大小")
    return None


async def video_compress(input_path, target_size_mb=10, return_type=None):
    """异步压缩视频文件到指定大小"""

    def _compress_sync():
        try:
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
        except Exception as e:
            print("[compress] probe 失败:", e)
            return None

        bitrate = (target_size_mb * 8 * 1024 * 1024) / duration  # bit/s
        max_retry = 5

        for i in range(max_retry):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmpfile:
                temp_path = tmpfile.name

            kwargs = {
                "b:v": str(int(bitrate))  # 视频压缩用 b:v
            }

            try:
                (
                    ffmpeg
                    .input(input_path)
                    .output(temp_path, format="mp4", **kwargs)
                    .overwrite_output()
                    .run(quiet=True)
                )
                size_mb = os.path.getsize(temp_path) / (1024 * 1024)
                if size_mb <= target_size_mb:
                    print(f"[compress] 成功压缩到 {size_mb:.2f}MB")
                    if return_type:
                        with open(temp_path, "rb") as f:
                            encoded = base64.b64encode(f.read()).decode("utf-8")
                        os.remove(temp_path)
                        return encoded
                    return open(temp_path, "rb")
                else:
                    print(f"[compress] 第 {i + 1} 次尝试大小 {size_mb:.2f}MB 超限")
                    bitrate *= 0.8  # 降低码率重试

            except ffmpeg.Error as e:
                print("[compress] FFmpeg 错误:", e.stderr.decode())
                break

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        print("[compress] 无法压缩至目标大小")
        return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, _compress_sync)
