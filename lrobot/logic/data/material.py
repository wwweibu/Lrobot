# TODO 之后便捷更新数据库物资时使用
import os
from config import path,query_database, update_database


async def query_material(table_name):
    # 查询对应表的所有物资信息
    query = f"PRAGMA table_info(material_{table_name});"
    columns_info = await query_database(query)

    # 提取所有列名
    table_list = [column["name"] for column in columns_info]
    query = f"SELECT {', '.join(table_list)} FROM material_{table_name} ORDER BY id;"
    print(query)
    details = await query_database(query)
    print(details)

    # 构建响应数据
    response_data = []
    for row in details:
        id = row.get("id")
        # 生成图片的 URL
        row["image_path"] = f"https://whumystery.cn/hjd/static/{table_name}/{id}.png"
        response_data.append(row)
    return response_data


async def delete_materials(selected_type, original_id):
    # 删除物资操作
    exists = await query_database(
        f"SELECT COUNT(*) FROM material_{selected_type} WHERE id = :originalID",
        {"originalID": original_id},
    )

    if not exists or exists[0][0] == 0:
        return 0  # 物资不存在

    # 删除旧图片
    old_image_path = os.path.join(
        "apps", "static", "images", selected_type, f"{original_id}.png"
    )
    if os.path.exists(old_image_path):
        os.remove(old_image_path)

    # 根据游戏 ID 删除对应的记录
    update = f"DELETE FROM material_{selected_type} WHERE id = :originalID"
    await update_database(update, {"originalID": original_id})
    return 1


async def update_materials(table_name, original_id, request, image):
    # 查询原始数据是否存在
    original_data = await query_database(
        f"SELECT * FROM material_{table_name} WHERE id = :originalID",
        {"originalID": original_id},
    )

    if not original_data:
        return 0, None, None

    query = f"PRAGMA table_info(materials_{table_name});"
    columns_info = await query_database(query)
    table_list = [column["name"] for column in columns_info]

    # 收集新的信息并处理布尔值和空值
    new_details = {}
    for attr in table_list:
        value = request.form.get(attr, "").strip()
        if value == "":
            new_details[attr] = None
        else:
            new_details[attr] = value

    new_id = new_details.get("id")  # 获取新 ID
    new_details["newID"] = new_id
    new_details["originalID"] = original_id

    # 检测新 ID 是否重复
    if new_id != original_id:
        existing_result = await query_database(
            f"SELECT * FROM material_{table_name} WHERE id = :newID", {"newID": new_id}
        )
        if existing_result:
            return new_id, None, None

    # 判断上传的图片是否存在
    if image and image.filename != "":
        old_path = path / "storage/file/resource" / table_name / f"{original_id}.png"
        if os.path.exists(old_path):
            os.remove(old_path)
        new_path = path / "storage/file/resource" / table_name / f"{new_id}.png"
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        with open(new_path, "wb") as f:
            f.write(await image.read())

    # 更新数据库中的记录
    update = f"""
              UPDATE material_{table_name} 
              SET id = :newID, {', '.join([f'{attr} = :{attr}' for attr in table_list if attr != 'id'])}
              WHERE id = :originalID
          """
    await update_database(update, new_details)

    filtered_new_values = [
        f"'{new_details[attr]}'"
        for attr in table_list
        if attr not in ["newID", "originalID"]
    ]

    return -1, original_data, filtered_new_values


async def add_materials(selected_type, request):
    file = request.files.get("image")
    owner = request.form.get("Owner")
    is_club = owner == "社团"

    # 获取新 ID
    if selected_type == "publications":
        max_id = await query_database("SELECT MAX(id) FROM material_publications")
        new_id = (int(max_id[0][0]) or 0) + 1
    else:
        if is_club:
            max_id = await query_database(
                f"SELECT MAX(CAST(TRIM(id) AS INTEGER)) FROM material_{selected_type} WHERE CAST(TRIM(id) AS INTEGER) BETWEEN 0 AND 999;"
            )
            new_id = str((int(max_id[0][0]) or 0) + 1).zfill(4)
        else:
            max_id = await query_database(
                f"SELECT MAX(CAST(TRIM(id) AS INTEGER)) FROM material_{selected_type} WHERE CAST(TRIM(id) AS INTEGER) BETWEEN 1000 AND 1999;"
            )
            new_id = str((int(max_id[0][0]) or 1000) + 1).zfill(4)

    if file:
        image_path = os.path.join(
            "apps", "static", "images", selected_type, f"{new_id}.png"
        )
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        file.save(image_path)

    query = f"PRAGMA table_info(materials_{selected_type});"
    columns_info = await query_database(query)
    table_list = [column[1] for column in columns_info]

    # 收集信息详情并处理布尔值和空值
    details = {"id": new_id}
    for attr in table_list:
        if attr == "id":  # 如果 attr 是 ID，跳过处理
            continue
        value = request.form.get(attr, "").strip()
        if value == "":
            details[attr] = None
        elif value.lower() == "true":
            details[attr] = 1
        elif value.lower() == "false":
            details[attr] = 0
        else:
            details[attr] = value

    # 将信息详情插入到数据库
    insert_sql = f"""
                    INSERT INTO material_{selected_type} ({', '.join(table_list)})
                    VALUES ({', '.join([':' + attr for attr in table_list])})
                """
    await update_database(insert_sql, details)

    filtered_new_values = [f"'{str(details[attr])}'" for attr in table_list]
    return filtered_new_values
