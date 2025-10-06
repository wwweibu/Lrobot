"""活动相关"""

import re
import json

from logic import data
from message.handler.msg import Msg
from config import monitor_adapter, path, future, database_update


async def merge_img():
    """生成合并后的寻宝群总图"""
    group_data = await data.system_get("hunt_group")
    if not group_data:
        return None

    group_list = json.loads(group_data)
    groups = group_list.get("groups", [])
    if not groups:
        return None

    temp_images = []
    for g in groups:
        gid = g["id"]
        info = g["info"]

        text_img_path = path / f"storage/file/command/hunt/tmp_text_{gid}.jpg"
        await data.text_to_image(f"群{gid}: {info}", text_img_path)

        qr_img_path = path / f"storage/file/command/hunt/{gid}.jpg"
        if not qr_img_path.exists():
            continue

        merged_single_path = path / f"storage/file/command/hunt/tmp_merge_{gid}.jpg"
        await data.image_merge([text_img_path, qr_img_path], merged_single_path, direction="vertical")

        temp_images.append(merged_single_path)

    if not temp_images:
        return None

    # 最终合并所有单群图
    final_output = path / "storage/file/command/hunt/merge.jpg"
    await data.image_merge(temp_images, final_output, direction="vertical")
    await database_update(
        "DELETE FROM user_media WHERE filepath = %s",
        (final_output,)
    )
    for platform in ["WECHAT", "BILI"]:
        Msg(
            platform=platform,
            event="发送",
            kind="私聊发送",
            content=f"[图片:{final_output}]",
        )

    return final_output


@monitor_adapter("/活动_寻宝_群")
async def activity_hunt_group(msg: Msg):
    """获取寻宝群二维码"""
    group_data = await data.system_get("hunt_group")
    if not group_data:
        content = "当前没有设置寻宝群"
    else:
        if msg.platform == "LR5921":
            group_list = json.loads(group_data)
            nodes = []
            for g in group_list.get("groups", []):
                gid = g["id"]
                info = g["info"]
                text_node = f"[节点:3502644244|LR5921|群{gid}:{info}]"
                img_path = path / f"storage/file/command/hunt/{gid}.jpg"
                img_node = f"[节点:3889270613|LR232|[图片:{img_path}]]"

                nodes.append(text_node)
                nodes.append(img_node)

            content = "".join(nodes)
            content = f"[节点:3502644244|LR5921|{content}]"
        else:
            final_output = path / "storage/file/command/hunt/merge.jpg"
            content = f"[图片:{final_output}]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/活动_寻宝_群设置")
async def activity_hunt_group_set(msg: Msg):
    """设置寻宝群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    group_data = await data.system_get(f"hunt_group")
    if group_data:
        group_list = json.loads(group_data)
    else:
        group_list = {"max_id": 0, "groups": []}
    new_id = group_list["max_id"] + 1

    if len(parts) == 2:
        info = parts[1].strip()
    else:
        info = f"本群为寻宝{new_id - 1}群"
    group_list["groups"].append({"id": new_id, "info": info})
    group_list["max_id"] = new_id
    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
    content = f"设置成功，本群为 {new_id} 群，请上传二维码"
    await data.status_add(msg.user, "寻宝添加群", new_id)
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )


@monitor_adapter("/活动_寻宝_群上传")
async def activity_hunt_group_upload(msg: Msg):
    """寻宝群上传"""
    group_id = await data.status_check(msg.user, "寻宝添加群")
    file_path = path / f"storage/file/command/hunt/{group_id}.jpg"
    file_url = msg.content[0]['data'].get('url')
    if file_url:
        await data.file_download(file_path, file_url)
    else:  # LR5921 文件格式图片
        msg.content[0]['data']['file_path'] = str(file_path)
        msg1 = Msg(
            platform="LR5921",
            event="发送",
            kind="文件下载",
            content=msg.content
        )
        await future.wait(msg1.num, f"[消息]文件下载超时-> {msg.content}")
    await merge_img()
    await data.status_delete(msg.user, "寻宝添加群")
    content = "添加成功"
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


@monitor_adapter("/活动_寻宝_群介绍")
async def activity_hunt_group_info(msg: Msg):
    """修改群介绍"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=2)
    if len(parts) == 3:
        try:
            group_id = int(parts[1].strip())
        except ValueError:
            content = "群 ID 错误，请输入数字"
        else:
            new_info = parts[2].strip()
            group_data = await data.system_get("hunt_group")
            if not group_data:
                content = "当前没有任何寻宝群"
            else:
                group_list = json.loads(group_data)
                target = None
                for g in group_list.get("groups", []):
                    if g["id"] == group_id:
                        target = g
                        break
                if not target:
                    content = f"未找到 ID 为 {group_id} 的寻宝群"
                else:
                    target["info"] = new_info
                    # 写回数据库
                    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
                    content = f"设置成功，群 {group_id} 的介绍已修改为：{new_info}"
                    await merge_img()
    else:
        content = "格式错误，请使用'/寻宝群介绍,1,这是介绍'类似格式"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_寻宝_群删除")
