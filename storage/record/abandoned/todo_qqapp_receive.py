# 物资租借小程序接收消息
import requests as re
from fastapi import APIRouter, Request, UploadFile
from config import config
from log import loggers
from logic import (
    authenticate_user,
    query_material,
    delete_materials,
    update_materials,
    add_materials,
)


router = APIRouter()
adapter_logger = loggers["adapter"]


@router.get("/login")
async def material_login(nickname: str, code: str):
    """登录"""
    if nickname in config["admin_nicknames"]:
        # 只处理管理员列表中的昵称
        response = re.get(
            "https://api.q.qq.com/sns/jscode2session",
            params={
                "appid": config["QQAPP_ID"],
                "secret": config["QQAPP_SECRET"],
                "js_code": code,  # 用 encryptedData 作为 js_code 发送
                "grant_type": "authorization_code",
            },
        )
        # 发送验证消息
        if response.status_code == 200:
            data = response.json()
            unionid = data.get("unionid")
            # print(unionid) # 用于添加管理员，先把user_name添加进列表，然后查看打印出的unionid
            if unionid in config["admin_uid"]:
                adapter_logger.info(
                    f"⌈QQAPP⌋ 管理员{nickname}成功登录", extra={"event": "程序登录"}
                )
                return {"success": True, "message": "0"}  # 管理员登录成功

    result = await authenticate_user(nickname, "1")
    if result == 1:
        adapter_logger.info(
            f"⌈QQAPP⌋ 用户{nickname}成功登录", extra={"event": "程序登录"}
        )
        return {"success": True, "message": "1"}  # 普通用户登录成功
    else:
        adapter_logger.error(
            f"⌈QQAPP⌋ 用户{nickname}登录失败", extra={"event": "程序登录"}
        )
        return {"success": True, "message": "2"}  # 登录失败


@router.get("/query")
async def material_query(
    nickname: str,
    code: str,
    selectedType: str,
):
    # 用户访问资源
    auth_code = await authenticate_user(nickname, code)
    if auth_code == 2:
        adapter_logger.error(
            f"⌈QQAPP⌋ 陌生用户{nickname}访问资源列表", extra={"event": "资源访问"}
        )
        return {"success": True, "message": "3"}

    if selectedType not in ["boardgames", "scriptmurders", "publications"]:
        adapter_logger.error(
            f"⌈QQAPP⌋ 用户{nickname}访问无效的物资类型", extra={"event": "资源访问"}
        )

        return {"success": True, "message": "4"}

    response_data = await query_material(selectedType)
    adapter_logger.info(
        f"⌈QQAPP⌋ 用户{nickname}获取物资列表成功", extra={"event": "资源访问"}
    )
    return {"success": True, "message": "5", "data": response_data}


@router.get("/delete")
async def material_delete(nickname: str, code: str, selectedType: str, originalID: str):
    # 管理员删除资源
    auth_code = await authenticate_user(nickname, code)
    if auth_code != 0:
        adapter_logger.error(
            f"⌈QQAPP⌋ 陌生用户{nickname}试图删除资源", extra={"event": "资源删除"}
        )
        return {"success": True, "message": "6"}

    result = await delete_materials(selectedType, originalID)
    if result == 1:
        adapter_logger.info(
            f"⌈QQAPP⌋ 管理{nickname}删除了ID为{originalID}的记录",
            extra={"event": "资源删除"},
        )
        return {"success": True, "message": "9"}
    else:
        adapter_logger.error(
            f"⌈QQAPP⌋ 管理{nickname}试图删除不存在的资源", extra={"event": "资源删除"}
        )
        return {"success": True, "message": "7"}


@router.post("/update")
async def material_update(
    nickname: str,
    code: str,
    selectedType: str,
    originalID: str,
    image: UploadFile,
    request: Request,
):
    # 管理员更新资源
    auth_code = await authenticate_user(nickname, code)
    if auth_code != 0:
        adapter_logger.error(
            f"⌈QQAPP⌋ 陌生用{nickname}试图修改资源", extra={"event": "资源修改"}
        )
        return {"success": True, "message": "10"}

    if selectedType not in ["boardgames", "scriptmurders", "publications"]:
        adapter_logger.error(
            f"⌈QQAPP⌋ 管理员{nickname}修改无效的物资类型", extra={"event": "资源修改"}
        )
        return {"success": True, "message": "11"}

    result, original_data, filtered_new_values = await update_materials(
        selectedType, originalID, request, image
    )
    if result == 0:
        adapter_logger.error(
            f"⌈QQAPP⌋ 管理员{nickname}试图修改不存在的资源", extra={"event": "资源修改"}
        )
        return {"success": True, "message": "12"}
    elif result != -1:
        adapter_logger.error(
            f"管理员{nickname}试图把{originalID}修改成已经存在的id{result}",
            extra={"event": "资源修改"},
        )
        return {"success": True, "message": "13"}
    else:
        adapter_logger.info(
            f"管理员{nickname}成功更新数据库{selectedType}:\n{original_data}\n{', '.join(filtered_new_values)}",
            extra={"event": "资源修改"},
        )
        return {"success": True, "message": "14"}


