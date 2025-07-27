# TODO 改成 Agent 后处理
# import os
#
# from logic import data
# from config import path,loggers
# from message.handler.msg import Msg
#
#
# msg_logger = loggers["message"]
#
# def is_qrcode_image(image_path):
#     if image_path.lower().endswith(".gif"):
#         with Image.open(image_path) as img:
#             new_image_path = os.path.splitext(image_path)[0] + ".png"
#             img.convert("RGB").save(new_image_path)
#             image_path = new_image_path
#     img = cv2.imread(image_path)
#     if img is None:
#         return False
#
#     barcodes = zxingcpp.read_barcodes(img)
#     if len(barcodes) == 0:
#         return False
#
#     for barcode in barcodes:
#         msg_logger.info(
#             f"⌈LR5921⌋二维码检测 -> Text:'{barcode.text}' Format:'{barcode.format}' Content:'{barcode.content_type}' Position:'{barcode.position}'", extra={"event": "消息处理"}
#         )
#     return True
#
#
# async def withdraw_qrcode(msg:Msg):
#     for file in msg.files:
#         file_path = path / f"storage/file/users/{msg.source}/二维码{file[0]}"
#         await data.download_file(file_path, file[1])
#         if is_qrcode_image(str(file_path)):
#             Msg(
#                 robot=msg.robot,
#                 kind=f"群聊撤回消息",
#                 event="发送",
#                 source=msg.source,
#                 seq=msg.seq,
#                 group=msg.group,
#             )
