"""内阁知识助手的只读检索、文件解析和 Codex 工具循环。"""

import asyncio
import hashlib
import html
import json
import re
import subprocess
import tempfile
import time
import uuid
import zipfile
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree

import chardet
import httpx
import jieba
import openpyxl
import xlrd

from config import config, database_query, loggers, path


DRIVE_ROOT = path / "storage/file/clouddrive"
TOKEN_PATH = path / "storage/yml/knowledge_api_token"
DEFAULT_BRIDGE_URL = "http://172.18.0.1:10003"
MAX_FILE_SIZE = 50 * 1024 * 1024
MAX_EXTRACTED_CHARS = 200_000
MAX_READ_CHARS = 30_000
INDEX_TTL_SECONDS = 300
TEXT_SUFFIXES = {
    ".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".html", ".htm",
    ".xml", ".ini", ".log", ".data", ".dat",
}
LEGACY_OFFICE_SUFFIXES = {".doc", ".ppt", ".rtf", ".wps"}
STOP_WORDS = {
    "什么", "是什么", "怎么", "如何", "请问", "一下", "相关", "文件", "资料",
    "帮我", "可以", "有没有", "介绍", "发送", "给我",
}
FILE_REQUEST_NOUNS = ("文件", "附件", "文档", "资料", "策划书", "活动总结", "题目", "规则")
FILE_REQUEST_ACTIONS = ("发", "发送", "给我", "下载", "提供")
PREFERRED_FILE_SUFFIXES = {".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx", ".txt"}

_drive_index = []
_drive_index_built_at = 0.0
_drive_index_lock = asyncio.Lock()
_http_client = None
_http_client_lock = asyncio.Lock()


def _normalize(value: str) -> str:
    return re.sub(r"[^0-9a-z\u3400-\u9fff]+", "", str(value).casefold())


def _query_terms(query: str) -> list[str]:
    normalized = _normalize(query)
    terms = []
    if normalized:
        terms.append(normalized)
    for item in jieba.lcut(query):
        term = _normalize(item)
        if len(term) >= 2 and term not in STOP_WORDS and term not in terms:
            terms.append(term)
    return terms[:12]


def _score(query: str, title: str, group: str = "", content: str = "") -> int:
    terms = _query_terms(query)
    title_text = _normalize(title)
    group_text = _normalize(group)
    content_text = _normalize(content)
    score = 0
    for index, term in enumerate(terms):
        weight = 4 if index == 0 else 1
        if term in title_text:
            score += 80 * weight
        if term in group_text:
            score += 30 * weight
        if term in content_text:
            score += 8 * weight
    return score


def _plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _snippet(content: str, query: str, length: int = 500) -> str:
    content = _plain_text(content)
    normalized_terms = [term for term in _query_terms(query) if len(term) >= 2]
    lower = content.casefold()
    positions = [lower.find(term.casefold()) for term in normalized_terms]
    positions = [position for position in positions if position >= 0]
    start = max(0, (min(positions) if positions else 0) - 100)
    return content[start:start + length]


async def knowledge_search_wiki(query: str, limit: int = 8) -> list[dict]:
    """按标题、分组和正文搜索 Wiki。"""
    rows = await database_query(
        "SELECT id, title, group_name, content FROM system_wiki ORDER BY sort"
    )
    results = []
    for row in rows:
        score = _score(query, row.get("title", ""), row.get("group_name", ""), row.get("content", ""))
        if score:
            results.append({
                "id": f"wiki:{row['id']}",
                "title": row.get("title") or "",
                "group": row.get("group_name") or "",
                "snippet": _snippet(row.get("content") or "", query),
                "score": score,
            })
    results.sort(key=lambda item: (-item["score"], item["title"]))
    return results[:max(1, min(limit, 12))]


async def knowledge_read_wiki(wiki_id: str) -> dict:
    """读取一个已经通过搜索得到的 Wiki 页面。"""
    raw_id = str(wiki_id).removeprefix("wiki:")
    if not raw_id.isdigit():
        raise ValueError("Wiki id 非法")
    rows = await database_query(
        "SELECT id, title, group_name, content FROM system_wiki WHERE id = %s LIMIT 1",
        (int(raw_id),),
    )
    if not rows:
        raise FileNotFoundError("Wiki 页面不存在")
    row = rows[0]
    return {
        "id": f"wiki:{row['id']}",
        "title": row.get("title") or "",
        "group": row.get("group_name") or "",
        "content": _plain_text(row.get("content") or "")[:MAX_EXTRACTED_CHARS],
    }


