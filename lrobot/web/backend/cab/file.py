"""网盘相关操作"""

import io
import json
import shutil
import asyncio
import chardet
import hashlib
import zipfile
import mimetypes
import threading
import subprocess
import pandas as pd
from datetime import datetime
from urllib.parse import quote
from typing import AsyncIterator
from pathlib import Path, PurePosixPath
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import UploadFile, File, Request, Form, Response

from config import path, monitor_adapter
from .base import APIRouter, Depends, R, website_logger, cookie_account_get, Dict, Query


UPLOAD_DIR = path / "storage/file/clouddrive"
RECYCLE_BIN = path / "storage/file/recycle"
TEMP_CHUNKS_DIR = RECYCLE_BIN / ".temp_chunks"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RECYCLE_BIN.mkdir(parents=True, exist_ok=True)
FILE_INDEX = []  # 全局文件索引
INDEX_LOCK = threading.Lock()

router = APIRouter()


def async_index_build():
    """异步构建索引"""
    threading.Thread(target=index_build, args=(UPLOAD_DIR,), daemon=True).start()


def index_build(base_path: Path):
    """构建索引(7k,6s)"""
    with INDEX_LOCK:
        FILE_INDEX.clear()
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for item_path in base_path.rglob('*'):
                futures.append(executor.submit(item_make, item_path, base_path))

            for f in futures:
                item = f.result()
                if item:
                    FILE_INDEX.append(item)


def item_make(full_path: Path, base_path: Path):
    """返回指定格式"""
    try:
        return {
            "name": full_path.name,
            "path": str(full_path.relative_to(base_path)).replace("\\", "/"),
            "is_dir": full_path.is_dir(),
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
            "size": full_path.stat().st_size if full_path.is_file() else 0,
        }
    except FileNotFoundError:
        return None


def folder_size_get(folder: Path):
    """递归计算文件夹总大小（字节）"""
    total = 0
    for f in folder.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
            if total > 2 * 1024 * 1024 * 1024:
                return total
    return total


def path_check(file_path, base_path=UPLOAD_DIR):
    """路径合法性检查"""
    try:
        file_path = PurePosixPath(file_path)
    except Exception as e:
        return f"路径格式错误: {e}"

    resolved_path = (base_path / file_path).resolve()
    if not resolved_path.is_relative_to(base_path):
        return "路径超出允许范围"
    resolved_path.mkdir(parents=True, exist_ok=True)
    return "路径正确"

@router.post("/file/chunk")
@monitor_adapter("#内阁_文件上传")
async def file_chunk_upload(
        file: UploadFile = File(...),
        upload_id: str = Form(...),
        filename: str = Form(...),
        chunk_index: int = Form(...),
        total_chunks: int = Form(...),
        base_path: str = Form(""),
    account: str = Depends(cookie_account_get),
):
    """上传文件"""
    if not account:
        return

    check = path_check(base_path)
    if check != "路径正确":
        return R(status="fail", data=check)

    # 临时目录：UPLOAD_DIR/.temp_chunks/{upload_id}/
    temp_dir = TEMP_CHUNKS_DIR / upload_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 使用固定宽度数字命名，保证排序正确
    part_name = f"{chunk_index:06d}.part"
    part_path = temp_dir / part_name

    # 保存分片
    try:
        with part_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        return R(status="fail", data=f"保存分片失败: {e}")

    # 如果是最后一个分片，进行合并
    if chunk_index == total_chunks - 1:
        try:
            # 检查所有分片是否存在
            for i in range(total_chunks):
                p = temp_dir / f"{i:06d}.part"
                if not p.exists():
                    return R(status="fail", data=f"缺少分片: {i}")

            # 目标目录
            target_dir = UPLOAD_DIR / base_path if base_path else UPLOAD_DIR
            dest = target_dir / filename

            if dest.exists():
                # 清理临时分片并返回错误，避免残留
                shutil.rmtree(temp_dir, ignore_errors=True)
                return R(status="fail", data=f"文件已存在: {filename}")

            # 合并分片
            with dest.open("wb") as outfile:
                for i in range(total_chunks):
                    part_file = temp_dir / f"{i:06d}.part"
                    with part_file.open("rb") as pf:
                        shutil.copyfileobj(pf, outfile)

            # 清理临时分片
            shutil.rmtree(temp_dir, ignore_errors=True)

            saved_files = [str((Path(base_path) / filename)) if base_path else str(Path(filename))]
            website_logger.info(f"[文件上传]{account}-> {str(Path(base_path) / filename)}",
                                extra={"event": "网页日志"})

            # 触发索引（保持原有逻辑）
            async_index_build()

            return R(status="success", data=saved_files)
        except Exception as e:
            # 出错时尝试清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            return R(status="fail", data=f"合并分片失败: {e}")

    # 非最后分片只返回上传成功
    return R(status="success", data=f"chunk {chunk_index} uploaded")


