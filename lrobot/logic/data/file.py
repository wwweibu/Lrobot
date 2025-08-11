"""文件相关"""

import av
import os
import pilk
import base64
import ffmpeg
import shutil
import asyncio
import tempfile
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor

from config import connect, loggers

process_pool = ProcessPoolExecutor()
msg_logger = loggers["message"]


def file_name_overwrite(path):
    """如果文件存在，则自动生成 file (1).ext"""
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter += 1
    return new_path

async def file_download(path, url):
    """文件下载"""
    client = connect()
    response = await client.get(url)
    response.raise_for_status()  # 如果失败抛出异常
    os.makedirs(os.path.dirname(path), exist_ok=True)
    path = file_name_overwrite(path)
    with open(path, "wb") as f:
        f.write(response.content)
    msg_logger.info(
        f"⌈文件处理⌋: 文件下载 -> 下载成功 {path}",
        extra={"event": "消息处理"},
    )


def _record_convert(media_path, silk_path):
    # 生成临时 PCM 文件
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pcm") as tmp_pcm:
            pcm_path = tmp_pcm.name
        with av.open(media_path) as in_container:
            in_stream = in_container.streams.audio[0]
            sample_rate = in_stream.codec_context.sample_rate
            # 写 PCM
            with av.open(pcm_path, "w", "s16le") as out_container:
                out_stream = out_container.add_stream(
                    "pcm_s16le", rate=sample_rate, layout="mono"
                )
                for frame in in_container.decode(in_stream):
                    frame.pts = None
                    for packet in out_stream.encode(frame):
                        out_container.mux(packet)
        msg_logger.info(
            f"⌈文件处理⌋: silk 转换 -> 转换 PCM 成功 {pcm_path}",
            extra={"event": "消息处理"},
        )
        # PCM → silk
        pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
        msg_logger.info(
            f"⌈文件处理⌋: silk 转换 -> 转换 Silk 成功 {silk_path}",
            extra={"event": "消息处理"},
        )
        os.remove(pcm_path)
        return silk_path
    except Exception as e:
        msg_logger.error(
            f"⌈文件处理⌋: silk 转换 -> {e}",
            extra={"event": "消息处理"},
        )
        return None


async def record_convert(media_path):
    """任意媒体文件转 silk"""
    silk_path = os.path.splitext(media_path)[0] + ".silk"

    if os.path.exists(silk_path):
        msg_logger.info(
            f"⌈文件处理⌋: silk 转换 -> 已存在 silk 文件 {silk_path}",
            extra={"event": "消息处理"},
        )
        return silk_path

    # 在后台线程执行
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _record_convert, media_path, silk_path)


