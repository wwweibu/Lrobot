"""wiki 页面"""

from fastapi import APIRouter, Query, HTTPException
from logic import wiki_get
from config import database_query


router = APIRouter()


@router.get("/wiki/index")
async def wiki_index_get():
    """获取页面索引（用于左侧导航）"""
    query = "SELECT id, title, group_name FROM system_wiki"
    result = await database_query(query)
    return result


@router.get("/wiki/page")
async def wiki_page_get(id: int = Query(...)):
    """获取单个页面内容"""
    query = "SELECT id, title, group_name FROM system_wiki WHERE id = %s"
    result = await database_query(query, (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Page not found")
    title = result[0]["title"]
    content = await wiki_get(title)
    return {**result[0], "content": content}


@router.get("/wiki/search")
async def wiki_search(q: str = Query(...)):
    """查找匹配的所有页面（标题或内容）"""
    query = """SELECT id, title, group_name FROM system_wiki"""
    all_pages = await database_query(query)

    matched = []
    group_names = set()

    for page in all_pages:
        title = page["title"]
        group_name = page["group_name"]
        content = await wiki_get(title)
        if q in content or q in title:
            matched.append({**page, "content": content})
            if group_name:
                group_names.add(group_name)

    parent_pages = []
    if group_names:
        placeholders = ",".join(["%s"] * len(group_names))
        parent_query = f"""
            SELECT id, title, group_name FROM system_wiki WHERE title IN ({placeholders})
        """
        parent_raw = await database_query(parent_query, tuple(group_names))
        for p in parent_raw:
            parent_content = await wiki_get(p)
            parent_pages.append({**p, "content": parent_content})

    all_combined = {p["id"]: p for p in matched + parent_pages}

    return list(all_combined.values())
