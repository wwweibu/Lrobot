"""文件相关"""

import av
import pilk
import base64
import ffmpeg
import shutil
import asyncio
import tempfile
import textwrap
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ProcessPoolExecutor

from message.handler.msg import Msg
from config import connect, loggers, future, path

COMMAND_PATH = path / "storage/file/command"
COMMAND_PATH.mkdir(parents=True, exist_ok=True)
USER_PATH = path / "storage/file/user"
USER_PATH.mkdir(parents=True, exist_ok=True)
process_pool = ProcessPoolExecutor()
msg_logger = loggers["message"]


def text_wrap(draw, text, font, max_width):
    """转换文字"""
    lines = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")  # 保留空行
            continue
        line = ""
        for ch in paragraph:
            # 动态测量当前行宽
            if draw.textlength(line + ch, font=font) <= max_width:
                line += ch
            else:
                lines.append(line)
                line = ch
        if line:
            lines.append(line)
    return lines


async def text_to_image(text, output, font_path=path / "storage/file/command/simsun.ttc", font_size=24, max_width=800):
    """文字转图片"""
    font = ImageFont.truetype(font_path, font_size)

    tmp_img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(tmp_img)
    lines = text_wrap(draw, text, font, max_width=max_width - 40)
    # 计算图片大小
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 20  # 行高（含间距）
    img_height = line_height * len(lines) + 40

    img = Image.new("RGB", (max_width, int(img_height)), color="white")
    draw = ImageDraw.Draw(img)

    y = 20
    for line in lines:
        draw.text((20, y), line, font=font, fill="black")
        y += line_height
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    msg_logger.debug(
        f"[文图转换]转换成功-> 图片: {output}",
        extra={"event": "文件处理"},
    )


async def table_to_image(
        headers, rows, output,
        font_path="storage/file/command/simsun.ttc",
        font_size=24):
    """文字转表格图片"""
    padding_x = 20
    padding_y = 15
    border_width = 2
    font = ImageFont.truetype(font_path, font_size)

    # 临时画布用于测量
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    num_cols = len(headers)
    col_widths = [0] * num_cols

    # 精确计算列宽
    for i in range(num_cols):
        col_texts = [str(headers[i])]
        for row in rows:
            if i < len(row):
                col_texts.append(str(row[i]))
        max_w = 0
        for txt in col_texts:
            bbox = draw_tmp.textbbox((0, 0), txt, font=font)
            w = bbox[2] - bbox[0]
            if w > max_w:
                max_w = w
        col_widths[i] = int(max_w + padding_x * 2)

    # 计算行高
    sample_bbox = font.getbbox("汉")
    text_height = sample_bbox[3] - sample_bbox[1]
    row_height = int(text_height + padding_y * 2)

    table_width = int(sum(col_widths) + border_width)
    table_height = int(row_height * (len(rows) + 1) + border_width)

    img = Image.new("RGB", (table_width, table_height), color="white")
    draw = ImageDraw.Draw(img)

    # 绘制表头
    y = 0
    draw.rectangle([0, y, table_width, y + row_height],
                   fill="#E6E6E6", outline="#000000", width=border_width)

    x = 0
    for i, header in enumerate(headers):
        text = str(header)
        w = col_widths[i]
        text_w = draw.textlength(text, font=font)
        draw.text((int(x + (w - text_w) / 2), int(y + padding_y)),
                  text, font=font, fill="black")
        x += w
        draw.line([(int(x), 0), (int(x), table_height)],
                  fill="#000000", width=border_width)

    # 绘制表格内容
    for row_idx, row in enumerate(rows):
        y = int(row_height * (row_idx + 1))
        draw.rectangle([0, y, table_width, y + row_height],
                       fill="#FFFFFF", outline="#000000", width=border_width)

        x = 0
        for col_idx in range(num_cols):
            cell = row[col_idx] if col_idx < len(row) else ""
            text = str(cell)
            w = col_widths[col_idx]
            text_w = draw.textlength(text, font=font)
            draw.text((int(x + (w - text_w) / 2), int(y + padding_y)),
                      text, font=font, fill="black")
            x += w
        draw.line([(0, y), (table_width, y)],
                  fill="#000000", width=border_width)

    # 保存图片
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output)

    msg_logger.debug(f"[表格图片]转换成功 -> 图片: {output}",
                     extra={"event": "文件处理"})