def _file_id(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:20]
    return f"file:{digest}"


def _build_drive_index() -> list[dict]:
    items = []
    for full_path in DRIVE_ROOT.rglob("*"):
        if not full_path.is_file():
            continue
        try:
            stat = full_path.stat()
            relative = full_path.relative_to(DRIVE_ROOT).as_posix()
        except (FileNotFoundError, OSError, ValueError):
            continue
        items.append({
            "id": _file_id(relative),
            "name": full_path.name,
            "path": relative,
            "suffix": full_path.suffix.lower(),
            "size": stat.st_size,
            "modified": stat.st_mtime,
        })
    return items


async def _get_drive_index() -> list[dict]:
    global _drive_index, _drive_index_built_at
    if _drive_index and time.monotonic() - _drive_index_built_at < INDEX_TTL_SECONDS:
        return _drive_index
    async with _drive_index_lock:
        if not _drive_index or time.monotonic() - _drive_index_built_at >= INDEX_TTL_SECONDS:
            _drive_index = await asyncio.to_thread(_build_drive_index)
            _drive_index_built_at = time.monotonic()
    return _drive_index


async def knowledge_search_drive(query: str, limit: int = 12) -> list[dict]:
    """搜索网盘文件名与相对路径。"""
    results = []
    for item in await _get_drive_index():
        score = _score(query, item["name"], item["path"])
        if score:
            results.append({**item, "score": score})
    results.sort(key=lambda item: (-item["score"], item["path"]))

    # 同一活动目录往往有几十到上百张图片。先保证不同活动目录都有机会
    # 出现在结果里，再用同目录的其余文件补足，避免结果永远停在最早年份。
    diverse = []
    remainder = []
    seen_buckets = set()
    for item in results:
        parts = item["path"].split("/")
        bucket = "/".join(parts[:2]) if len(parts) >= 2 else item["path"]
        if bucket in seen_buckets:
            remainder.append(item)
            continue
        seen_buckets.add(bucket)
        diverse.append(item)
    diverse.extend(remainder)
    return diverse[:max(1, min(limit, 100))]


def _is_file_request(question: str) -> bool:
    text = str(question)
    return (
        any(word in text for word in FILE_REQUEST_ACTIONS)
        and any(word in text for word in FILE_REQUEST_NOUNS)
    )