@router.post("/file/folders/chunk")
@monitor_adapter("#内阁_文件夹上传")
async def file_folders_chunk_upload(
        file: UploadFile = File(...),
        upload_id: str = Form(...),
        filename: str = Form(...),
        chunk_index: int = Form(...),
        total_chunks: int = Form(...),
        base_path: str = Form(""),
        relative_path: str = Form(...),  # 相对于上传根目录的路径，例如 "dir1/sub/file.txt"
        account: str = Depends(cookie_account_get),
):
    """接收文件夹内单个文件的分片并在接收最后一个分片时合并保存为相对路径文件。"""
    if not account:
        return

    check1 = path_check(base_path)
    if check1 != "路径正确":
        return R(status="fail", data=check1)
    check2 = path_check(relative_path)
    if check2 != "路径正确":
        return R(status="fail", data=check2)

    temp_dir = TEMP_CHUNKS_DIR / upload_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    part_name = f"{chunk_index:06d}.part"
    part_path = temp_dir / part_name

    try:
        with part_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        return R(status="fail", data=f"保存分片失败: {e}")

    if chunk_index == total_chunks - 1:
        try:
            # 验证分片完整性
            for i in range(total_chunks):
                p = temp_dir / f"{i:06d}.part"
                if not p.exists():
                    return R(status="fail", data=f"缺少分片: {i}")

            # 目标文件路径（包含 base_path + relative_path）
            full_rel = Path(relative_path)
            target_dir = (UPLOAD_DIR / base_path / full_rel.parent) if base_path else (UPLOAD_DIR / full_rel.parent)
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = (target_dir / full_rel.name)

            if dest.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                return R(status="fail", data=f"文件已存在: {relative_path}")

            with dest.open("wb") as outfile:
                for i in range(total_chunks):
                    part_file = temp_dir / f"{i:06d}.part"
                    with part_file.open("rb") as pf:
                        shutil.copyfileobj(pf, outfile)

            shutil.rmtree(temp_dir, ignore_errors=True)

            saved_files = [str((Path(base_path) / relative_path)) if base_path else str(Path(relative_path))]
            website_logger.info(f"[文件夹上传]{account}-> {saved_files[0]}", extra={"event": "网页日志"})

            async_index_build()
            return R(status="success", data=saved_files)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return R(status="fail", data=f"合并分片失败: {e}")

    return R(status="success", data=f"chunk {chunk_index} uploaded")

@router.delete("/file")
@monitor_adapter("#内阁_文件删除")
async def files_delete(data: str = Query(...), account: str = Depends(cookie_account_get)):
    """删除文件"""
    if not account:
        return
    data_dict = json.loads(data)
    file_path = data_dict["path"]
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)

    try:
        target_path = UPLOAD_DIR / file_path
        if target_path == UPLOAD_DIR:
            return R(status="fail", data="不能删除根目录")

        if not target_path.exists():
            return R(status="fail", data="路径不存在")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f"{target_path.name}_{timestamp}"

        recycle_path = RECYCLE_BIN / new_name

        shutil.move(str(target_path), str(recycle_path))

        website_logger.info(
            f"[文件删除]{account}-> {str(target_path)}", extra={"event": "网页日志"}
        )

        async_index_build()
        return R(status="success", data=str(target_path))

    except PermissionError:
        return R(status="fail", data="没有删除权限")
    except Exception as e:
        website_logger.error(f"[文件页]删除失败-> {type(e).__name__}: {e}", extra={"event": "网页日志"})
        return R(status="fail", data=f"删除操作失败: {str(e)}")


