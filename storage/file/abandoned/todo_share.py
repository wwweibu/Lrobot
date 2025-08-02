from message.handler.msg import Msg


# TODO 更新小程序后修改内容、发送方式
# async def share_app(msg: Msg):
#     kind = msg.kind[:2]
#     content = [
#         {
#             "type": "json",
#             "data": {
#                 "data": '{"app":"com.tencent.miniapp_01","desc":"","view":"view_8C8E89B49BE609866298ADDFF2DBABA4",'
#                 '"bizsrc":"","ver":"1.0.0.19","prompt":"[QQ小程序]","appID":"","sourceName":"","actionData":"",'
#                 '"actionData_A":"","sourceUrl":"","meta":{"detail_1":{"appid":"1112322667","appType":0,'
#                 '"title":"武大推协社团物资租借","desc":"",'
#                 '"icon":"https:\\/\\/miniapp.gtimg.cn\\/public\\/appicon\\/f3705e7de1bad89bb65da0b290e65575_200'
#                 '.jpg","preview":"https:\\/\\/pubminishare-30161.picsz.qpic.cn\\/2dea7f65-514d-4662-8634'
#                 '-d57a8570c355","url":"m.q.qq.com\\/a\\/s\\/007b0aa0f354d5b7f91da7a05f607a13","scene":0,'
#                 '"host":{"uin":663748426,"nick":"令狐二中"},"shareTemplateId":"8C8E89B49BE609866298ADDFF2DBABA4",'
#                 '"shareTemplateData":{},"showLittleTail":"","gamePoints":"","gamePointsUrl":"","shareOrigin":0}},'
#                 '"config":{"type":"normal","width":0,"height":0,"forward":1,"autoSize":0,"ctime":1729577825,'
#                 '"token":"faae3a587823165a579f89c966f80cc9"},"text":"","extraApps":[],"sourceAd":"","extra":""}'
#             },
#         }
#     ]
#     Msg(
#         robot=msg.robot,
#         kind=f"{kind}发送文本",
#         event="发送",
#         source=msg.source,
#         seq=msg.seq,
#         content=content,
#         group=msg.group,
#     )