async def image_merge(image_paths, output, direction="vertical", padding=0):
    """合并多张图片"""
    images = [Image.open(p).convert("RGB") for p in image_paths]

    if direction == "vertical":
        avg_width = int(sum(img.width for img in images) / len(images))
        resized = []
        for img in images:
            new_h = int(img.height * (avg_width / img.width))
            resized.append(img.resize((avg_width, new_h), Image.Resampling.LANCZOS))

        total_height = sum(img.height for img in resized) + padding
        merged = Image.new("RGB", (avg_width, total_height), "white")

        y_offset = padding
        for img in resized:
            merged.paste(img, (0, y_offset))
            y_offset += img.height
    else:  # 横向拼接
        avg_height = int(sum(img.height for img in images) / len(images))
        resized = []
        for img in images:
            new_w = int(img.width * (avg_height / img.height))
            resized.append(img.resize((new_w, avg_height), Image.Resampling.LANCZOS))

        total_width = sum(img.width for img in resized) + padding
        merged = Image.new("RGB", (total_width, avg_height), "white")

        x_offset = padding
        for img in resized:
            merged.paste(img, (x_offset, 0))
            x_offset += img.width
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    merged.save(output)
    msg_logger.debug(f"[图像合并]合并成功-> 图片: {output}", extra={"event": "文件处理"})


def file_name_overwrite(file_path):
    """如果文件存在，则自动生成 file (1).ext"""
    file_path = Path(file_path)
    base, ext = file_path.stem, file_path.suffix
    parent = file_path.parent

    counter = 1
    new_path = file_path
    while new_path.exists():
        new_path = parent / f"{base} ({counter}){ext}"
        counter += 1
    return new_path


async def file_download(file_path, url=None, data=None):
    """文件下载"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if data:
        with open(file_path, "wb") as f:
            f.write(data)
    else:
        async with connect() as client:
            response = await client.get(url)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
    msg_logger.debug(
        f"[文件下载]下载成功-> 文件: {file_path}",
        extra={"event": "文件处理"},
    )


async def remove_later(file_path, delay=60):
    """延迟删除文件"""
    await asyncio.sleep(delay)
    file_path = Path(file_path)
    try:
        if file_path.exists():
            file_path.unlink()
            msg_logger.debug(f"[文件删除]已删除临时文件-> {file_path}", extra={"event": "文件处理"})
    except Exception as e:
        msg_logger.error(
            f"[文件删除]延迟删除失败-> {file_path}: {type(e).__name__}: {e}", extra={"event": "文件处理"}
        )
        pass

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
        msg_logger.debug(
            f"[音频转换]pcm 写入-> 音频: {pcm_path}",
            extra={"event": "文件处理"},
        )
        # PCM → silk
        pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
        msg_logger.debug(
            f"[音频转换]pcm 转 silk-> 音频: {silk_path}",
            extra={"event": "文件处理"},
        )
        Path(pcm_path).unlink()
        return silk_path
    except Exception as e:
        msg_logger.error(
            f"[音频转换]silk 转换失败-> 错误: {type(e).__name__}: {e}",
            extra={"event": "文件处理"},
        )
        return None


async def record_convert(media_path):
    """任意媒体文件转 silk"""
    silk_path = Path(media_path).with_suffix(".silk")

    if Path(silk_path).exists():
        msg_logger.debug(
            f"[音频转换]silk 已存在-> 音频: {silk_path}",
            extra={"event": "文件处理"},
        )
        return silk_path

    # 在后台线程执行
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _record_convert, media_path, silk_path)


def _read(file_path, return_type):
    """分别对应 open(file_path, "rb") 和 with open(file_path, "rb") as f: file_data = base64.b64encode(f.read()).decode("utf-8")"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8") if return_type else BytesIO(f.read())


def _compress_path_get(file_path):
    file_path = Path(file_path)
    return file_path.with_stem(f"{file_path.stem}_compress")


def _to_return(buf, return_type):
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8") if return_type else buf