@router.post("/file/new_folders")
@monitor_adapter("#内阁_文件夹新建")
async def file_folders_create(data: Dict, account: str = Depends(cookie_account_get)):
    """新建文件夹"""
    if not account:
        return
    file_path = data["path"]
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)
    if file_path == "none":
        file_path = ""
    full_path = UPLOAD_DIR / file_path
    if full_path.exists():
        return R(status="fail", data="文件夹已存在")
    try:
        full_path.mkdir(parents=True, exist_ok=False)
    except Exception as e:
        return R(status="fail", data=f"文件夹创建失败: {e}")

    website_logger.info(
        f"[文件夹新建]{account}-> {str(full_path)}", extra={"event": "网页日志"}
    )
    async_index_build()
    return R(status="success", data=str(full_path))


@router.post("/file/search")
async def files_search(data: Dict):
    """搜索文件"""
    file_path = data["path"]
    keyword = data["keyword"]
    if file_path == "none":
        file_path = ""
    keyword_lower = keyword.lower()
    result = [
        item for item in FILE_INDEX
        if item["path"].startswith(file_path)  # 只在 path 子目录下搜索
           and keyword_lower in item["name"].lower()
    ]
    return R(status="success", data=result)


@router.put("/file/rename")
@monitor_adapter("#内阁_文件重命名")
async def files_rename(data: Dict, account: str = Depends(cookie_account_get)):
    """重命名文件"""
    if not account:
        return
    old_path = data["old_path"]
    if old_path == "none":
        old_path = ""
    new_path = data["new_path"]
    if new_path == "none":
        new_path = ""
    if not new_path:
        return R(status="fail", data="新名称不能为空")
    check1 = path_check(old_path)
    if check1 != "路径正确":
        return R(status="fail", data=check1)
    check2 = path_check(new_path)
    if check2 != "路径正确":
        return R(status="fail", data=check2)

    old_item = UPLOAD_DIR / old_path
    new_item = old_item.with_name(new_path)

    if not old_item.exists():
        return R(status="fail", data="原文件不存在")
    if new_item.exists():
        return R(status="fail", data="目标文件已存在")

    website_logger.info(
        f"[文件重命名]{account}-> {old_item}: {new_item}", extra={"event": "网页日志"}
    )
    old_item.rename(new_item)
    async_index_build()
    return R(status="success", data=f"原路径: {old_item} 目标路径: {new_item}")


@router.post("/file/move")
@monitor_adapter("#内阁_文件移动")
async def files_move(data: Dict, account: str = Depends(cookie_account_get)):
    """移动文件"""
    if not account:
        return
    src_path = data["src_path"]
    if src_path == "none":
        src_path = ""
    dst_path = data["dst_path"]
    if dst_path == "none":
        dst_path = ""
    check1 = path_check(src_path)
    if check1 != "路径正确":
        return R(status="fail", data=check1)
    check2 = path_check(dst_path)
    if check2 != "路径正确":
        return R(status="fail", data=check2)

    src_item = UPLOAD_DIR / src_path
    dst_item = UPLOAD_DIR / dst_path
    if not src_item.exists():
        return R(status="fail", data=f"源文件不存在: {src_item}")
    if dst_item.exists():
        return R(status="fail", data=f"目标文件已存在: {dst_item}")

    try:
        shutil.move(str(src_item), str(dst_item))
        website_logger.info(
            f"[文件移动]{account}-> {str(src_item)}: {str(dst_item)}",
            extra={"event": "网页日志"},
        )
        async_index_build()
        return R(status="success", data=f"原目录:{src_item} 目标目录: {dst_item}")
    except Exception as e:
        return R(status="fail", data=f"文件移动失败: {e}")


