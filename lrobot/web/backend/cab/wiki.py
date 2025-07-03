from fastapi import APIRouter,Query, HTTPException
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
    query = "SELECT id, title, group_name, content FROM system_wiki WHERE id = %s"
    result = await query_database(query, (id,))
    if not result:
        raise HTTPException(status_code=404, detail="Page not found")
    return result[0]


@router.get("/wiki/search")
async def search_wiki(q: str = Query(...)):
    # 查找匹配的所有页面（标题或内容）
    keyword = f"%{q}%"
    search_sql = """
        SELECT id, title, group_name, content
        FROM system_wiki
        WHERE title LIKE %s OR content LIKE %s
    """
    matched = await query_database(search_sql, (keyword, keyword))

    # 获取需要补全的 group_name 列表（需要显示的父页面）
    group_names = set(p['group_name'] for p in matched if p['group_name'])
    parent_pages = []

    if group_names:
        placeholders = ','.join(['%s'] * len(group_names))
        parent_sql = f"""
            SELECT id, title, group_name, content
            FROM system_wiki
            WHERE title IN ({placeholders})
        """
        params = tuple(group_names)
        parent_pages = await query_database(parent_sql, params)

    # 合并并去重
    print(1234)
    print(matched)
    print(parent_pages)
    all_pages = {p['id']: p for p in list(matched) + parent_pages}

    print(all_pages)
    return list(all_pages.values())
