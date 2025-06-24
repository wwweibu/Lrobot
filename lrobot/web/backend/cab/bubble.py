from fastapi import APIRouter, HTTPException,Request
from config import update_database,query_database

router = APIRouter()

@router.post("/bubbles")
async def upsert_bubble(request: Request):
    data = await request.json()
    bubble_id = data.get('id')
    content = data.get('content')
    x = data.get('x')
    y = data.get('y')

    if not content or x is None or y is None:
        return {"status": "error", "message": "Missing content, x, or y"}

    if bubble_id:  # 修改或移动
        query = "UPDATE system_bubble SET content = %s, x = %s, y = %s WHERE id = %s"
        await update_database(query, (content, x, y, bubble_id))
        return {"status": "updated"}
    else:  # 创建新泡泡
        query = "INSERT INTO system_bubble (content, x, y) VALUES (%s, %s, %s)"
        result = await update_database(query, (content, x, y))
        return {"status": "inserted", "id": result}

@router.post("/bubbles/delete")
async def delete_bubble(request: Request):
    data = await request.json()
    bubble_id = data.get('id')
    if not bubble_id:
        return {"status": "error", "message": "Missing id"}
    query = "DELETE FROM system_bubble WHERE id = %s"
    await update_database(query, (bubble_id,))
    return {"status": "deleted"}

@router.get("/bubbles")
async def get_bubbles():
    query = "SELECT id, content, x, y FROM system_bubble ORDER BY id ASC"
    return await query_database(query)