def unique_pdf_name_get(doc_path):
    """获取唯一文件名（根据内容生成哈希)"""
    file_hash = hashlib.md5(doc_path.read_bytes()).hexdigest()[:8]
    base_name = doc_path.stem  # 不含后缀的文件名
    return f"{base_name}_{file_hash}.pdf"


@router.post("/file/preview")
async def files_preview(data: dict):
    """文件预览"""
    file_path = data["path"][0]
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        return {"error": "文件不存在"}

    # 支持类型
    mime_type, _ = mimetypes.guess_type(str(full_path))
    mime_type = mime_type or "application/octet-stream"

    # 类型转文本
    if full_path.suffix.lower() in [".asp", ".md", ".cfm", ".inc", ".dat", ".data", ".ini", ".lst", ".obj", ".xml",
                                    ".yaml", ".raw", ".log", ".yml"]:
        mime_type = "text/plain"

    # Word / PPT 转 PDF
    if mime_type in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12",  # .pptm
        "application/rtf",
        "text/rtf",  # .rtf
        "application/wps-office.wps",
        "application/vnd.ms-works",  # .wps
    ]:
        pdf_filename = unique_pdf_name_get(full_path)
        pdf_path = RECYCLE_BIN / pdf_filename

        if not pdf_path.exists():
            await asyncio.to_thread(
                subprocess.run,
                [
                    "soffice", "--headless", "--convert-to", "pdf",
                    str(full_path), "--outdir", str(RECYCLE_BIN)
                ],
                check=True,
            )
        generated_pdf = RECYCLE_BIN / full_path.with_suffix(".pdf").name
        if generated_pdf.exists():
            generated_pdf.rename(pdf_path)
        return FileResponse(
            str(pdf_path), media_type="application/pdf", filename=pdf_path.name
        )

    if mime_type == "application/vnd.ms-excel":
        xlsx_filename = unique_pdf_name_get(full_path)
        xlsx_path = RECYCLE_BIN / xlsx_filename
        if not xlsx_path.exists():
            df = pd.read_excel(full_path, sheet_name=None)
            with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
                for sheet_name, sheet_df in df.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
        return FileResponse(
            str(xlsx_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=xlsx_path.name,
        )

    # 文本类：探测编码 → 转 UTF-8
    if mime_type.startswith("text/"):
        raw = await asyncio.to_thread(full_path.read_bytes)
        enc = chardet.detect(raw)["encoding"] or "utf-8"
        try:
            text = raw.decode(enc)
        except Exception:
            # 极端情况下探测失败，直接按系统默认编码
            text = raw.decode("gb18030", errors="ignore")
        # 统一用 UTF-8 返回
        return Response(content=text, media_type=mime_type + "; charset=utf-8")

    return FileResponse(str(full_path), media_type=mime_type, filename=full_path.name)


@router.get("/file/stream_video")
async def files_stream_preview(request: Request, file_path: str = Query(...)):
    """视频流式预览"""
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        return {"error": "视频不存在"}

    if full_path.suffix.lower() == ".f4v":
        mp4_filename = full_path.stem + ".mp4"
        mp4_path = RECYCLE_BIN / mp4_filename

        # 如果没转过，就执行 ffmpeg 转封装
        if not mp4_path.exists():
            await asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-i", str(full_path), "-c", "copy", str(mp4_path)],
                check=True,
            )

        # 转换完成后，直接返回 mp4 文件
        return FileResponse(
            str(mp4_path),
            media_type="video/mp4",
            filename=mp4_path.name,
        )

    if full_path.suffix.lower() in [".wmv", ".avi"]:
        mp4_filename = full_path.stem + ".mp4"
        mp4_path = RECYCLE_BIN / mp4_filename

        if not mp4_path.exists():
            await asyncio.to_thread(
                subprocess.run,
                [
                    "ffmpeg", "-i", str(full_path),
                    "-c:v", "libx264", "-c:a", "aac",
                    "-movflags", "+faststart",
                    str(mp4_path),
                ],
                check=True,
            )

        return FileResponse(
            str(mp4_path),
            media_type="video/mp4",
            filename=mp4_path.name,
        )

    file_size = full_path.stat().st_size
    range_header = request.headers.get("range")

    start = 0
    end = file_size - 1

    if range_header:
        # 支持 Range 请求
        range_match = range_header.replace("bytes=", "").split("-")
        try:
            start = int(range_match[0])
            if range_match[1]:
                end = int(range_match[1])
        except ValueError:
            pass  # fallback to default

    chunk_size = end - start + 1

    async def iterfile():
        """文件分块"""
        with open(full_path, "rb") as f:
            f.seek(start)
            remaining = chunk_size
            block_size = 1024 * 1024  # 每块1MB，避免一次性读取太多
            while remaining > 0:
                read_size = min(block_size, remaining)
                data = await asyncio.to_thread(f.read, read_size)
                if not data:
                    break
                yield data
                remaining -= len(data)

    return StreamingResponse(
        iterfile(),
        status_code=206,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4",
            "Cache-Control": "public, max-age=3600",  # 加快浏览器重复加载
        },
    )