async def activity_hunt_group_delete(msg: Msg):
    """删除群"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    if len(parts) == 2:
        try:
            group_id = int(parts[1].strip())
        except ValueError:
            content = "群 ID 错误，请输入数字"
        else:
            group_data = await data.system_get("hunt_group")
            if not group_data:
                content = "当前没有任何寻宝群"
            else:
                group_list = json.loads(group_data)
                groups = group_list.get("groups", [])

                new_groups = [g for g in groups if g["id"] != group_id]

                if len(new_groups) == len(groups):
                    content = f"未找到 ID 为 {group_id} 的寻宝群"
                else:
                    group_list["groups"] = new_groups
                    # 写回数据库
                    await data.system_edit("hunt_group", json.dumps(group_list, ensure_ascii=False))
                    content = f"已删除 ID 为 {group_id} 的寻宝群"
                    await merge_img()
    else:
        content = "格式错误，请使用'/寻宝群删除,1'类似格式"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_寻宝_题目")
async def activity_hunt_problem(msg: Msg):
    """获取指定题目"""
    parts = re.split(r"[，,]", Msg.content_join(msg.content), maxsplit=1)
    user_list = await data.user_identify(msg.user, msg.platform)
    if "内阁" not in user_list:
        return
    if len(parts) != 2:
        content = "格式错误，请使用 '/寻宝题目,数字'"
    else:
        try:
            ans_id = int(parts[1].strip())
        except ValueError:
            content = "答案 ID 错误，请输入数字"
        else:
            answer_file = path / "storage/file/command/hunt/answer.txt"

            if not answer_file.exists():
                content = "答案文件不存在"
            else:
                raw = answer_file.read_text(encoding="utf-8")
                # 按空行分割段落，保留多行内容
                answers = [a.strip() for a in re.split(r"\n\s*\n", raw) if a.strip()]

                if ans_id < 1 or ans_id > len(answers):
                    content = f"未找到 ID 为 {ans_id} 的答案"
                else:
                    answer_text = answers[ans_id - 1]
                    img_path = path / f"storage/file/command/hunt/answer_{ans_id}.jpg"

                    if img_path.exists():
                        content = f"{answer_text}[图片:{img_path}]"
                    else:
                        content = answer_text

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_日记_开始")
async def activity_diary_start(msg: Msg):
    """日记开始答题"""
    await data.status_add(msg.user, "日记", 1)
    content = f"[图片:{path}/storage/file/command/diary/1.png]"
    content += ("所有答案的形式均为小写英文字母/数字/中文\n"
                "且中间无空格\n"
                "输入'航海日记提示'获取当前题目的提示\n"
                "可在绑定的多平台同步答题\n"
                "不要过于依赖提示哦＞﹏＜")

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        content=content,
        seq=msg.seq,
        user=msg.user,
        group=msg.group,
    )
    return content


@monitor_adapter("/活动_日记_提示")
async def activity_diary_prompt(msg: Msg):
    """日记提示"""
    id = await data.status_check(msg.user, "日记")
    try:
        id = int(id)
    except (ValueError, TypeError):
        content = "日记 ID 错误"
    else:
        diary_file = path / "storage/file/command/diary/answer.txt"
        if not diary_file.exists():
            content = "日记题目文件不存在"
        else:
            lines = diary_file.read_text(encoding="utf-8").splitlines()
            # 去除空行，保证每两行一组
            lines = [l.strip() for l in lines if l.strip()]
            # 按两行一组（提示, 答案）
            groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]

            if id < 1 or id > len(groups):
                content = f"未找到 ID 为 {id} 的日记题目"
            else:
                prompt = groups[id - 1][0]
                content = f"提示: {prompt}"

    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content


async def activity_diary_answer(msg: Msg):
    """日记答题"""
    id = await data.status_check(msg.user, "日记")
    try:
        id = int(id)
    except (ValueError, TypeError):
        return False
    diary_file = path / "storage/file/command/diary/answer.txt"
    if not diary_file.exists():
        return False

    lines = diary_file.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in lines if l.strip()]
    groups = [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]

    if id < 1 or id > len(groups):
        return False
    correct_answer = groups[id - 1][1].strip()
    user_answer = Msg.content_join(msg.content).strip()
    if user_answer == correct_answer:
        if id == 16:
            await data.status_delete(msg.user, "日记")
        else:
            await data.status_add(msg.user, "日记", id + 1)
        await activity_diary_answer_write(msg, id)
        return True
    return False


@monitor_adapter("/活动_日记_答题")
async def activity_diary_answer_write(msg: Msg, id):
    """日记答题记录"""
    content = f"[图片:{path}/storage/file/command/diary/{id + 1}.png]"
    Msg(
        platform=msg.platform,
        event="发送",
        kind=f"{msg.kind[:2]}发送",
        seq=msg.seq,
        content=content,
        user=msg.user,
        group=msg.group,
    )
    return content
