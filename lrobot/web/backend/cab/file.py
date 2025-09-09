"""网盘相关操作"""
import os
import asyncio
import shutil
import chardet
import hashlib
import tempfile
import mimetypes
import threading
import subprocess
import pandas as pd
from typing import List
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import UploadFile, File, Request, HTTPException, APIRouter, Form, Depends, Response

from config import path, loggers
from .cookie import cookie_account_get

router = APIRouter()
website_logger = loggers["website"]
UPLOAD_DIR = path / "storage/file/clouddrive"
RECYCLE_BIN = path / "storage/file/recycle"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RECYCLE_BIN.mkdir(parents=True, exist_ok=True)
FILE_INDEX = []  # 全局文件索引
INDEX_LOCK = threading.Lock()


def rebuild_index_async():
    """异步构建索引"""
    threading.Thread(target=build_index, args=(UPLOAD_DIR,), daemon=True).start()


def build_index(base_path: Path):
    """构建索引(7k,6s)"""
    with INDEX_LOCK:
        FILE_INDEX.clear()
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for root, dirs, files in os.walk(base_path):
                for name in dirs + files:
                    full_path = Path(root) / name
                    futures.append(executor.submit(make_item, full_path, base_path))

            for f in futures:
                item = f.result()
                if item:
                    FILE_INDEX.append(item)


def make_item(full_path: Path, base_path: Path):
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


async def remove_later(path, delay=60):
    """延迟删除文件"""
    await asyncio.sleep(delay)
    try:
        os.remove(path)
    except Exception as e:
        website_logger.info(
            f"删除文件失败: {path}", extra={"event": "文件删除"}
        )
        pass


def get_folder_size(folder: Path) -> int:
    """递归计算文件夹总大小（字节）"""
    total = 0
    for f in folder.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
            if total > 2 * 1024 * 1024 * 1024:
                return total
    return total


@router.post("/file")
async def files_upload(
    files: List[UploadFile] = File(...),
    paths: str = Form(...),
    account: str = Depends(cookie_account_get),
):
    """上传文件"""
    if not account:
        return
    saved_files = []
    target_dir = UPLOAD_DIR / paths
    target_dir.mkdir(parents=True, exist_ok=True)
    for file in files:
        dest = target_dir / file.filename
        if dest.exists():
            raise HTTPException(403, f"文件已存在: {file.filename}")
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(str((Path(paths) / file.filename)))
        website_logger.info(
            f"{account} 上传文件: {paths}/{file.filename}", extra={"event": "管理操作"}
        )
    rebuild_index_async()
    return {"uploaded": saved_files}


@router.delete("/file")
async def files_delete(request: Request, account: str = Depends(cookie_account_get)):
    """删除文件"""
    if not account:
        return
    data = await request.json()
    path = data["path"].lstrip("/\\")
    try:
        target_path = UPLOAD_DIR / path
        if target_path == UPLOAD_DIR:
            raise HTTPException(403, "不能删除根目录")
        resolved_path = target_path.resolve()
        if not resolved_path.is_relative_to(UPLOAD_DIR.resolve()):
            raise HTTPException(400, "非法路径访问")

        # 安全验证
        if ".." in path.split("/"):
            raise HTTPException(400, "路径包含非法字符")

        if not target_path.exists():
            raise HTTPException(404, "路径不存在")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f"{target_path.name}_{timestamp}"

        recycle_path = RECYCLE_BIN / new_name

        shutil.move(str(target_path), str(recycle_path))

        website_logger.info(
            f"{account} 删除文件: {str(target_path)}", extra={"event": "管理操作"}
        )

        rebuild_index_async()

        return {"status": "success", "deleted_path": str(target_path)}

    except PermissionError:
        raise HTTPException(403, "没有删除权限")
    except Exception as e:
        raise HTTPException(500, f"删除操作失败: {str(e)}")


@router.post("/file/folders")
async def file_folders_upload(
    files: List[UploadFile] = File(...),
    paths: List[str] = Form(...),
    account: str = Depends(cookie_account_get),
):
    """上传文件夹"""
    if not account:
        return
    saved_files = []
    print(files)
    print(paths)

    for file, relative_path in zip(files, paths):
        # 构造完整保存路径
        dest = UPLOAD_DIR / relative_path

        # 创建父目录
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        saved_files.append(str(relative_path))

        website_logger.info(
            f"{account} 上传文件夹: {str(relative_path)}", extra={"event": "管理操作"}
        )
    rebuild_index_async()

    return {"uploaded": saved_files}


