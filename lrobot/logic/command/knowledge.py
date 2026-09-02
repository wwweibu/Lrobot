"""LR5921 内阁知识助手命令。"""

import asyncio
import time
import uuid
import zipfile

from config import loggers, monitor_adapter, path
from logic import data
from message.handler.msg import Msg


DRIVE_ROOT = (path / "storage/file/clouddrive").resolve()
EXPORT_ROOT = (path / "storage/file/knowledge_exports").resolve()
MAX_BUNDLE_BYTES = 80 * 1024 * 1024


def _send(msg: Msg, content) -> None:
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


def _send_file(msg: Msg, file_path) -> None:
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}文件上传",
        seq=msg.seq,
        content=f"[文件:{file_path}]",
        user=msg.user,
        group=msg.group,
    )


def _build_attachment_bundle(file_paths) -> tuple:
    """将多份网盘资料打成一个可正常下载的 ZIP，避免伪造转发产生 0B 文件。"""
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for old_file in EXPORT_ROOT.glob("LRobot知识资料-*.zip"):
        try:
            if now - old_file.stat().st_mtime > 24 * 60 * 60:
                old_file.unlink()
        except OSError:
            pass

    archive_path = EXPORT_ROOT / (
        f"LRobot知识资料-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}.zip"
    )
    added = 0
    total_size = 0
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for file_path in file_paths:
            full_path = file_path.resolve()
            if not full_path.is_relative_to(DRIVE_ROOT) or not full_path.is_file():
                continue
            size = full_path.stat().st_size
            if added and total_size + size > MAX_BUNDLE_BYTES:
                break
            archive.write(full_path, full_path.relative_to(DRIVE_ROOT).as_posix())
            total_size += size
            added += 1
    if not added:
        archive_path.unlink(missing_ok=True)
        raise ValueError("没有可打包的附件")
    return archive_path, added


async def knowledge_ask_judge(msg: Msg) -> bool:
    """匹配 `/问 问题`，以及内阁私聊中的明确文件请求。"""
    text = Msg.content_join(msg.content).strip()
    if text.startswith("/问 "):
        return bool(text[3:].strip())
    return (
        msg.kind.startswith("私聊")
        and "文件" in text
        and any(word in text for word in ("发送", "发一下", "给我", "下载"))
    )


@monitor_adapter("/知识_问")
async def knowledge_ask(msg: Msg):
    """检索内阁 Wiki 和网盘，并按需发送命中文件。"""
    if msg.platform != "LR5921" or not msg.kind.endswith("接收"):
        return
    text = Msg.content_join(msg.content).strip()
    question = text[3:].strip() if text.startswith("/问 ") else text
    if len(question) > 1000:
        _send(msg, "问题太长了，请压缩到 1000 字以内。")
        return

    _send(msg, "正在检索内阁 Wiki 和网盘，请稍候……")
    try:
        result = await data.knowledge_answer(question)
        content = result["answer"]
        if result["sources"]:
            content += "\n\n来源：\n" + "\n".join(f"- {source}" for source in result["sources"])
        _send(msg, content)

        attachment_paths = []
        for relative_path in result["attachments"]:
            full_path = (path / "storage/file/clouddrive" / relative_path).resolve()
            if not full_path.is_relative_to(DRIVE_ROOT) or not full_path.is_file():
                continue
            attachment_paths.append(full_path)
        if len(attachment_paths) > 1:
            try:
                bundle_path, _ = await asyncio.to_thread(_build_attachment_bundle, attachment_paths)
                _send_file(msg, bundle_path)
            except (OSError, ValueError, zipfile.BadZipFile):
                for full_path in attachment_paths:
                    _send_file(msg, full_path)
        elif attachment_paths:
            _send_file(msg, attachment_paths[0])
        return content
    except Exception as error:
        logger = loggers.get("system")
        if logger:
            logger.error(
                f"[知识助手]调用失败: {type(error).__name__}",
                extra={"event": "知识助手"},
            )
        content = "知识助手暂时不可用，请稍后再试。"
        _send(msg, content)
        return content