def _read(path, return_type):
    """分别对应 open(file_path, "rb") 和 with open(file_path, "rb") as f: file_data = base64.b64encode(f.read()).decode("utf-8")"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8") if return_type else BytesIO(f.read())


def _get_compress_path(path):
    base, ext = os.path.splitext(path)
    return f"{base}_compress{ext}"


def _to_return(buf, return_type):
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8") if return_type else buf


def _image_compress(path, target_size_mb, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = os.path.getsize(path)

    if file_size <= max_size:
        msg_logger.info(
            f"⌈文件处理⌋: 图片压缩 -> 图片无需压缩 {file_size}",
            extra={"event": "消息处理"},
        )
        return _read(path, return_type)
    img = Image.open(path).convert("RGB")
    if target_size_mb <= 64 / 1024:  # 缩略图
        width, height = img.size
        buffer = ""
        while file_size > max_size and (width > 50 and height > 50):
            width = int(width * 0.8)
            height = int(height * 0.8)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=20)  # 极低质量
            file_size = buffer.tell()
        msg_logger.info(
            f"⌈文件处理⌋: 图片压缩 -> 缩略图 size={file_size / 1024:.2f}KB, resolution={width}x{height}",
            extra={"event": "消息处理"},
        )
        with open(_get_compress_path(path), "wb") as f:
            f.write(buffer.getvalue())
        return _to_return(buffer, return_type)

    for quality in range(85, 25, -5):
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()
        if size <= max_size:
            msg_logger.info(
                f"⌈文件处理⌋: 图片压缩 -> 图片成功压缩到 size={size / 1024 / 1024}MB,quality={quality}",
                extra={"event": "消息处理"},
            )
            with open(_get_compress_path(path), "wb") as f:
                f.write(buffer.getvalue())
            return _to_return(buffer, return_type)
        msg_logger.info(
            f"⌈文件处理⌋: 图片压缩 -> 继续尝试 size={size / 1024 / 1024}MB,quality={quality}",
            extra={"event": "消息处理"},
        )
    msg_logger.error(
        f"⌈文件处理⌋: 图片压缩 -> 无法压缩图片至 {target_size_mb}MB",
        extra={"event": "消息处理"},
    )
    return None


async def image_compress(path, target_size_mb=10, return_type=None):
    """图片压缩"""
    comp_path = _get_compress_path(path)
    if os.path.exists(comp_path):
        msg_logger.info(
            f"⌈文件处理⌋: 图片压缩 -> 已存在文件 {comp_path}",
            extra={"event": "消息处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _image_compress, path, target_size_mb, return_type)


def _record_compress(path, target_size_mb, duration_limit_sec, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = os.path.getsize(path)
    try:
        duration = float(ffmpeg.probe(path)['format']['duration'])
    except ffmpeg.Error as e:
        msg_logger.error(f"⌈文件处理⌋: 音频压缩 -> probe 失败 : {e}", extra={"event": "消息处理"})
        return None
    dur = min(duration, duration_limit_sec or 1e9)
    if file_size <= max_size and (duration_limit_sec is None or duration <= duration_limit_sec):
        msg_logger.info(
            f"⌈文件处理⌋: 音频压缩 -> 音频无需压缩 {file_size}",
            extra={"event": "消息处理"},
        )
        return _read(path, return_type)

    bitrate = int((target_size_mb * 8 * 1024 * 1024) / dur)
    for _ in range(5):
        try:
            out, _ = (
                ffmpeg.input(path, t=duration_limit_sec)
                .output("pipe:", format="mp3", audio_bitrate=str(bitrate))
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            if len(out) <= max_size:
                msg_logger.info(
                    f"⌈文件处理⌋: 音频压缩 -> 音频成功压缩到 size={len(out) / 1024 / 1024:.2f}MB,bitrate={bitrate}",
                    extra={"event": "消息处理"},
                )
                with open(_get_compress_path(path), "wb") as f:
                    f.write(out)
                return _to_return(BytesIO(out), return_type)
            msg_logger.info(
                f"⌈文件处理⌋: 音频压缩 -> 继续尝试 size={len(out) / 1024 / 1024:.2f}MB,bitrate={bitrate}",
                extra={"event": "消息处理"},
            )
            bitrate = int(bitrate * 0.8)
        except Exception as e:
            msg_logger.error(f"⌈文件处理⌋: 音频压缩 -> ffmpeg 失败 : {e}", extra={"event": "消息处理"})
            return None
    msg_logger.error(
        f"⌈文件处理⌋: 音频压缩 -> 无法压缩音频至 {target_size_mb}MB",
        extra={"event": "消息处理"},
    )
    return None


async def record_compress(
        path,
        target_size_mb=2,
        duration_limit_sec=None,
        return_type=None
):
    """压缩音视频到指定大小"""
    comp_path = _get_compress_path(path)
    if os.path.exists(comp_path):
        msg_logger.info(
            f"⌈文件处理⌋: 音频压缩 -> 已存在文件 {comp_path}",
            extra={"event": "消息处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _record_compress, path, target_size_mb, duration_limit_sec,
                                      return_type)


def _video_compress(path, target_size_mb, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = os.path.getsize(path)
    if file_size <= max_size:
        msg_logger.info(
            f"⌈文件处理⌋: 视频压缩 -> 视频无需压缩 {file_size}",
            extra={"event": "消息处理"},
        )
        return _read(path, return_type)
    try:
        dur = float(ffmpeg.probe(path)['format']['duration'])
    except Exception as e:
        msg_logger.error(f"⌈文件处理⌋: 视频压缩 -> probe 失败 : {e}", extra={"event": "消息处理"})
        return None
    bitrate = int((target_size_mb * 8 * 1024 * 1024) / dur)
    for _ in range(5):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.close()
        try:
            (
                ffmpeg.input(path)
                .output(tmp.name, **{"b:v": str(bitrate)}, format="mp4")
                .overwrite_output()
                .run(quiet=True)
            )
            file_size = os.path.getsize(tmp.name)
            if os.path.getsize(tmp.name) <= max_size:
                shutil.move(tmp.name, _get_compress_path(path))
                msg_logger.info(
                    f"⌈文件处理⌋: 视频压缩 -> 视频成功压缩到 size={file_size / 1024 / 1024:.2f}MB,bitrate={bitrate}",
                    extra={"event": "消息处理"},
                )
                return _read(_get_compress_path(path), return_type)
            msg_logger.info(
                f"⌈文件处理⌋: 视频压缩 -> 继续尝试 size={os.path.getsize(tmp.name) / 1024 / 1024:.2f}MB,bitrate={bitrate}",
                extra={"event": "消息处理"},
            )
            bitrate = int(bitrate * 0.8)
        except Exception as e:
            msg_logger.error(f"⌈文件处理⌋: 视频压缩 -> ffmpeg 失败 : {e}", extra={"event": "消息处理"})
            return None
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)
    msg_logger.error(
        f"⌈文件处理⌋: 视频压缩 -> 无法压缩视频至 {target_size_mb}MB",
        extra={"event": "消息处理"},
    )
    return None


async def video_compress(path, target_size_mb=10, return_type=None):
    """异步压缩视频文件到指定大小"""
    comp_path = _get_compress_path(path)
    if os.path.exists(comp_path):
        msg_logger.info(
            f"⌈文件处理⌋: 视频压缩 -> 已存在文件 {comp_path}",
            extra={"event": "消息处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _video_compress, path, target_size_mb, return_type)
