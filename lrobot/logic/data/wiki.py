from config import path

async def get_wiki(title):
    file_path = path / f"storage/file/wiki/{title}.md"
    if not file_path.exists():
        raise Exception(f"Markdown file for '{title}' not found")
    content = file_path.read_text(encoding="utf-8")
    return content

async def set_wiki(title, content):
    file_path = path / f"storage/file/wiki/{title}_change.md"
    file_path.write_text(content, encoding="utf-8")