async def file_iterator(file_path: Path, chunk_size: int = 1024 * 1024) -> AsyncIterator[bytes]:
    """流式读取文件，每次读取 chunk_size 字节"""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def zip_directory_generator(directory_path: Path, chunk_size: int = 64 * 1024):
    """使用生成器流式压缩文件夹"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(directory_path)
                with open(file_path, 'rb') as f:
                    info = zipfile.ZipInfo.from_file(file_path, arcname)
                    with zip_file.open(info, 'w') as dest:
                        while chunk := f.read(chunk_size):
                            dest.write(chunk)
    zip_buffer.seek(0)
    while chunk := zip_buffer.read(chunk_size):
        yield chunk


@router.get("/file/download/{file_path:path}")
async def download_file(file_path: str):
    """流式下载文件或文件夹"""
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)
    file_path = (UPLOAD_DIR / file_path).resolve()

    # 文件/文件夹不存在
    if not file_path.exists():
        return R(status="fail", data="文件不存在")

    # 如果是文件，直接流式返回
    if file_path.is_file():
        return StreamingResponse(
            file_iterator(file_path),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{quote(file_path.name)}"',
                "Content-Length": str(file_path.stat().st_size),
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff"
            }
        )

    # 如果是文件夹，检查大小
    elif file_path.is_dir():
        folder_size = folder_size_get(file_path)

        if folder_size > 2 * 1024 * 1024 * 1024:  # 2GB
            return R(status="fail", data="文件夹总大小大于2GB，请单独下载内容")

        # 流式压缩并返回
        zip_filename = f"{file_path.name}.zip"

        return StreamingResponse(
            zip_directory_generator(file_path),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{quote(zip_filename)}"',
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff"
            }
        )

    else:
        return R(status="fail", data="文件不存在")


@router.get("/file/{file_path:path}")
async def files_get(file_path: str = ""):
    """访问文件夹目录"""
    if file_path == "none":
        file_path = ""
    check = path_check(file_path)
    if check != "路径正确":
        return R(status="fail", data=check)
    base_path = UPLOAD_DIR / file_path

    if not base_path.exists():
        return R(status="fail", data="页面不存在")

    items = []
    for item in base_path.iterdir():
        items.append(
            {
                "name": item.name,
                "path": str(item.relative_to(UPLOAD_DIR)),
                "is_dir": item.is_dir(),
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                "size": item.stat().st_size if item.is_file() else 0,
            }
        )
    return R(status="success", data=items)


index_build(UPLOAD_DIR)
