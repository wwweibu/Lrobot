"""消息记录器"""

import re
import json
from datetime import datetime

from logic import data
from message.handler.msg import Msg
from config import path, temp_key, monitor_adapter, storage, config

recording_groups = storage.setdefault("recording_groups", {})
record_path = path / f"storage/file/command/record"
record_path.mkdir(parents=True, exist_ok=True)
name_pool = ["阿富汗医生", "比利时的灰脑袋", "犯罪界的拿破仑", "洗衣机", "七次退休的养蜂人", "八卦老太太",
             "天才物理学家", "神父", "修道院的僧侣", "独眼警长", "妖怪博士", "杀人建筑师",
             "时刻表警部", "会占卜的猫", "从不出门的胖子", "上海滩神探", "包打听", "37岁高中生",
             "千面女巫", "红约翰追踪者", "时空对讲机"]


@monitor_adapter("/基础_记录_开始")
async def record_add(msg: Msg):
    """开始记录指定群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) < 2:
        content = "格式错误，请使用 /记录,水群/玩耍地"
    else:
        group = parts[1].strip()
        if group not in config["public"]:
            content = "格式错误，请使用 /记录,水群/玩耍地"
        else:
            group_id = config["public"][group][0]

            file_path = record_path / f"{group_id}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
            else:
                data_json = []
            new_id = max((r["id"] for r in data_json), default=0) + 1

            new_record = {
                "id": new_id,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "messages": []
            }
            data_json.append(new_record)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_json, f, ensure_ascii=False, indent=2)
            recording_groups[group_id] = new_id
            content = f"开始记录 {group} 的消息(记录ID: {new_id})"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group
    )
    return content


@monitor_adapter("/基础_记录_结束")
async def record_delete(msg: Msg):
    """结束记录指定群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) < 2:
        content = "格式错误，请使用'/结束记录,水群/玩耍地'"
    else:
        group = parts[1].strip()
        if group not in config["public"]:
            content = "格式错误，请使用'/结束记录,水群/玩耍地'"
        else:
            group_id = config["public"][group][0]
            if group_id not in recording_groups:
                content = f"{group} 当前未在记录中"
            else:
                file_path = record_path / f"{group_id}.json"
                record_id = recording_groups[group_id]
                with open(file_path, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                for r in data_json:
                    if r["id"] == record_id:
                        r["end_time"] = datetime.now().isoformat()
                        break
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_json, f, ensure_ascii=False, indent=2)
                del recording_groups[group_id]
                content = f"已结束记录 {group} 的消息(记录ID: {record_id})"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group
    )
    return content


async def record_write(msg: Msg):
    """记录消息"""
    if msg.platform != "LR5921":
        return
    group_id = str(msg.group)
    if group_id not in recording_groups:
        return
    record_id = recording_groups[group_id]
    file_path = record_path / f"{group_id}.json"
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data_json = json.load(f)
    current_record = next((r for r in data_json if r["id"] == record_id), None)
    if not current_record:
        return
    if msg.event == "发送":
        user = config["LR5921_ID"]
        name = "LR5921"
    else:
        user = msg.user
        name = await data.user_name(user, "LR5921")
    message_entry = {
        "seq": msg.seq,
        "user": user,
        "name": name,
        "content": Msg.content_join(msg.content),
        "time": datetime.now().isoformat()
    }
    current_record["messages"].append(message_entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=2)


@monitor_adapter("/基础_记录_导出")
async def record_export(msg: Msg):
    """记录导出"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content))
    if len(parts) == 1:
        summary = []
        for record_file in record_path.glob("*.json"):
            group_id = record_file.stem
            group_name = next((name for name, group_list in config["public"].items() if group_list[0] == group_id),
                              group_id)
            with open(record_file, "r", encoding="utf-8") as f:
                data_json = json.load(f)
            for r in data_json:
                start = datetime.fromisoformat(r.get("start_time", "1970-01-01T00:00:00")).strftime("%m-%d %H:%M")
                end_time = r.get("end_time")
                if end_time:
                    end = datetime.fromisoformat(end_time).strftime("%m-%d %H:%M")
                else:
                    end = "进行中"
                summary.append(f"{group_name}: {r['id']}->{start}: {end}")
        content = "\n".join(summary) if summary else "暂无任何记录。"
    elif len(parts) >= 3:
        group = parts[1].strip()
        if group not in config["public"]:
            content = "格式错误，请使用 /记录导出,水群/玩耍地,id"
        else:
            group_id = config["public"][group][0]
            record_file = record_path / f"{group_id}.json"
            if not record_file.exists():
                content = f"未找到群 {group} 的记录文件。"
            else:
                with open(record_file, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                try:
                    record_id = int(parts[2].strip())
                except ValueError:
                    content = "ID 格式错误"
                else:
                    target_record = next((r for r in data_json if r["id"] == record_id), None)
                    if not target_record:
                        content = f"群 {group} 不存在记录 ID={record_id}"
                    else:
                        mode = parts[3].strip() if len(parts) >= 4 else None
                        if mode is None:
                            txt_lines = [f"{m['name']}: {m['content']}" for m in target_record["messages"]]
                            txt_content = "\n".join(txt_lines)
                            output_path = record_path / f"{group_id}_record_{record_id}.txt"
                            with open(output_path, "w", encoding="utf-8") as f:
                                f.write(txt_content)
                            content = f"[文件:{output_path}]"
                        elif mode == "转发":
                            seq_nodes = "".join(
                                f"[节点:{m['user']}|{m['name']}|{m['content']}]" for m in target_record["messages"])
                            content = f"[节点:3502644244|LR5921|{seq_nodes}]"
                        elif mode == "匿名":
                            name_map = {}
                            next_index = 0

                            txt_lines = []
                            for m in target_record["messages"]:
                                if m["name"] not in name_map:
                                    if next_index < len(name_pool):
                                        name_map[m["name"]] = name_pool[next_index]
                                        next_index += 1
                                    else:
                                        name_map[m["name"]] = f"匿名{next_index}"
                                        next_index += 1
                                anon_name = name_map[m["name"]]
                                txt_lines.append(f"{anon_name}: {m['content']}")

                            txt_content = "\n".join(txt_lines)
                            output_path = record_path / f"{group_id}_record_{record_id}_匿名.txt"
                            with open(output_path, "w", encoding="utf-8") as f:
                                f.write(txt_content)
                            content = f"[文件:{output_path}]"
                        else:
                            content = "格式错误，请使用:'/记录导出,群,id'、'/记录导出,群,id,转发'或'/记录导出,群,id,匿名'"
    else:
        content = "格式错误，请使用'/记录导出','/记录导出,群,id','/记录导出,群,id,转发'"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group
    )
    return content