@router.post("/add")
async def material_add(nickname: str, code: str, selectedType: str, request: Request):
    # 管理员添加资源
    auth_code = await authenticate_user(nickname, code)
    if auth_code != 0:
        adapter_logger.error(
            f"陌生用户{nickname}试图添加资源",
            extra={"event": "资源添加"},
        )
        return {"success": True, "message": "15"}

    if selectedType not in ["boardgames", "scriptmurders", "publications"]:
        adapter_logger.error(
            f"管理员{nickname} 添加无效的物资类型",
            extra={"event": "资源添加"},
        )
        return {"success": True, "message": "16"}

    filtered_new_values = await add_materials(selectedType, request)

    adapter_logger.info(
        f"管理员{nickname}成功添加物资到数据库{selectedType}:\n{filtered_new_values}",
        extra={"event": "资源添加"},
    )

    return {"success": True, "message": "17"}

# from config import config, update_database, query_database


# TODO qq小程序合并到identify部分
# async def authenticate_user(nickname, code):
#     # 管理员身份确认
#     if nickname in config["admin_nicknames"] and code == "0":
#         return 0
#     elif nickname in ["One-8587", "Two-8587", "New Wave", "梦周王良将舞"]:
#         # 测试员账号
#         return 1
#     # 从数据库中查找用户
#     user_found = await query_database(
#         "SELECT * FROM user_all WHERE qq_name = :nickname", {"nickname": nickname}
#     )
#     if user_found and code == "1":
#         return 1
#     return 2
#
#
# # 仅作参考，到 abandoned
# async def add_users(user_list, identity):
#     # 更新 users_qq_nickname 表，如果 qq_number 存在则更新 nickname及identity
#     for user in user_list:
#         qq_number = user[0]  # user_id
#         nickname = user[1]  # nickname
#
#         # 查询当前用户的 identity
#         identity_query = "SELECT identity FROM user_all WHERE qq_number = ?"
#         current_identity = await query_database(identity_query, (qq_number,))
#
#         if current_identity:  # 如果存在
#             current_identity = current_identity[0][0]
#             # 更新 nickname
#             update_nickname_query = (
#                 "UPDATE user_all SET nickname = ? WHERE qq_number = ?"
#             )
#             await update_database(update_nickname_query, (nickname, qq_number))
#
#             # 如果 identity 从 1 改为 2,则更新 identity
#             if current_identity == 1 and identity == 2:
#                 update_identity_query = (
#                     "UPDATE user_all SET identity = ? WHERE qq_number = ?"
#                 )
#                 await update_database(update_identity_query, (2, qq_number))
#         else:  # 如果不存在，插入新记录
#             insert_query = """
#             INSERT INTO user_all (qq_number, nickname, identity)
#             VALUES (?, ?, ?)
#             """
#             await update_database(insert_query, (qq_number, nickname, identity))
#
#
# async def users_all():
#     # 删除表
#     await update_database("DROP TABLE IF EXISTS users_all")
#
#     # 创建表
#     create_table_query = """
#            CREATE TABLE IF NOT EXISTS users_all (
#                qq_number TEXT PRIMARY KEY,
#                qq_name TEXT,
#                identity TEXT,
#                name TEXT,
#                nickname TEXT,
#                gender TEXT,
#                grade TEXT,
#                major TEXT,
#                student_id TEXT,
#                phone TEXT,
#                political_status TEXT,
#                hometown TEXT,
#                card_number TEXT,
#                id TEXT
#            );
#            """
#     await execute_update(create_table_query)
#
#     # 获取 users_qq_nickname 表中的数据
#     users_qq_nickname_data = await execute_query(
#         "SELECT qq_number, nickname, identity FROM users_qq_nickname"
#     )
#
#     # 插入合并数据
#     for qq_number, qq_name, identity in users_qq_nickname_data:
#         # 查询对应的 users_info 数据
#         users_info_query = """
#                SELECT 姓名, 代号, 性别, 年级, 专业, 学号, 电话, 政治面貌, 籍贯, 卡号, id
#                FROM users_info
#                WHERE qq = ?
#                """
#         users_info_data = await execute_query(users_info_query, (qq_number,))
#
#         # 默认将各字段设为 None，表示缺失
#         name = nickname = gender = grade = major = student_id = phone = (
#             political_status
#         ) = hometown = card_number = user_id = None
#
#         # 如果找到对应的 users_info 数据，则更新各字段
#         if users_info_data:
#             (
#                 name,
#                 nickname,
#                 gender,
#                 grade,
#                 major,
#                 student_id,
#                 phone,
#                 political_status,
#                 hometown,
#                 card_number,
#                 user_id,
#             ) = users_info_data[0]
#
#         # 插入到 users_all 表
#         insert_query = """
#                        INSERT INTO users_all (
#                            qq_number, qq_name, identity, name, nickname, gender, grade,
#                            major, student_id, phone, political_status, hometown, card_number, id
#                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                        """
#         await execute_update(
#             insert_query,
#             (
#                 qq_number,
#                 qq_name,
#                 identity,
#                 name,
#                 nickname,
#                 gender,
#                 grade,
#                 major,
#                 student_id,
#                 phone,
#                 political_status,
#                 hometown,
#                 card_number,
#                 user_id,
#             ),
#         )