def _file_search_query(question: str) -> str:
    """从自然语言文件请求中提取适合文件名搜索的关键词。"""
    text = re.sub(r"^\s*/问\s*", "", str(question)).strip()
    for word in (*FILE_REQUEST_ACTIONS, *FILE_REQUEST_NOUNS, "一下", "相关", "一些", "全部", "所有", "的"):
        text = text.replace(word, " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or str(question)


def _representative_files(results: list[dict], max_files: int = 10) -> list[dict]:
    """优先为每个本协会活动年份选择一份可读的代表文件。"""
    usable = [
        item for item in results
        if item["size"] <= MAX_FILE_SIZE and item["suffix"] in PREFERRED_FILE_SUFFIXES
    ]
    selected = []
    selected_paths = set()
    by_year = {}
    for item in usable:
        match = re.match(r"^活动/(20\d{2})[^/]*(?:校园)?寻宝(?:/|$)", item["path"])
        if match and match.group(1) not in by_year:
            by_year[match.group(1)] = item
    for year in sorted(by_year):
        item = by_year[year]
        selected.append(item)
        selected_paths.add(item["path"])
        if len(selected) >= max_files:
            return selected

    seen_buckets = {"/".join(item["path"].split("/")[:2]) for item in selected}
    for item in usable:
        if item["path"] in selected_paths:
            continue
        bucket = "/".join(item["path"].split("/")[:2])
        if bucket in seen_buckets:
            continue
        selected.append(item)
        selected_paths.add(item["path"])
        seen_buckets.add(bucket)
        if len(selected) >= max_files:
            break
    return selected


async def _deterministic_file_answer(question: str) -> dict | None:
    """文件发送不依赖模型临场选择工具，确保网盘检索稳定且覆盖年份。"""
    query = _file_search_query(question)
    results = await knowledge_search_drive(query, limit=100)
    requested_year = re.search(r"20\d{2}", question)
    if requested_year:
        year = requested_year.group(0)
        subject_terms = [
            term for term in _query_terms(query)
            if term != "年" and year not in term and not term.isdigit()
        ]
        requested_types = [
            keyword for keyword in ("策划", "题目", "总结", "规则", "手册", "答案", "地图")
            if keyword in question
        ]
        candidates = [
            item for item in results
            if year in item["path"]
            and item["size"] <= MAX_FILE_SIZE
            and item["suffix"] in PREFERRED_FILE_SUFFIXES
            and (not subject_terms or any(term in _normalize(item["path"]) for term in subject_terms))
        ]
        annual = [
            item for item in candidates
            if re.match(rf"^活动/{year}[^/]*(?:校园)?寻宝(?:/|$)", item["path"])
        ]
        if annual:
            candidates = annual
        selected = [
            item for item in candidates
            if not requested_types or any(keyword in item["path"] for keyword in requested_types)
        ][:10]
    else:
        selected = _representative_files(results)
    if not selected:
        if requested_year:
            return {
                "answer": (
                    f"没有找到同时符合 {requested_year.group(0)} 年及指定文件类型的资料。"
                    "可以去掉文件类型后重试。"
                ),
                "sources": [],
                "attachments": [],
            }
        return None
    years = []
    for item in selected:
        match = re.match(r"^活动/(20\d{2})", item["path"])
        if match and match.group(1) not in years:
            years.append(match.group(1))
    coverage = "、".join(years) if years else "多个活动目录"
    if requested_year:
        answer = (
            f"已选出 {len(selected)} 份 {requested_year.group(0)} 年的相关资料，并打包为一个 ZIP 发送。"
            "单次最多发送 10 份；如需进一步筛选，可指定“策划书”“题目”或“活动总结”。"
        )
    else:
        answer = (
            f"网盘中匹配到至少 {len(results)} 个候选文件；已按活动目录去重，"
            f"选出 {len(selected)} 份代表资料并打包为一个 ZIP 发送，覆盖 {coverage}。"
            "为避免同一年几十张图片刷屏，每年先发一份；如需某一年的更多资料，"
            "可以继续指定年份和文件类型。"
        )
    paths = [item["path"] for item in selected]
    return {
        "answer": answer,
        "sources": [f"网盘：{relative_path}" for relative_path in paths],
        "attachments": paths,
    }


def _resolve_drive_path(relative_path: str) -> Path:
    candidate = (DRIVE_ROOT / relative_path).resolve()
    root = DRIVE_ROOT.resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise FileNotFoundError("网盘文件不存在或路径非法")
    if candidate.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("文件超过 50 MiB，不能直接解析")
    return candidate


def _decode_text(raw: bytes) -> str:
    encoding = chardet.detect(raw[:200_000]).get("encoding") or "utf-8"
    try:
        return raw.decode(encoding)
    except (LookupError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


def _zip_xml_text(file_path: Path, prefixes: tuple[str, ...]) -> str:
    parts = []
    with zipfile.ZipFile(file_path) as archive:
        names = sorted(name for name in archive.namelist() if name.startswith(prefixes) and name.endswith(".xml"))
        for name in names:
            root = ElementTree.fromstring(archive.read(name))
            for element in root.iter():
                if element.tag.rsplit("}", 1)[-1] == "t" and element.text:
                    parts.append(element.text)
                    if sum(map(len, parts)) >= MAX_EXTRACTED_CHARS:
                        return "\n".join(parts)[:MAX_EXTRACTED_CHARS]
    return "\n".join(parts)


def _spreadsheet_text(file_path: Path) -> str:
    lines = []
    if file_path.suffix.lower() == ".xlsx":
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        try:
            for sheet in workbook.worksheets:
                lines.append(f"[{sheet.title}]")
                for row in sheet.iter_rows(values_only=True):
                    values = [str(value) for value in row if value is not None]
                    if values:
                        lines.append("\t".join(values))
                    if sum(map(len, lines)) >= MAX_EXTRACTED_CHARS:
                        break
        finally:
            workbook.close()
    else:
        workbook = xlrd.open_workbook(file_path, on_demand=True)
        try:
            for sheet in workbook.sheets():
                lines.append(f"[{sheet.name}]")
                for row_index in range(sheet.nrows):
                    values = [str(value) for value in sheet.row_values(row_index) if value not in (None, "")]
                    if values:
                        lines.append("\t".join(values))
                    if sum(map(len, lines)) >= MAX_EXTRACTED_CHARS:
                        break
        finally:
            workbook.release_resources()
    return "\n".join(lines)[:MAX_EXTRACTED_CHARS]


def _legacy_office_text(file_path: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="lrobot-knowledge-") as temp_dir:
        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", "txt:Text", "--outdir", temp_dir, str(file_path)],
            check=False,
            capture_output=True,
            timeout=60,
        )
        output_path = Path(temp_dir) / f"{file_path.stem}.txt"
        if result.returncode != 0 or not output_path.exists():
            raise ValueError("旧 Office 文件转换失败")
        return _decode_text(output_path.read_bytes())[:MAX_EXTRACTED_CHARS]


@lru_cache(maxsize=8)
def _extract_cached(file_name: str, modified_ns: int, size: int) -> str:
    del modified_ns, size
    file_path = Path(file_name)
    suffix = file_path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        text = _decode_text(file_path.read_bytes())
    elif suffix == ".docx":
        text = _zip_xml_text(file_path, ("word/",))
    elif suffix == ".pptx":
        text = _zip_xml_text(file_path, ("ppt/slides/",))
    elif suffix in {".xlsx", ".xls"}:
        text = _spreadsheet_text(file_path)
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise ValueError("PDF 解析组件未安装") from error
        parts = []
        for page in PdfReader(file_path).pages:
            parts.append(page.extract_text() or "")
            if sum(map(len, parts)) >= MAX_EXTRACTED_CHARS:
                break
        text = "\n".join(parts)
    elif suffix in LEGACY_OFFICE_SUFFIXES:
        text = _legacy_office_text(file_path)
    else:
        raise ValueError(f"暂不支持解析 {suffix or '无扩展名'} 文件")
    return re.sub(r"\n{3,}", "\n\n", text).strip()[:MAX_EXTRACTED_CHARS]


async def knowledge_read_drive(relative_path: str, offset: int = 0) -> dict:
    """读取网盘文件的一个受限文本片段。"""
    file_path = _resolve_drive_path(relative_path)
    stat = file_path.stat()
    text = await asyncio.to_thread(_extract_cached, str(file_path), stat.st_mtime_ns, stat.st_size)
    offset = max(0, min(int(offset), len(text)))
    return {
        "path": relative_path,
        "offset": offset,
        "total_chars": len(text),
        "content": text[offset:offset + MAX_READ_CHARS],
    }


async def _client() -> httpx.AsyncClient:
    global _http_client
    async with _http_client_lock:
        if _http_client is None:
            _http_client = httpx.AsyncClient(timeout=130)
    return _http_client


def _bridge_url() -> str:
    bridge_config = config["knowledge_llm"]
    return bridge_config.get("bridge_url", DEFAULT_BRIDGE_URL).rstrip("/")


def _bridge_token() -> str:
    token = TOKEN_PATH.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError("知识助手令牌为空")
    return token


async def _bridge_call(endpoint: str, payload: dict) -> dict:
    response = await (await _client()).post(
        f"{_bridge_url()}{endpoint}",
        json=payload,
        headers={"Authorization": f"Bearer {_bridge_token()}"},
    )
    response.raise_for_status()
    return response.json()


async def knowledge_answer(question: str) -> dict:
    """驱动 Codex 的结构化工具循环并返回答案、来源和附件路径。"""
    if _is_file_request(question):
        deterministic = await _deterministic_file_answer(question)
        if deterministic:
            return deterministic

    request_id = uuid.uuid4().hex
    allowed_wikis = {}
    allowed_files = {}
    allowed_sources = {}
    tool_calls = 0
    wants_file = _is_file_request(question)
    try:
        wiki_results, drive_results = await asyncio.gather(
            knowledge_search_wiki(question),
            knowledge_search_drive(question),
        )
        for item in wiki_results:
            allowed_wikis[item["id"]] = item["id"]
            source = f"Wiki：{item['title']}"
            allowed_sources[item["title"]] = source
            allowed_sources[source] = source
        for item in drive_results:
            allowed_files[item["id"]] = item["path"]
            source = f"网盘：{item['path']}"
            allowed_sources[item["path"]] = source
            allowed_sources[source] = source
        if wiki_results or drive_results:
            tool_calls = 1
        payload = await _bridge_call("/v1/start", {
            "request_id": request_id,
            "question": question,
            "initial_context": {
                "wiki_results": wiki_results,
                "drive_results": drive_results,
            },
        })
        action = payload.get("action", {})
        for _ in range(8):
            action_name = action.get("action")
            if action_name == "search_wiki":
                query = str(action.get("query") or question)[:500]
                results = await knowledge_search_wiki(query)
                for item in results:
                    allowed_wikis[item["id"]] = item["id"]
                    source = f"Wiki：{item['title']}"
                    allowed_sources[item["title"]] = source
                    allowed_sources[source] = source
                tool_result = {"tool": action_name, "query": query, "results": results}
            elif action_name == "read_wiki":
                wiki_id = str(action.get("id") or "")
                if wiki_id not in allowed_wikis:
                    tool_result = {"tool": action_name, "error": "必须先搜索并使用返回的 Wiki id"}
                else:
                    item = await knowledge_read_wiki(wiki_id)
                    source = f"Wiki：{item['title']}"
                    allowed_sources[item["title"]] = source
                    allowed_sources[source] = source
                    tool_result = {"tool": action_name, "result": item}
            elif action_name == "search_drive":
                query = str(action.get("query") or question)[:500]
                results = await knowledge_search_drive(query)
                for item in results:
                    allowed_files[item["id"]] = item["path"]
                    source = f"网盘：{item['path']}"
                    allowed_sources[item["path"]] = source
                    allowed_sources[source] = source
                tool_result = {"tool": action_name, "query": query, "results": results}
            elif action_name == "read_file":
                file_id = str(action.get("id") or "")
                relative_path = allowed_files.get(file_id)
                if not relative_path:
                    tool_result = {"tool": action_name, "error": "必须先搜索并使用返回的 file id"}
                else:
                    try:
                        item = await knowledge_read_drive(relative_path)
                        source = f"网盘：{relative_path}"
                        allowed_sources[relative_path] = source
                        allowed_sources[source] = source
                        tool_result = {"tool": action_name, "id": file_id, "result": item}
                    except (ValueError, FileNotFoundError, OSError, zipfile.BadZipFile) as error:
                        tool_result = {"tool": action_name, "id": file_id, "error": str(error)}
            elif action_name == "final":
                if tool_calls == 0:
                    tool_result = {"tool": "validation", "error": "回答前必须至少搜索一次 Wiki 或网盘"}
                else:
                    answer = str(action.get("answer") or "").strip()
                    if not answer:
                        raise ValueError("知识助手返回了空答案")
                    sources = list(dict.fromkeys(
                        allowed_sources[source]
                        for source in action.get("sources", [])
                        if source in allowed_sources
                    ))
                    attachment_ids = action.get("attachments", []) if wants_file else []
                    attachments = [allowed_files[file_id] for file_id in attachment_ids if file_id in allowed_files][:3]
                    return {"answer": answer[:4000], "sources": sources[:10], "attachments": attachments}
            else:
                tool_result = {"tool": "validation", "error": "未知工具请求"}

            tool_calls += 1
            payload = await _bridge_call(
                "/v1/continue",
                {"request_id": request_id, "tool_result": tool_result},
            )
            action = payload.get("action", {})
        raise TimeoutError("知识助手检索步骤过多")
    finally:
        try:
            await _bridge_call("/v1/end", {"request_id": request_id})
        except Exception:
            pass


async def knowledge_health() -> bool:
    """检查宿主机知识桥接健康状态。"""
    try:
        response = await (await _client()).get(f"{_bridge_url()}/health", timeout=5)
        return response.status_code == 200 and response.json().get("ok") is True
    except Exception:
        return False
