import os
import shutil
import hashlib
import mimetypes
import subprocess
from typing import List
from pathlib import Path
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi import UploadFile, File, Request, HTTPException, APIRouter, Form
from config import path

router = APIRouter()
UPLOAD_DIR = path / "storage/file/resource/clouddrive"
RECYCLE_BIN = path / "storage/file/resource/recycle"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/files")
async def upload_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        dest = UPLOAD_DIR / file.filename
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(file.filename)
    return {"uploaded": saved_files}


@router.delete("/files")
async def delete_item(request: Request):
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

        return {"status": "success", "deleted_path": str(target_path)}

    except PermissionError:
        raise HTTPException(403, "没有删除权限")
    except Exception as e:
        raise HTTPException(500, f"删除操作失败: {str(e)}")


@router.post("/file_folders")
async def upload_folders(
    files: List[UploadFile] = File(...), paths: List[str] = Form(...)
):
    saved_files = []

    for file, relative_path in zip(files, paths):
        # 构造完整保存路径
        dest = UPLOAD_DIR / relative_path

        # 创建父目录
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        saved_files.append(str(relative_path))

    return {"uploaded": saved_files}


@router.post("/folders")
async def create_folder(request: Request):
    data = await request.json()
    path = data["path"].lstrip("/\\")
    print(path)
    full_path = UPLOAD_DIR / path
    full_path = full_path.resolve()
    # 防止路径跳出上传目录
    if not str(full_path).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")

    print(full_path)
    full_path.mkdir(parents=True, exist_ok=True)
    return {"path": str(full_path)}


@router.get("/browse/{path:path}")
async def browse_directory(path: str = ""):
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


@router.get("/search")
async def search_files(path: str, keyword: str):
    if path == "none":
        path = ""
    base_path = UPLOAD_DIR / path

    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    result = []
    for root, dirs, files in os.walk(base_path):
        for name in dirs + files:
            if keyword.lower() in name.lower():
                full_path = Path(root) / name
                result.append(
                    {
                        "name": name,
                        "path": str(full_path.relative_to(UPLOAD_DIR)).replace(
                            "\\", "/"
                        ),
                        "is_dir": full_path.is_dir(),
                        "modified": datetime.fromtimestamp(
                            full_path.stat().st_mtime
                        ).isoformat(),
                        "size": full_path.stat().st_size if full_path.is_file() else 0,
                    }
                )

    return {"items": result}


@router.put("/rename")
async def rename_item(request: Request):
    data = await request.json()
    old_path = data["old_path"]
    new_path = data["new_path"]
    old_item = UPLOAD_DIR / old_path
    new_item = UPLOAD_DIR / new_path
    print(old_item)
    print(new_item)
    old_item.rename(new_item)
    return {"new_path": str(new_item)}


@router.post("/move")
async def move_item(request: Request):
    data = await request.json()
    src_path = data["src_path"]
    dst_path = data["dst_path"]
    src_item = UPLOAD_DIR / src_path
    dst_item = UPLOAD_DIR / dst_path
    print(src_item)
    print(dst_item)
    shutil.move(str(src_item), str(dst_item))
    return {"new_path": str(dst_item)}


# 获取唯一文件名（hash 或时间戳）：
def get_unique_pdf_name(doc_path):
    # 方式一：根据文件内容生成哈希（不重复且对内容敏感）
    file_hash = hashlib.md5(doc_path.read_bytes()).hexdigest()[:8]
    base_name = doc_path.stem  # 不含后缀的文件名
    return f"{base_name}_{file_hash}.pdf"


@router.post("/preview")
async def preview_file(body: dict):
    file_path = body["path"][0]
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        return {"error": "文件不存在"}

    # 支持类型
    mime_type, _ = mimetypes.guess_type(str(full_path))
    mime_type = mime_type or "application/octet-stream"

    if full_path.suffix == ".md":
        mime_type = "text/markdown"

    # Word / Excel / PPT 转 PDF
    if mime_type in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]:
        pdf_filename = get_unique_pdf_name(full_path)
        pdf_path = RECYCLE_BIN / pdf_filename
        print(pdf_path)

        if not pdf_path.exists():
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    str(full_path),
                    "--outdir",
                    str(RECYCLE_BIN),
                ],
                check=True,
            )
        generated_pdf = RECYCLE_BIN / full_path.with_suffix(".pdf").name
        if generated_pdf.exists():
            generated_pdf.rename(pdf_path)
        return FileResponse(
            str(pdf_path), media_type="application/pdf", filename=pdf_path.name
        )

    return FileResponse(str(full_path), media_type=mime_type, filename=full_path.name)
