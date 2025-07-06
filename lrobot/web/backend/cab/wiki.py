from fastapi import APIRouter,Query, HTTPException
from logic import get_wiki
from config import query_database


router = APIRouter()

# 获取页面索引（用于左侧导航）
@router.get("/wiki/index")
async def get_wiki_index():
    query = "SELECT id, title, group_name FROM system_wiki"
    result = await query_database(query)
    return result


# 获取单个页面内容
@router.get("/wiki/page")
async def get_wiki_page(id: int = Query(...)):
    query = "SELECT id, title, group_name FROM system_wiki WHERE id = %s"
    result = await query_database(query, (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Page not found")
    title = result[0]['title']
    content = await get_wiki(title)
    return { **result[0],"content":content}


@router.get("/wiki/search")
async def search_wiki(q: str = Query(...)):
    # 查找匹配的所有页面（标题或内容）
    query = """SELECT id, title, group_name FROM system_wiki"""
    all_pages = await query_database(query)

    matched = []
    group_names = set()

    for page in all_pages:
        title = page['title']
        group_name = page['group_name']
        content = await get_wiki(title)
        if q in content or q in title:
            matched.append({
                **page,
                "content": content
            })
            if group_name:
                group_names.add(group_name)

    parent_pages = []
    if group_names:
        placeholders = ','.join(['%s'] * len(group_names))
        parent_query = f"""
            SELECT id, title, group_name FROM system_wiki WHERE title IN ({placeholders})
        """
        parent_raw = await query_database(parent_query, tuple(group_names))
        for p in parent_raw:
            parent_content=await get_wiki(p)
            parent_pages.append({
                **p,
                "content": parent_content
            })

    all_combined = {p['id']: p for p in matched + parent_pages}

    return list(all_combined.values())