@router.post("/file/new_folders")
async def file_folders_create(
    request: Request, account: str = Depends(cookie_account_get)
):
    """新建文件夹"""
    if not account:
        return
    data = await request.json()
    path = data["path"].lstrip("/\\")
    full_path = UPLOAD_DIR / path
    full_path = full_path.resolve()
    # 防止路径跳出上传目录
    if not str(full_path).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path.mkdir(parents=True, exist_ok=True)
    website_logger.info(
        f"{account} 新建文件夹:{str(full_path)}", extra={"event": "管理操作"}
    )
    rebuild_index_async()
    return {"path": str(full_path)}


@router.get("/file/search")
async def files_search(path: str, keyword: str):
    """搜索文件"""
    if path == "none":
        path = ""
    keyword_lower = keyword.lower()
    result = [
        item for item in FILE_INDEX
        if item["path"].startswith(path)  # 只在 path 子目录下搜索
           and keyword_lower in item["name"].lower()
    ]
    return {"items": result}


@router.put("/file/rename")
async def files_rename(request: Request, account: str = Depends(cookie_account_get)):
    """重命名文件"""
    if not account:
        return
    data = await request.json()
    old_path = data["old_path"]
    new_path = data["new_path"]
    old_item = UPLOAD_DIR / old_path
    new_item = old_item.with_name(new_path)

    if not old_item.exists():
        raise HTTPException(status_code=404, detail="原文件不存在")
    if new_item.exists():
        raise HTTPException(status_code=409, detail="目标文件已存在")

    website_logger.info(
        f"{account} 重命名文件: {old_item} -> {new_item}", extra={"event": "管理操作"}
    )
    old_item.rename(new_item)
    rebuild_index_async()
    return {"new_path": str(new_item)}


@router.post("/file/move")
async def files_move(request: Request, account: str = Depends(cookie_account_get)):
    """移动文件"""
    if not account:
        return
    data = await request.json()
    src_path = data["src_path"]
    dst_path = data["dst_path"]
    src_item = UPLOAD_DIR / src_path
    dst_item = UPLOAD_DIR / dst_path

    shutil.move(str(src_item), str(dst_item))
    website_logger.info(
        f"{account} 移动文件: {str(src_item)} -> {str(dst_item)}",
        extra={"event": "管理操作"},
    )
    rebuild_index_async()
    return {"new_path": str(dst_item)}

def get_unique_pdf_name(doc_path):
    """获取唯一文件名（根据内容生成哈希)"""
    file_hash = hashlib.md5(doc_path.read_bytes()).hexdigest()[:8]
    base_name = doc_path.stem  # 不含后缀的文件名
    return f"{base_name}_{file_hash}.pdf"


@router.post("/file/preview")
async def files_preview(body: dict):
    """文件预览"""
    print(body)
    file_path = body["path"][0]
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        return {"error": "文件不存在"}

    # 支持类型
    mime_type, _ = mimetypes.guess_type(str(full_path))
    mime_type = mime_type or "application/octet-stream"

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
        pdf_filename = get_unique_pdf_name(full_path)
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
        print("PDF size:", pdf_path.stat().st_size)
        return FileResponse(
            str(pdf_path), media_type="application/pdf", filename=pdf_path.name
        )

    if mime_type == "application/vnd.ms-excel":
        xlsx_filename = get_unique_pdf_name(full_path)
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
    if mime_type.startswith("text/") or mime_type == "text/markdown":
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
async def files_stream_preview(request: Request, path: str):
    """视频流式预览"""
    full_path = UPLOAD_DIR / path
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

    file_size = os.path.getsize(full_path)
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
            "Content-Type": "video/mp4",  # 可根据后缀动态设置
            "Cache-Control": "public, max-age=3600",  # 加快浏览器重复加载
        },
    )


@router.get("/file/download/{path:path}")
async def download_file(path: str):
    """下载文件"""
    file_path = (UPLOAD_DIR / path).resolve()

    if not str(file_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=403, detail="非法路径")

    if file_path.is_file():
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream"
        )

    elif file_path.is_dir():
        folder_size = get_folder_size(file_path)
        if folder_size > 2 * 1024 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="文件夹总大小大于2GB，请单独下载内容"
            )
        tmp_dir = tempfile.gettempdir()
        zip_name = file_path.name + ".zip"
        zip_path = os.path.join(tmp_dir, zip_name)

        shutil.make_archive(base_name=os.path.join(tmp_dir, file_path.name),
                            format='zip',
                            root_dir=file_path)
        asyncio.create_task(remove_later(zip_path))

        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )


@router.get("/file/{path:path}")
async def files_get(path: str = ""):
    """访问文件夹目录"""
    if path == "none":
        path = ""
    base_path = UPLOAD_DIR / path

    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

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
    return {"items": items}


build_index(UPLOAD_DIR)
