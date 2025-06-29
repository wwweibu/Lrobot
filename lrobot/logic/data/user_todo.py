# TODO
from config import config, update_database, query_database


# TODO qq小程序合并到identify部分
async def authenticate_user(nickname, code):
    # 管理员身份确认
    if nickname in config["admin_nicknames"] and code == "0":
        return 0
    elif nickname in ["One-8587", "Two-8587", "New Wave", "梦周王良将舞"]:
        # 测试员账号
        return 1
    # 从数据库中查找用户
    user_found = await query_database(
        "SELECT * FROM user_all WHERE qq_name = :nickname", {"nickname": nickname}
    )
    if user_found and code == "1":
        return 1
    return 2


# 仅作参考，到 abandoned
async def add_users(user_list, identity):
    # 更新 users_qq_nickname 表，如果 qq_number 存在则更新 nickname及identity
    for user in user_list:
        qq_number = user[0]  # user_id
        nickname = user[1]  # nickname

        # 查询当前用户的 identity
        identity_query = "SELECT identity FROM user_all WHERE qq_number = ?"
        current_identity = await query_database(identity_query, (qq_number,))

        if current_identity:  # 如果存在
            current_identity = current_identity[0][0]
            # 更新 nickname
            update_nickname_query = (
                "UPDATE user_all SET nickname = ? WHERE qq_number = ?"
            )
            await update_database(update_nickname_query, (nickname, qq_number))

            # 如果 identity 从 1 改为 2,则更新 identity
            if current_identity == 1 and identity == 2:
                update_identity_query = (
                    "UPDATE user_all SET identity = ? WHERE qq_number = ?"
                )
                await update_database(update_identity_query, (2, qq_number))
        else:  # 如果不存在，插入新记录
            insert_query = """
            INSERT INTO user_all (qq_number, nickname, identity)
            VALUES (?, ?, ?)
            """
            await update_database(insert_query, (qq_number, nickname, identity))


async def users_all():
    # 删除表
    await update_database("DROP TABLE IF EXISTS users_all")

    # 创建表
    create_table_query = """
           CREATE TABLE IF NOT EXISTS users_all (
               qq_number TEXT PRIMARY KEY,
               qq_name TEXT,
               identity TEXT,
               name TEXT,
               nickname TEXT,
               gender TEXT,
               grade TEXT,
               major TEXT,
               student_id TEXT,
               phone TEXT,
               political_status TEXT,
               hometown TEXT,
               card_number TEXT,
               id TEXT
           );
           """
    await execute_update(create_table_query)

    # 获取 users_qq_nickname 表中的数据
    users_qq_nickname_data = await execute_query(
        "SELECT qq_number, nickname, identity FROM users_qq_nickname"
    )

    # 插入合并数据
    for qq_number, qq_name, identity in users_qq_nickname_data:
        # 查询对应的 users_info 数据
        users_info_query = """
               SELECT 姓名, 代号, 性别, 年级, 专业, 学号, 电话, 政治面貌, 籍贯, 卡号, id
               FROM users_info
               WHERE qq = ?
               """
        users_info_data = await execute_query(users_info_query, (qq_number,))

        # 默认将各字段设为 None，表示缺失
        name = nickname = gender = grade = major = student_id = phone = (
            political_status
        ) = hometown = card_number = user_id = None

        # 如果找到对应的 users_info 数据，则更新各字段
        if users_info_data:
            (
                name,
                nickname,
                gender,
                grade,
                major,
                student_id,
                phone,
                political_status,
                hometown,
                card_number,
                user_id,
            ) = users_info_data[0]

        # 插入到 users_all 表
        insert_query = """
                       INSERT INTO users_all (
                           qq_number, qq_name, identity, name, nickname, gender, grade,
                           major, student_id, phone, political_status, hometown, card_number, id
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       """
        await execute_update(
            insert_query,
            (
                qq_number,
                qq_name,
                identity,
                name,
                nickname,
                gender,
                grade,
                major,
                student_id,
                phone,
                political_status,
                hometown,
                card_number,
                user_id,
            ),
        )
