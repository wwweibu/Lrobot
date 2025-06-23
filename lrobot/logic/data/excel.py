# TODO 支持所有格式的excel
import pandas as pd
from .database import update_database, query_database


async def excel_to_users_info(excel_file):
    # 将会员信息收集表收集结果转换到users_info表
    df = pd.read_excel(excel_file, header=None)

    df.columns = df.iloc[0]  # 将第一行设置为列名
    df = df[1:]  # 删除第一行

    # 删除原来的表
    drop_query = "DROP TABLE IF EXISTS users_info"
    await execute_update(drop_query)

    # 创建表，使用固定的列名
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users_info (
        提交时间 TEXT,
        姓名 TEXT,
        代号 TEXT,
        性别 TEXT,
        年级 TEXT,
        专业 TEXT,
        学号 TEXT,
        电话 TEXT,
        qq TEXT,
        政治面貌 TEXT,
        籍贯 TEXT,
        卡号 TEXT,
        ID TEXT,
        提交者 TEXT
    );
    """
    await execute_update(create_table_query)

    for index, row in df.iterrows():
        if row["提交者（自动）"] == "LR5921":  # 检查提交者是否为 "LR5921"
            continue  # 跳过该行

        params = (
            str(row["提交时间（自动）"]),
            str(row["姓名（必填）"]),
            str(row["代号（自己取）（必填）"]),
            str(row["性别（必填）"]),
            str(row["年级（23/23研）（必填）"]),
            str(row["专业（必填）"]),
            str(row["学号（必填）"]),
            str(row["电话（必填）"]),
            str(row["qq（必填）"]),
            str(row["政治面貌（必填）"]),
            str(row["籍贯（必填）"]),
            str(row["卡号"]),
            str(row["ID"]),
            str(row["提交者（自动）"]),
        )
        placeholders = ", ".join("?" * 14)  # 14个占位符
        query = f"INSERT INTO users_info (提交时间, 姓名, 代号, 性别, 年级, 专业, 学号, 电话, qq, 政治面貌, 籍贯, 卡号, ID, 提交者) VALUES ({placeholders})"
        await execute_update(query, params)


async def excel_fill(excel_file):
    #  收集表填写者
    df = pd.read_excel(excel_file, header=None)

    # 将第一行设置为列名，并删除第一行
    df.columns = df.iloc[0]
    df = df[1:]

    # 检查是否存在提交者列
    if "提交者（自动）" not in df.columns:
        return []

    # 提取提交者列，并去重和去掉空值
    submitters = df["提交者（自动）"].dropna().unique()

    # 转换为列表并返回
    return submitters.tolist()


async def excel_export(excel_file):
    # 将数据库中所有表导入excel
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = await execute_query(query)

    # 只导出活动、物资表
    tables = [
        table
        for table in tables
        if table[0]
        in (
            "activities",
            "materials_boardgames",
            "materials_publications",
            "materials_scriptmurders",
        )
    ]

    with pd.ExcelWriter(excel_file) as writer:
        for table in tables:
            table_name = table[0]  # 获取表名

            # 获取表的列名
            columns_query = f"PRAGMA table_info({table_name})"
            columns_info = await execute_query(columns_query)
            column_names = [column[1] for column in columns_info]  # 获取列名

            # 读取表的数据
            query = f"SELECT * FROM {table_name}"
            rows = await execute_query(query)

            if rows:
                df = pd.DataFrame(rows, columns=column_names)  # 使用列名创建 DataFrame

                # 将所有列转换为字符串类型
                for col in df.columns:
                    df[col] = df[col].astype(str)

                # 将数据写入 Excel 文件
                df.to_excel(writer, sheet_name=table_name, index=False)
            else:
                print(f"表 {table_name} 的查询结果为空，跳过导出。")


def handle_na(df):
    # 将NaN、None、空字符串等替换为统一的值
    return df.map(
        lambda x: (
            "NULL"
            if pd.isna(x)
            or x is None
            or x == ""
            or x == "None"
            or x == "NaN"
            or x == "nan"
            else str(x)
        )
    )


async def generate_instructions(excel_df, db_df, common_ids, table_name):
    instructions = []  # 用于存储所有指令

    # 生成修改指令
    for _, row in excel_df[excel_df["id"].isin(common_ids)].iterrows():
        db_row = db_df[db_df["id"] == row["id"]]
        if not db_row.empty:
            db_row = db_row.iloc[0]  # 取第一行数据
            differences = {}
            for col in db_df.columns:  # 比较所有列
                db_value = db_row.get(col, "NULL")  # 使用 get 方法，缺失值默认 "NULL"
                excel_value = row.get(col, "NULL")  # 使用 get 方法，缺失值默认 "NULL"
                if db_value != excel_value:
                    differences[col] = (db_value, excel_value)
            if differences:
                instruction = {
                    "type": "modify",
                    "id": row["id"],
                    "table": table_name,
                    "differences": differences,
                }
                instructions.append(instruction)

    # 生成添加指令
    for _, row in excel_df[~excel_df["id"].isin(db_df["id"])].iterrows():
        instruction = {
            "type": "add",
            "id": row["id"],
            "table": table_name,
            "data": row.to_dict(),
        }
        instructions.append(instruction)

    # 生成删除指令
    for _, row in db_df[~db_df["id"].isin(excel_df["id"])].iterrows():
        instruction = {
            "type": "delete",
            "id": row["id"],
            "table": table_name,
            "data": row.to_dict(),  # 删除的数据也包含详细信息
        }
        instructions.append(instruction)

    return instructions


async def excel_to_database_show(excel_file):
    # excel导入数据库指令生成
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = await execute_query(query)
    table_names = [table[0] for table in tables]  # 获取所有表名

    # 读取 Excel 文件中的所有表名
    excel_sheets = pd.ExcelFile(excel_file).sheet_names

    all_instructions = []  # 用于存储所有表的指令

    for table_name in table_names:
        if table_name in excel_sheets:
            # 从数据库中获取该表的数据
            query = f"SELECT * FROM {table_name}"
            db_rows = await execute_query(query)
            columns_query = f"PRAGMA table_info({table_name})"
            columns_info = await execute_query(columns_query)
            column_names = [column[1] for column in columns_info]
            db_df = pd.DataFrame(db_rows, columns=column_names)
            db_df = db_df.map(str)  # 强制所有列为字符串类型

            excel_df = pd.read_excel(excel_file, sheet_name=table_name, dtype=str)

            # 将 NaN 和 None 替换为统一的 "NULL"
            excel_df = handle_na(excel_df)
            db_df = handle_na(db_df)

            # 找出 ID 在 Excel 和数据库中都存在的项
            common_ids = set(excel_df["id"]).intersection(set(db_df["id"]))

            # 生成指令列表
            instructions = await generate_instructions(
                excel_df, db_df, common_ids, table_name
            )

            # 将生成的指令以清晰的方式发送给用户
            table_instructions = []  # 存储当前表的所有指令
            for idx, instruction in enumerate(instructions):
                if instruction["type"] == "modify":
                    instruction_str = (
                        f"修改 ID: {instruction['id']} 表 {instruction['table']}"
                    )
                    for col, (old_value, new_value) in instruction[
                        "differences"
                    ].items():
                        instruction_str += (
                            f"，修改字段: {col}， 旧值: {old_value}， 新值: {new_value}"
                        )
                    table_instructions.append(instruction_str)
                elif instruction["type"] == "add":
                    instruction_str = f"添加 ID: {instruction['id']} 表 {instruction['table']}，数据: {instruction['data']}"
                    table_instructions.append(instruction_str)
                elif instruction["type"] == "delete":
                    instruction_str = f"删除 ID: {instruction['id']} 表 {instruction['table']}，数据: {instruction['data']}"
                    table_instructions.append(instruction_str)

            all_instructions.append(
                "\n".join(table_instructions)
            )  # 每个表的指令以字符串形式加入总指令列表

    # 返回所有表的指令列表
    return "\n".join(all_instructions)  # 用 /n 隔开每个表的指令


async def excel_to_database_deal(instructions_str, user_response):
    # excel导入数据库指令执行
    instructions = instructions_str.split("\n")  # 将指令字符串转换为列表
    for idx, instruction in enumerate(instructions):
        if idx >= len(user_response):
            break  # 用户回应可能比指令少，忽略多余的指令
        if user_response[idx] == "1":  # 用户选择执行
            if "修改" in instruction:
                # 解析修改指令
                parts = instruction.split("，")
                # 提取表名和ID
                table_name = parts[0].split("表")[1].split()[0].strip()
                record_id = parts[0].split("ID:")[1].strip()

                # 提取字段名、旧值和新值
                field_name = parts[1].split("修改字段:")[1].strip()
                old_value = parts[2].split("旧值:")[1].strip()
                new_value = parts[3].split("新值:")[1].strip()
                differences = {field_name: {"old": old_value, "new": new_value}}
                await modify_record(table_name, record_id, differences)

            elif "添加" in instruction:
                # 解析添加指令
                parts = instruction.split("，")
                table_name = parts[0].split("表 ")[1]  # 表名
                record_id = parts[0].split("ID:")[1].split()[0]  # ID
                data = eval(parts[1].split("数据: ")[1])  # 转为字典
                await add_record(table_name, record_id, data)

            elif "删除" in instruction:
                # 解析删除指令
                parts = instruction.split("，")
                table_name = parts[0].split("表 ")[1]  # 表名
                record_id = parts[0].split("ID:")[1].split()[0]  # ID
                data = eval(parts[1].split("数据: ")[1])  # 转为字典
                await delete_record(table_name, record_id, data)


async def modify_record(table_name, record_id, differences):
    #  修改数据库记录
    set_clauses = ", ".join([f"{key} = ?" for key in differences.keys()])
    query = f"UPDATE {table_name} SET {set_clauses} WHERE id = ?"
    values = list(differences.values()) + [record_id]
    print(f"[修改操作] 表: {table_name}, ID: {record_id}, 修改内容: {differences}")
    # await execute_query(query, values)  # 执行修改语句


async def add_record(table_name, record_id, data):
    #  添加数据库记录
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    values = list(data.values())
    print(f"[添加操作] 表: {table_name}, 数据: {data}")
    # await execute_query(query, values)  # 执行插入语句


async def delete_record(table_name, record_id, data):
    #  删除数据库记录
    query = f"DELETE FROM {table_name} WHERE id = ?"
    print(f"[删除操作] 表: {table_name}, ID: {record_id}, 数据: {data}")
    # await execute_query(query, [record_id])  # 执行删除语句