def _image_compress(file_path, target_size_mb, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size

    if file_size <= max_size:
        msg_logger.debug(
            f"[图片压缩]图片无需压缩-> 大小: {file_size}",
            extra={"event": "文件处理"},
        )
        return _read(file_path, return_type)
    img = Image.open(file_path).convert("RGB")
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
        msg_logger.debug(
            f"[图片压缩]缩略图压缩完成-> 大小: {file_size / 1024:.2f}KB | 分辨率: {width}x{height}",
            extra={"event": "文件处理"},
        )
        with open(_compress_path_get(file_path), "wb") as f:
            f.write(buffer.getvalue())
        return _to_return(buffer, return_type)

    for quality in range(85, 25, -5):
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()
        if size <= max_size:
            msg_logger.debug(
                f"[图片压缩]压缩完成-> 大小: {size / 1024 / 1024}MB | 品质: {quality}",
                extra={"event": "文件处理"},
            )
            with open(_compress_path_get(file_path), "wb") as f:
                f.write(buffer.getvalue())
            return _to_return(buffer, return_type)
        msg_logger.debug(
            f"[图片压缩]压缩继续-> 大小: {size / 1024 / 1024}MB | 品质: {quality}",
            extra={"event": "文件处理"},
        )
    msg_logger.error(
        f"[图片压缩]压缩失败-> 错误: 无法压缩图片至 {target_size_mb}MB",
        extra={"event": "文件处理"},
    )
    return None


async def image_compress(file_path, target_size_mb=10, return_type=None):
    """图片压缩"""
    comp_path = _compress_path_get(file_path)
    if Path(comp_path).exists():
        msg_logger.debug(
            f"[图片压缩]图片已存在-> 图片: {comp_path}",
            extra={"event": "文件处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _image_compress, file_path, target_size_mb, return_type)


def _record_compress(file_path, target_size_mb, duration_limit_sec, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size
    try:
        duration = float(ffmpeg.probe(file_path)['format']['duration'])
    except ffmpeg.Error as e:
        msg_logger.error(f"[音频压缩]probe 错误-> 错误: {type(e).__name__}: {e}", extra={"event": "文件处理"})
        return None
    dur = min(duration, duration_limit_sec or 1e9)
    if file_size <= max_size and duration == dur:
        msg_logger.debug(
            f"[音频压缩]音频无需压缩-> 大小: {file_size}",
            extra={"event": "文件处理"},
        )
        return _read(file_path, return_type)

    bitrate = int((target_size_mb * 8 * 1024 * 1024) / dur)
    for _ in range(5):
        try:
            out, _ = (
                ffmpeg.input(file_path, t=dur)
                .output("pipe:", format="mp3", audio_bitrate=str(bitrate))
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            if len(out) <= max_size:
                msg_logger.debug(
                    f"[音频压缩]压缩完成-> 大小: {len(out) / 1024 / 1024:.2f}MB | 比特率: {bitrate}",
                    extra={"event": "文件处理"},
                )
                with open(_compress_path_get(file_path), "wb") as f:
                    f.write(out)
                return _to_return(BytesIO(out), return_type)
            msg_logger.debug(
                f"[音频压缩]压缩继续-> 大小: {len(out) / 1024 / 1024:.2f}MB | 比特率: {bitrate}",
                extra={"event": "文件处理"},
            )
            bitrate = int(bitrate * 0.8)
        except Exception as e:
            msg_logger.error(f"[音频压缩]ffmpeg 错误-> 错误: {type(e).__name__}: {e}", extra={"event": "文件处理"})
            return None
    msg_logger.error(
        f"[音频压缩]压缩失败-> 错误: 无法压缩音频至 {target_size_mb}MB",
        extra={"event": "文件处理"},
    )
    return None


async def record_compress(
        file_path,
        target_size_mb=2,
        duration_limit_sec=None,
        return_type=None
):
    """压缩音视频到指定大小"""
    comp_path = _compress_path_get(file_path)
    if Path(comp_path).exists():
        msg_logger.debug(
            f"[音频压缩]音频已存在-> 音频: {comp_path}",
            extra={"event": "文件处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _record_compress, file_path, target_size_mb, duration_limit_sec,
                                      return_type)


def _video_compress(file_path, target_size_mb, return_type):
    max_size = target_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size
    if file_size <= max_size:
        msg_logger.debug(
            f"[视频压缩]视频无需压缩-> 大小: {file_size}",
            extra={"event": "文件处理"},
        )
        return _read(file_path, return_type)
    try:
        dur = float(ffmpeg.probe(file_path)['format']['duration'])
    except Exception as e:
        msg_logger.error(f"[视频压缩]probe 错误-> 错误: {type(e).__name__}: {e}", extra={"event": "文件处理"})
        return None
    bitrate = int((target_size_mb * 8 * 1024 * 1024) / dur)
    for _ in range(5):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.close()
        try:
            (
                ffmpeg.input(file_path)
                .output(tmp.name, **{"b:v": str(bitrate)}, format="mp4")
                .overwrite_output()
                .run(quiet=True)
            )
            file_size = Path(tmp.name).stat().st_size
            if file_size <= max_size:
                shutil.move(tmp.name, _compress_path_get(file_path))
                msg_logger.debug(
                    f"[视频压缩]压缩完成-> 大小: {file_size / 1024 / 1024:.2f}MB | 比特率: {bitrate}",
                    extra={"event": "文件处理"},
                )
                return _read(_compress_path_get(file_path), return_type)
            msg_logger.debug(
                f"[视频压缩]压缩继续-> 大小: {file_size / 1024 / 1024:.2f}MB | 比特率: {bitrate}",
                extra={"event": "文件处理"},
            )
            bitrate = int(bitrate * 0.8)
        except Exception as e:
            msg_logger.error(f"[视频压缩]ffmpeg 错误-> 错误: {type(e).__name__}: {e}", extra={"event": "文件处理"})
            return None
        finally:
            if Path(tmp.name).exists():
                Path(tmp.name).unlink()
    msg_logger.error(
        f"[视频压缩]压缩失败-> 错误: 无法压缩视频至 {target_size_mb}MB",
        extra={"event": "文件处理"},
    )
    return None


async def video_compress(file_path, target_size_mb=10, return_type=None):
    """异步压缩视频文件到指定大小"""
    comp_path = _compress_path_get(file_path)
    if Path(comp_path).exists():
        msg_logger.debug(
            f"[视频压缩]视频已存在-> 视频: {comp_path}",
            extra={"event": "文件处理"},
        )
        return _read(comp_path, return_type)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(process_pool, _video_compress, file_path, target_size_mb, return_type)


async def bv_download(bv, file_path):
    """下载 bv"""
    msg = Msg(
        platform="BILI",
        kind="私聊视频下载",
        event="发送",
        content=bv,
    )
    dash = await future.wait(msg.num, f"[文件处理]下载链接请求超时-> 视频: {bv}")

    url = dash.get("audio", [])[0].get("baseUrl") if dash.get("audio", []) else None
    if not url:
        raise Exception(f"[文件处理]未获取到下载链接-> 视频: {bv}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }
    temp_m4s = None
    try:
        # 下载音频文件
        with tempfile.NamedTemporaryFile(suffix=".m4s", delete=False) as temp_m4s_file:
            temp_m4s = temp_m4s_file.name
            async with connect() as client:
                async with client.stream("GET", url, headers=headers) as r:
                    if r.status_code != 200:
                        raise Exception(f"[文件处理]下载失败-> {url}: {r.status_code}")
                    async for chunk in r.aiter_bytes():
                        temp_m4s_file.write(chunk)

        # 转换为wav格式
        try:
            (
                ffmpeg
                .input(temp_m4s)
                .output(
                    str(file_path),
                    format="wav",  # 指定容器为 wav
                    acodec="pcm_s16le",  # 16-bit PCM
                    ac=1,  # 单声道
                    ar="16000",  # 16kHz 采样率
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
            msg_logger.error(f"[音频转换]ffmpeg 错误-> 错误: {type(e).__name__}: {err_msg}",
                             extra={"event": "文件处理"})
            raise

    finally:
        # 删除临时文件
        if temp_m4s and Path(temp_m4s).exists():
            try:
                Path(temp_m4s).unlink()
            except Exception as e:
                msg_logger.error(
                    f"[文件删除]临时文件删除失败-> {temp_m4s}: {type(e).__name__}: {e}",
                    extra={"event": "文件处理"},
                )
