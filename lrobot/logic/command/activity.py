# # TODO 改成自动获取活动
# import asyncio
# import re
# import time
# import json
# import jionlp as jio
# from message.handler.msg import Msg
# from config import config, path
# from logic import (
#     update_database,
#     identify_user,
#     check_status,
#     chinese_time,
#     add_status,
#     check_activity,
#     delete_status,
#     get_activity_msg_id,
#     edit_activity_all,
#     download_file,
#     query_activity,
# )
#
#
# # 禁用日志
# jio.logging = jio.set_logger(level="WARN", log_dir_name=None)
#
#
# def wrap_text(text, width=15):
#     return "\n".join(text[i : i + width] for i in range(0, len(text), width))
#
#
# async def activity_add(msg: Msg):
#     """认证成员添加活动"""
#     msg.content = re.sub(r"/活动添加[,，]?", "", msg.content).strip()
#     kind = msg.kind[:2]
#     qq = await identify_user(msg.source, msg.robot)
#
#     if not qq:
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="未绑定身份无法添加活动",
#             group=msg.group,
#         )
#         return
#
#     statuses = await check_status(qq)  # 检查用户状态
#     if "活动添加" in statuses:
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="活动审核中，请等待管理员审核再进行其他操作",
#             group=msg.group,
#         )
#         return
#
#     parts = re.split(r"[，,]", msg.content, maxsplit=4)  # 分割成五部分
#     while len(parts) < 5:
#         parts.append("未提供")  # 填充缺失的部分
#     event_name, event_time, event_duration, event_location, event_description = parts
#
#     # 时间转换
#     try:
#         event_time = jio.parse_time(
#             event_time, time_base=time.time(), time_type="time_point"
#         )
#         if event_time["type"] == "time_point" or event_time["type"] == "time_span":
#             event_time = event_time["time"][0]
#         else:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#                 group=msg.group,
#             )
#             return
#     except ValueError:
#         # 如果解析失败
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#             group=msg.group,
#         )
#         return
#
#     # 时间段转换
#     try:
#         event_duration = jio.parse_time(
#             event_duration, time_base=time.time(), time_type="time_delta"
#         )
#         if event_duration["type"] == "time_delta":
#             event_duration = event_duration["time"]
#         else:
#             event_duration = "待定"
#     except ValueError:
#         event_duration = "待定"
#
#     # 主持
#     event_qq = qq
#
#     # 简介换行
#     wrapped_description = wrap_text(event_description.strip())
#     # 时间输出
#     wrapped_time, wrapped_duration = chinese_time(event_time, event_duration)
#
#     content = (
#         "\n=========活动信息=========\n"
#         "\n"
#         f"名称: {event_name.strip()}\n"
#         f"时间: {wrapped_time.strip()}\n"
#         f"时长: {wrapped_duration.strip()}\n"
#         f"地点: {event_location.strip()}\n"
#         f"主持: {event_qq}\n"
#         "简介:\n"
#         f"{wrapped_description}\n"
#         "\n"
#         "======等待管理审核中======\n"
#         "======如有群聊请发码======\n"
#     )
#
#     query = """
#         INSERT INTO logic_activity (name, time, duration, location, qq, description, status,msg_id)
#         VALUES (?, ?, ?, ?, ?, ?, '待审核',?)
#         """
#     params = (
#         event_name,
#         event_time,
#         json.dumps(event_duration),
#         event_location,
#         event_qq,
#         event_description,
#         msg.seq,
#     )
#     id = await update_database(query, params)
#
#     # 更新用户状态为“活动添加审核”
#     await add_status(qq, "活动添加", id)
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content=content,
#         group=msg.group,
#     )
#
#     # 活动添加后通知管理员
#     content_lines = content.splitlines()
#     new_content = (
#         "\n".join(content_lines[:-1])
#         + "\n"
#         + (
#             "======回复消息以审核======\n"
#             "======并选择以下回答======\n"
#             "======/确认，活动类型=====\n"
#             "======/修改，活动类型=====\n"
#             "========/删除===========\n"
#             "======活动类型可查询======\n"
#         )
#     )
#     admin_list = config["私聊"]["活动管理员"]
#     await asyncio.sleep(10)
#     for admin in admin_list:
#         await add_status(admin, "管理活动添加", id)
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=admin,
#             seq=msg.seq,
#             content=new_content,
#             group=msg.group,
#         )
#
#
# async def activity_check(msg: Msg):
#     """管理员审核活动"""
#     kind = msg.kind[:2]
#     info = await check_status(msg.source, "管理活动修改")
#     match = re.search(r"\[回复(\d+)\]", msg.content)
#     if not match:
#         raise Exception(f"未找到回复内容 -> 活动审核 | 消息: {msg.content}")
#     reply_id = match.group(1)
#     if info:
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="正在修改其他活动，请先完成当前活动",
#             group=msg.group,
#         )
#         return
#     if "确认" in msg.content:
#         event_type = re.sub(r"确认[,，]?", "", msg.content).strip()
#         qq = await check_activity(reply_id, event_type, "确认")
#
#         if not qq:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="当前活动信息已失效",
#                 group=msg.group,
#             )
#         else:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="活动审核成功",
#                 group=msg.group,
#             )
#             Msg(
#                 robot="LR5921",
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=qq,
#                 seq=msg.seq,
#                 content="活动审核成功",
#                 group=msg.group,
#             )
#             await delete_status(qq, "活动添加")
#     elif "修改" in msg.content:
#         event_type = re.sub(r"修改[,，]?", "", msg.content).strip()
#         qq = await check_activity(reply_id, event_type, "修改")
#         if not qq:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="当前活动信息已失效",
#                 group=msg.group,
#             )
#         else:
#             activity = await get_activity_msg_id(reply_id)
#             if not activity:
#                 raise Exception(f"未找到活动 id -> 活动修改 | 消息 id: {reply_id}")
#             wrapped_time, wrapped_duration = chinese_time(
#                 activity["time"], json.loads(activity["duration"])
#             )
#             new_content = (
#                 "\n===========活动信息===========\n"
#                 "\n"
#                 f"名称: {activity['name']}\n"
#                 f"时间: {activity['time']}\n"
#                 f"时长: {wrapped_time}\n"
#                 f"地点: {wrapped_duration}\n"
#                 f"主持: {activity['qq']}\n"
#                 f"类型: {activity['type']}\n"
#                 "简介:\n"
#                 f"{wrap_text(activity['description'].strip())}\n"
#                 "\n"
#                 "========复制并修改发送========\n"
#             )
#             add_status(msg.source, "管理活动修改", activity["id"])
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content=new_content,
#                 group=msg.group,
#             )
#     elif "删除" in msg.content:
#         qq = await check_activity(reply_id, "", "删除")
#         if not qq:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="当前活动信息已失效",
#                 group=msg.group,
#             )
#         else:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="活动删除成功",
#                 group=msg.group,
#             )
#             Msg(
#                 robot="LR5921",
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=qq,
#                 seq=msg.seq,
#                 content="活动审核不通过，请联系管理员！",
#                 group=msg.group,
#             )
#             await delete_status(qq, "活动添加")
#     else:
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="格式错误，请长按消息选择引用，并输入'确认，血字'等指令",
#             group=msg.group,
#         )
#
#
# async def activity_check_edit(msg: Msg):
#     """管理员修改活动信息"""
#     kind = msg.kind[:2]
#     pattern = (
#         r"名称:\s*(.*?)\n"
#         r"时间:\s*(.*?)\n"
#         r"时长:\s*(.*?)\n"
#         r"地点:\s*(.*?)\n"
#         r"主持:\s*(.*?)\n"
#         r"类型:\s*(.*?)\n"
#         r"简介:\s*([^=]*)"  # 捕获简介直到下一个'='出现
#     )
#     match = re.search(pattern, msg.content, re.DOTALL)
#
#     if match:
#         (
#             activity_name,
#             activity_time,
#             activity_duration,
#             activity_location,
#             activity_qq,
#             activity_type,
#             activity_description,
#         ) = match.groups()
#         activity_description = activity_description.replace("\n", "").strip()
#         info = await check_status(msg.source, status="管理活动修改")
#
#         try:
#             activity_time = jio.parse_time(
#                 activity_time, time_base=time.time(), time_type="time_point"
#             )
#             if (
#                 activity_time["type"] == "time_point"
#                 or activity_time["type"] == "time_span"
#             ):
#                 activity_time = activity_time["time"][0]
#             else:
#                 Msg(
#                     robot="LR5921",
#                     kind=f"{kind}发送文本",
#                     event="发送",
#                     source=msg.source,
#                     seq=msg.seq,
#                     content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#                     group=msg.group,
#                 )
#                 return
#         except ValueError:
#             Msg(
#                 robot="LR5921",
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#                 group=msg.group,
#             )
#             return
#         try:
#             activity_duration = jio.parse_time(
#                 activity_duration, time_base=time.time(), time_type="time_delta"
#             )
#             if activity_duration["type"] == "time_delta":
#                 activity_duration = activity_duration["time"]
#             else:
#                 activity_duration = "待定"
#         except ValueError:
#             activity_duration = "待定"
#
#         qq = await edit_activity_all(
#             info,
#             activity_name,
#             activity_time,
#             json.dumps(activity_duration),
#             activity_location,
#             activity_description,
#             activity_type,
#             activity_qq,
#         )
#         if not qq:
#             raise Exception(f"未找到活动 id -> 活动修改 | 消息 id: {info}")
#         # 简介换行
#         wrapped_description = wrap_text(activity_description.strip())
#         # 时间输出
#         wrapped_time, wrapped_duration = chinese_time(activity_time, activity_duration)
#
#         new_content = (
#             "\n===========活动信息===========\n"
#             "\n"
#             f"名称: {activity_time}\n"
#             f"时间: {wrapped_time}\n"
#             f"时长: {wrapped_duration}\n"
#             f"地点: {activity_location}\n"
#             f"主持: {activity_qq}\n"
#             f"类型: {activity_type}\n"
#             "简介:\n"
#             f"{wrapped_description}\n"
#             "\n"
#             "========活动已成功修改========\n"
#         )
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content=new_content,
#             group=msg.group,
#         )
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=qq,
#             seq=msg.seq,
#             content="活动审核成功",
#             group=msg.group,
#         )
#         await delete_status(msg.source, "管理活动修改")
#         await delete_status(qq, "活动添加")
#     else:
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="活动审核修改格式错误，请完整复制之前的文字",
#             group=msg.group,
#         )
#
#
# async def activity_add_group(msg: Msg):
#     """添加活动群聊二维码"""
#     kind = msg.kind[:2]
#     activities = await get_activity_msg_id(msg.source)
#     activity_id = ""
#     activity_name = ""
#     for activity in activities:
#         if activity["status"] == "待审核":
#             activity_id = activity["id"]
#             activity_name = activity["name"]
#             break
#     if not activity_id:
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="不存在审核中的活动",
#             group=msg.group,
#         )
#     file_path = path / f"storage/file/activity/{activity_id}.png"
#     await download_file(file_path, msg.files[0][1])
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content="群聊二维码添加成功",
#         group=msg.group,
#     )
#     await asyncio.sleep(10)
#     for admin in config["私聊"]["活动管理员"]:
#         await add_status(admin, "管理活动群聊添加", activity_id)
#         Msg(
#             robot="LR5921",
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=admin,
#             seq=msg.seq,
#             content=f"活动{activity_name}的群聊图片，长按回复确认或删除",
#             group=msg.group,
#             files=[f"{activity_id}.png", file_path],
#         )
#
#
# async def activity_edit(msg: Msg):
#     """社员修改活动信息"""
#     kind = msg.kind[:2]
#     activities = await query_activity(msg.source, ["待审核", "进行中"])
#     content = "\n========复制整段并发送========\n"
#     for activity in activities:
#         activity_id = activity["id"]
#         activity_name = activity["name"]
#         activity_time = activity["time"]
#         activity_duration = json.loads(activity["duration"])
#         activity_location = activity["location"]
#         activity_host = activity["host"]
#         activity_description = activity["description"]
#         activity_type = activity.get("type", "待管理添加")
#         wrapped_description = wrap_text(activity_description.strip())
#         wrapped_time, wrapped_duration = chinese_time(activity_time, activity_duration)
#         content += (
#             f"\n===========活动{activity_id}===========\n"
#             "\n"
#             f"名称: {activity_name}\n"
#             f"时间: {wrapped_time}\n"
#             f"时长: {wrapped_duration}\n"
#             f"地点: {activity_location}\n"
#             f"主持: {activity_host}\n"
#             f"类型: {activity_type}\n"
#             "简介:\n"
#             f"{wrapped_description}\n"
#             "\n"
#             "========修改后发送此段========\n"
#         )
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content=content,
#         group=msg.group,
#     )
#
#
# async def activity_edit_check(msg: Msg):
#     """用户修改活动"""
#     kind = msg.kind[:2]
#     pattern = (
#         r"===========活动(\d+)?===========\n\n"
#         r"名称:\s*(.*?)\n"
#         r"时间:\s*(.*?)\n"
#         r"时长:\s*(.*?)\n"
#         r"地点:\s*(.*?)\n"
#         r"主持:\s*(.*?)\n"
#         r"类型:\s*(.*?)\n"
#         r"简介:\s*([^=]*)"  # 捕获简介直到下一个'='出现
#     )
#     match = re.search(pattern, msg.content, re.DOTALL)
#
#     if match:
#         (
#             activity_id,
#             activity_name,
#             activity_time,
#             activity_duration,
#             activity_location,
#             activity_qq,
#             activity_type,
#             activity_description,
#         ) = match.groups()
#         activity_description = activity_description.replace("\n", "").strip()
#         info = await check_status(msg.source, status="活动添加")
#         if info != activity_id:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="当前有其他审核事项，请等待当前事项审核完成",
#                 group=msg.group,
#             )
#             return
#         try:
#             activity_time = jio.parse_time(
#                 activity_time, time_base=time.time(), time_type="time_point"
#             )
#             if (
#                 activity_time["type"] == "time_point"
#                 or activity_time["type"] == "time_span"
#             ):
#                 activity_time = activity_time["time"][0]
#             else:
#                 Msg(
#                     robot=msg.robot,
#                     kind=f"{kind}发送文本",
#                     event="发送",
#                     source=msg.source,
#                     seq=msg.seq,
#                     content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#                     group=msg.group,
#                 )
#                 return
#         except ValueError:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="活动时间格式错误，请不要使用.来描述时间，xxh来描述时长",
#                 group=msg.group,
#             )
#             return
#         try:
#             activity_duration = jio.parse_time(
#                 activity_duration, time_base=time.time(), time_type="time_delta"
#             )
#             if activity_duration["type"] == "time_delta":
#                 activity_duration = activity_duration["time"]
#             else:
#                 activity_duration = "待定"
#         except ValueError:
#             activity_duration = "待定"
#
#         qq = await edit_activity_all(
#             info,
#             activity_name,
#             activity_time,
#             json.dumps(activity_duration),
#             activity_location,
#             activity_description,
#             activity_type,
#             activity_qq,
#         )
#         if not qq:
#             Msg(
#                 robot=msg.robot,
#                 kind=f"{kind}发送文本",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 content="请勿修改活动序号！",
#                 group=msg.group,
#             )
#             return
#         # 简介换行
#         wrapped_description = wrap_text(activity_description.strip())
#         # 时间输出
#         wrapped_time, wrapped_duration = chinese_time(activity_time, activity_duration)
#
#         new_content = (
#             "\n===========活动信息===========\n"
#             "\n"
#             f"名称: {activity_time}\n"
#             f"时间: {wrapped_time}\n"
#             f"时长: {wrapped_duration}\n"
#             f"地点: {activity_location}\n"
#             f"主持: {activity_qq}\n"
#             f"类型: {activity_type}\n"
#             "简介:\n"
#             f"{wrapped_description}\n"
#             "\n"
#             "========活动已成功修改========\n"
#         )
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content=new_content,
#             group=msg.group,
#         )
#     else:
#         Msg(
#             robot=msg.robot,
#             kind=f"{kind}发送文本",
#             event="发送",
#             source=msg.source,
#             seq=msg.seq,
#             content="活动审核修改格式错误，请完整复制之前的文字",
#             group=msg.group,
#         )
#
#
# async def activity_attend(msg: Msg):
#     """添加活动参与者"""
#     kind = msg.kind[:2]
#     activities = await query_activity(msg.source, ["进行中"])
#     content = "\n========发序号和参与者========\n"
#     for activity in activities:
#         task_id = activity["id"]
#         task_name = activity["name"]
#         task_time = activity["time"]
#         task_duration = json.loads(activity["duration"])
#         task_location = activity["location"]
#         task_host = activity["host"]
#         task_description = activity["description"]
#         task_activity_type = activity.get("type", "待管理添加")
#         wrapped_description = wrap_text(task_description.strip())
#         wrapped_time, wrapped_duration = chinese_time(task_time, task_duration)
#         content += (
#             f"\n===========活动{task_id}===========\n"
#             "\n"
#             f"名称: {task_name}\n"
#             f"时间: {wrapped_time}\n"
#             f"时长: {wrapped_duration}\n"
#             f"地点: {task_location}\n"
#             f"主持: {task_host}\n"
#             f"类型: {task_activity_type}\n"
#             "简介:\n"
#             f"{wrapped_description}\n"
#             "\n"
#             "========不用来复制此段========\n"
#         )
#     content += "格式为\n/活动参与,20,a,b,c"
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content=content,
#         group=msg.group,
#     )
#
#
# async def activity_query(msg: Msg):
#     """查询活动，查询历史活动，查询指定条件活动"""
#     kind = msg.kind[:2]
#     content = re.sub(r"/活动查询[,，]?", "", msg.content).strip()
#     if not content:
#         activities = await query_activity("", ["进行中"])
#     elif content == "历史":
#         activities = await query_activity("", ["进行中", "已结束"])
#     else:
#         activities = await query_activity(content, ["进行中"])
#
#     # 检查是否有活动
#     if activities:
#         activities_info = ""
#         for activity in activities:
#             task_name = activity["name"]
#             task_time = activity["time"]
#             task_duration = json.loads(activity["duration"])
#             task_location = activity["location"]
#             task_host = activity["qq"]
#             task_description = activity["description"]
#             task_activity_type = activity.get("type", "待管理添加")
#             wrapped_description = wrap_text(task_description.strip())
#             wrapped_time, wrapped_duration = chinese_time(task_time, task_duration)
#             activities_info += (
#                 "\n===========活动信息===========\n"
#                 f"活动名称: {task_name}\n"
#                 f"活动时间: {wrapped_time}\n"
#                 f"活动时长: {wrapped_duration}\n"
#                 f"活动地点: {task_location}\n"
#                 f"主持人: {task_host}\n"
#                 f"类型: {task_activity_type}\n"
#                 "简介:\n"
#                 f"{wrapped_description}\n"
#                 f"===================\n"
#             )
#         content = activities_info
#     else:
#         content = "未查询到任何符合条件的活动。"
#
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content=content,
#         group=msg.group,
#     )
