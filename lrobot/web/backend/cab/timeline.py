from datetime import datetime, date
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# 临时数据库
nodes_db = []
next_id = 1

# 数据模型
class TimeNode(BaseModel):
    id: int
    date: date  # 改为 date 类型
    event: str
    tag: Optional[str] = "里程碑"  # 添加 tag 字段

class TimeNodeCreate(BaseModel):
    date: date  # 改为 date 类型
    event: str
    tag: Optional[str] = "里程碑"  # 添加 tag 字段

@router.get("/nodes", response_model=List[TimeNode])
def get_nodes():
    # 确保返回的数据是 TimeNode 格式
    return [TimeNode(**node) for node in nodes_db]

@router.post("/nodes", response_model=TimeNode)
def create_node(node: TimeNodeCreate):
    global next_id
    # 创建新节点时使用 date 字段
    new_node = TimeNode(
        id=next_id,
        date=node.date,
        event=node.event,
        tag=node.tag
    )
    nodes_db.append(new_node.dict())
    next_id += 1
    return new_node

@router.put("/nodes/{node_id}", response_model=TimeNode)
def update_node(node_id: int, node: TimeNodeCreate):
    for idx, n in enumerate(nodes_db):
        if n["id"] == node_id:
            # 更新时使用 date 字段
            updated_node = TimeNode(
                id=node_id,
                date=node.date,
                event=node.event,
                tag=node.tag
            )
            nodes_db[idx] = updated_node.dict()
            return updated_node
    raise HTTPException(status_code=404, detail="Node not found")

@router.delete("/nodes/{node_id}")
def delete_node(node_id: int):
    global nodes_db
    initial_length = len(nodes_db)
    nodes_db = [n for n in nodes_db if n["id"] != node_id]
    if len(nodes_db) == initial_length:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted"}