"""wiki 相关"""

from config import path


async def wiki_get(title):
    """获取 wiki 内容"""
    file_path = path / f"storage/file/wiki/{title}.md"
    if not file_path.exists():
        raise Exception(f"Markdown file for '{title}' not found")
    content = file_path.read_text(encoding="utf-8")
    return content


async def wiki_set(title, content):
    """更新 wiki 内容"""
    file_path = path / f"storage/file/wiki/{title}_change.md"
    file_path.write_text(content, encoding="utf-8")
