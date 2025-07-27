# LR232 消息格式

---
# 消息接收
## 验证消息
#### 回调验证 
```
{
    "d": {"plain_token": "oeFQcoqScE5sMT078N1J", "event_ts": "1739431127"},
    "op": 13,
}
```

## 普通消息
#### 私聊图片 
```
{
    "op": 0,
    "id": "C2C_MESSAGE_CREATE:o87gxm4ehyludnpeniqsbxuqtddoh9dixtehialxfuohchhcigml0xmisoz2",
    "d": {
        "id": "ROBOT1.0_YVzTU7YSOT5lDwl..a9qHIE9dmbeOnIa8htmw65.plUjarnep2VtBmgwh4JWmBlBWJVB8Ei-356O9DOFQyISCg!!",
        "content": "",
        "timestamp": "2025-02-15T16:32:42+08:00",
        "author": {
            "id": "7D296480D464EC5C16714E74A43E5BC7",
            "user_openid": "7D296480D464EC5C16714E74A43E5BC7",
            "union_openid": "7D296480D464EC5C16714E74A43E5BC7",
        },
        "attachments": [
            {
                "url": "https://multimedia.nt.qq.com.cn/download?appid=1406&fileid=EhSCDbrMCGYv504w8Awvml7QIbY4uRjbpAMg_goo2-_4k6LFiwMyBHByb2RaEMgOTLmSn0zCEWu1FKQVcxY&rkey=CAMSKIoMrO0nej4OY6dtO-Iyi1nN7QA8u0wIg4KryEbBDjk3kGouR40xtnU&spec=0",
                "filename": "B43A0CF83A2D80BBEFBB9C566FEE436F.jpg",
                "width": 520,
                "height": 524,
                "size": 53851,
                "content_type": "image/jpeg",
                "content": "",
            }
        ],
        "message_scene": {"source": "default", "callback_data": ""},
    },
    "t": "C2C_MESSAGE_CREATE",
}
```

#### 好友卡片
```
{
    "op": 0,
    "id": "C2C_MESSAGE_CREATE:9ixa3f8z7eyirxbob6jcxnozplu78he9ta3ridrtohpfuohchhcigml0xmisoz2",
    "d": {
        "id": "ROBOT1.0_YVzTU7YSOT5lDwl..a9qHDoXrSodopMFoddkRdYCtnkCWikTayQG9PmaDE0dZhvOjoPzoiAec0gi5cXfaox4ugjlj6H3wBCAbx3PilKrAso!",
        "content": "",
        "timestamp": "2025-07-12T16:44:45+08:00",
        "author": {
            "id": "7D296480D464EC5C16714E74A43E5BC7",
            "user_openid": "7D296480D464EC5C16714E74A43E5BC7",
            "union_openid": "7D296480D464EC5C16714E74A43E5BC7",
        },
        "message_scene": {
            "source": "default",
            "ext": ["msg_idx=REFIDX_COGnAhD9wMjDBhjK/r+8Ag=="],
        },
        "message_type": 3,
    },
    "t": "C2C_MESSAGE_CREATE",
}
```

#### 群聊消息
```
{
    "op": 0,
    "id": "GROUP_AT_MESSAGE_CREATE:dplmss1ni5jdxvhqmsablrwi16gnqpxgg9ecoamsg9xqkgxwpynhysl6q6ws849",
    "d": {
        "id": "ROBOT1.0_DPLMsS1ni5JdXvHqMSAbLhCWDXkR.ypJfF8MMAvV1o.nJ6EAnAE5kMg2FFFnMSNfcCPxLSoIMEzLwfEp0kRuhQjlj6H3wBCAbx3PilKrAso!",
        "content": " 123",
        "timestamp": "2025-02-15T16:35:23+08:00",
        "author": {
            "id": "7D296480D464EC5C16714E74A43E5BC7",
            "member_openid": "7D296480D464EC5C16714E74A43E5BC7",
            "union_openid": "7D296480D464EC5C16714E74A43E5BC7",
        },
        "group_id": "D4DE5F2EF86365A1FBEAA8C7C3C12B91",
        "group_openid": "D4DE5F2EF86365A1FBEAA8C7C3C12B91",
        "message_scene": {"source": "default", "callback_data": ""},
    },
    "t": "GROUP_AT_MESSAGE_CREATE",
}
```

## 事件消息
#### 关闭消息推送 
```
{
    "op": 0,
    "id": "C2C_MSG_REJECT:da8f64c2-7cde-4dc7-94f1-6813efbda797",
    "d": {"timestamp": 1741878278, "openid": "7D296480D464EC5C16714E74A43E5BC7"},
    "t": "C2C_MSG_REJECT",
}
```

#### 开启消息推送 
```
{
    "op": 0,
    "id": "C2C_MSG_RECEIVE:f296a5b6-4111-4df4-b828-2f7b8226a401",
    "d": {"timestamp": 1741878735, "openid": "7D296480D464EC5C16714E74A43E5BC7"},
    "t": "C2C_MSG_RECEIVE",
}
```

#### 好友删除 
```
{
    "op": 0,
    "id": "FRIEND_DEL:e1f1f790-43ce-4249-8e81-f7df496deff1",
    "d": {
        "timestamp": 1741879562,
        "openid": "7D296480D464EC5C16714E74A43E5BC7",
        "author": {"union_openid": "7D296480D464EC5C16714E74A43E5BC7"},
    },
    "t": "FRIEND_DEL",
}
```

#### 好友添加 
```
{
    "op": 0,
    "id": "FRIEND_ADD:ec2769d0-f3d5-4315-a000-3d8e6fa4a0d4",
    "d": {
        "timestamp": 1741879599,
        "openid": "7D296480D464EC5C16714E74A43E5BC7",
        "author": {"union_openid": "7D296480D464EC5C16714E74A43E5BC7"},
    },
    "t": "FRIEND_ADD",
}
```

#### 加入群聊 
```
{
    "op": 0,
    "id": "GROUP_ADD_ROBOT:56d7a1f4-a7f7-4e96-9ca4-fa5ba6697ddf",
    "d": {
        "timestamp": 1741880682,
        "group_openid": "492C3C6EC6630BD6DD71A32074BDB2F9",
        "op_member_openid": "7D296480D464EC5C16714E74A43E5BC7",
    },
    "t": "GROUP_ADD_ROBOT",
}
```

#### 退出群聊 
```
{
    "op": 0,
    "id": "GROUP_DEL_ROBOT:bcffb8e4-693c-4e81-bf34-d5653f3dd781",
    "d": {
        "timestamp": 1741880615,
        "group_openid": "492C3C6EC6630BD6DD71A32074BDB2F9",
        "op_member_openid": "7D296480D464EC5C16714E74A43E5BC7",
    },
    "t": "GROUP_DEL_ROBOT",
}
```

#### 关闭群消息 
```
{
    "op": 0,
    "id": "GROUP_MSG_REJECT:92a270a2-91ba-4807-a6aa-dabd47eefeca",
    "d": {
        "timestamp": 1741880868,
        "group_openid": "492C3C6EC6630BD6DD71A32074BDB2F9",
        "op_member_openid": "7D296480D464EC5C16714E74A43E5BC7",
    },
    "t": "GROUP_MSG_REJECT",
}
```

#### 开启群消息 
```
{
    "op": 0,
    "id": "GROUP_MSG_RECEIVE:86adfa8d-59b1-4454-ac5c-c9bcac78184d",
    "d": {
        "timestamp": 1741880888,
        "group_openid": "492C3C6EC6630BD6DD71A32074BDB2F9",
        "op_member_openid": "7D296480D464EC5C16714E74A43E5BC7",
    },
    "t": "GROUP_MSG_RECEIVE",
}
```

## 返回消息
#### 发送失败 
```
{
    "message": "请求参数event_id对应事件不能回复消息",
    "code": 40034027,
    "err_code": 40034027,
    "trace_id": "12c7dfb902497f6b211c1d3c8a6a9d42",
}
```
####  发送成功 
```
{
    "id":"ROBOT1.0_-vh8GQMXamm82CP8NyBAyAMnXBZgzqfB5m7T-NJ1LZfB-93hxA47spViToX6-JLx6a778A74yX2PnVj6vlAX4A!!"
    "timestamp":"2025-03-13T23:30:49+08:00"
}
```

 {'op': 0, 'id': 'C2C_MESSAGE_CREATE:9ixa3f8z7eyirxbob6jcxnozplu78he9ta3ridrtohpfuohchhcigml0xmisoz2', 'd': {'id': 'ROBOT1.0_YVzTU7YSOT5lDwl..a9qHDoXrSodopMFoddkRdYCtnkCWikTayQG9PmaDE0dZhvOjoPzoiAec0gi5cXfaox4ugjlj6H3wBCAbx3PilKrAso!', 'content': '', 'timestamp': '2025-07-12T16:44:45+08:00', 'author': {'id': '7D296480D464EC5C16714E74A43E5BC7', 'user_openid': '7D296480D464EC5C16714E74A43E5BC7', 'union_openid': '7D296480D464EC5C16714E74A43E5BC7'}, 'message_scene': {'source': 'default', 'ext': ['msg_idx=REFIDX_COGnAhD9wMjDBhjK/r+8Ag==']}, 'message_type': 3}, 't': 'C2C_MESSAGE_CREATE'}

---
# 消息发送
## test.py
- 发送文字消息（私聊/群聊）
- 发送图片消息（私聊/群聊）
- 重复发送消息（私聊/群聊）
- 发送视频消息（10MB 就会上传失败）
- 消息撤回（私聊/群聊）

## welcome.py
- 群聊添加、群聊/好友开启消息推送均能根据事件 id 回复消息，但 1 天内只能回复 1 次

## 无法使用
- 好友添加/删除、群聊删除、群聊/好友关闭消息推送均不能回复消息
- 发送文件消息（无法使用）
- 消息引用（无法使用） （msg_reference 使用 id、返回的 dict 均不行
- 发送 ark 消息（无权限）
- 发送 markdown 消息（无被动发送权限）
- 发送 embed 消息（群聊/私聊未开放）
- 发送群聊 @ 消息（无法使用）（两种方法均未测试成功）
- 发送表情（无法使用）（未测试成功）

## 其他参考
- 文件接收可以接收所有类型文件（与文档中不一致）
- 发送语音消息（MP3转silk脚本），手机可以播放，电脑播放不了
- 解析表情（存在于表情商城中的表情，即便收藏中也一样）
- 商城表情 <faceType=4,faceId="",ext="eyJ0ZXh0IjoiW+mFt10ifQ==">
- 普通表情 <faceType=1,faceId="277",ext="eyJ0ZXh0Ijoi5rGq5rGqIn0=">

#### 推荐联系人字段解析
由于 records.elements.xxxxElement 字段不固定，故不解析
```
{
    "self_id": 3502644244,
    "user_id": 663748426,
    "time": 1752310516,
    "message_id": 1018006251,
    "message_seq": 1018006251,
    "real_id": 1018006251,
    "real_seq": "5378",
    "message_type": "private",
    "sender": {"user_id": 663748426, "nickname": "令狐二中", "card": ""},
    "raw_message": "[CQ:reply,id=527004916]111",
    "font": 14,
    "sub_type": "friend",
    "message": [
        {"type": "reply", "data": {"id": "527004916"}},
        {"type": "text", "data": {"text": "111"}},
    ],
    "message_format": "array",
    "post_type": "message",
    "target_id": 663748426,
    "raw": {
        "msgId": "7526116358751577877",
        "msgRandom": "435307650",
        "msgSeq": "5378",
        "cntSeq": "0",
        "chatType": 1,
        "msgType": 9,
        "subMsgType": 33,
        "sendType": 0,
        "senderUid": "u_-LwnI9ZCFS_HIOOaRJL58Q",
        "peerUid": "u_-LwnI9ZCFS_HIOOaRJL58Q",
        "channelId": "",
        "guildId": "",
        "guildCode": "0",
        "fromUid": "0",
        "fromAppid": "0",
        "msgTime": "1752310516",
        "msgMeta": {},
        "sendStatus": 2,
        "sendRemarkName": "",
        "sendMemberName": "",
        "sendNickName": "",
        "guildName": "",
        "channelName": "",
        "elements": [
            {
                "elementType": 7,
                "elementId": "7526116358751577871",
                "elementGroupId": 0,
                "extBufForUI": {},
                "textElement": None,
                "faceElement": None,
                "marketFaceElement": None,
                "replyElement": {
                    "replayMsgId": "0",
                    "replayMsgSeq": "5376",
                    "replayMsgRootSeq": "0",
                    "replayMsgRootMsgId": "0",
                    "replayMsgRootCommentCnt": "0",
                    "sourceMsgIdInRecords": "7526116358751577878",
                    "sourceMsgText": "",
                    "sourceMsgTextElems": [
                        {
                            "replyAbsElemType": 1,
                            "textElemContent": "推荐联系人：暗世现",
                            "faceElem": None,
                            "picElem": None,
                        }
                    ],
                    "senderUid": "663748426",
                    "senderUidStr": "u_-LwnI9ZCFS_HIOOaRJL58Q",
                    "replyMsgClientSeq": "30294",
                    "replyMsgTime": "1752310206",
                    "replyMsgRevokeType": 0,
                    "sourceMsgIsIncPic": False,
                    "sourceMsgExpired": False,
                    "anonymousNickName": None,
                    "originalMsgState": None,
                },
                "picElement": None,
                "pttElement": None,
                "videoElement": None,
                "grayTipElement": None,
                "arkElement": None,
                "fileElement": None,
                "liveGiftElement": None,
                "markdownElement": None,
                "structLongMsgElement": None,
                "multiForwardMsgElement": None,
                "giphyElement": None,
                "walletElement": None,
                "inlineKeyboardElement": None,
                "textGiftElement": None,
                "calendarElement": None,
                "yoloGameResultElement": None,
                "avRecordElement": None,
                "structMsgElement": None,
                "faceBubbleElement": None,
                "shareLocationElement": None,
                "tofuRecordElement": None,
                "taskTopMsgElement": None,
                "recommendedMsgElement": None,
                "actionBarElement": None,
                "prologueMsgElement": None,
                "forwardMsgElement": None,
            },
            {
                "elementType": 1,
                "elementId": "7526116358751577876",
                "elementGroupId": 0,
                "extBufForUI": {},
                "textElement": {
                    "content": "111",
                    "atType": 0,
                    "atUid": "0",
                    "atTinyId": "0",
                    "atNtUid": "",
                    "subElementType": 0,
                    "atChannelId": "0",
                    "linkInfo": None,
                    "atRoleId": "0",
                    "atRoleColor": 0,
                    "atRoleName": "",
                    "needNotify": 0,
                },
                "faceElement": None,
                "marketFaceElement": None,
                "replyElement": None,
                "picElement": None,
                "pttElement": None,
                "videoElement": None,
                "grayTipElement": None,
                "arkElement": None,
                "fileElement": None,
                "liveGiftElement": None,
                "markdownElement": None,
                "structLongMsgElement": None,
                "multiForwardMsgElement": None,
                "giphyElement": None,
                "walletElement": None,
                "inlineKeyboardElement": None,
                "textGiftElement": None,
                "calendarElement": None,
                "yoloGameResultElement": None,
                "avRecordElement": None,
                "structMsgElement": None,
                "faceBubbleElement": None,
                "shareLocationElement": None,
                "tofuRecordElement": None,
                "taskTopMsgElement": None,
                "recommendedMsgElement": None,
                "actionBarElement": None,
                "prologueMsgElement": None,
                "forwardMsgElement": None,
            },
        ],
        "records": [
            {
                "msgId": "7526116358751577878",
                "msgRandom": "1315653190",
                "msgSeq": "5376",
                "cntSeq": "0",
                "chatType": 1,
                "msgType": 11,
                "subMsgType": 0,
                "sendType": 0,
                "senderUid": "u_-LwnI9ZCFS_HIOOaRJL58Q",
                "peerUid": "u_-LwnI9ZCFS_HIOOaRJL58Q",
                "channelId": "",
                "guildId": "",
                "guildCode": "0",
                "fromUid": "0",
                "fromAppid": "0",
                "msgTime": "1752310206",
                "msgMeta": {},
                "sendStatus": 2,
                "sendRemarkName": "21－策划副会－微步",
                "sendMemberName": "",
                "sendNickName": "令狐二中",
                "guildName": "",
                "channelName": "",
                "elements": [
                    {
                        "elementType": 10,
                        "elementId": "7526116358751577879",
                        "elementGroupId": 0,
                        "extBufForUI": {},
                        "textElement": None,
                        "faceElement": None,
                        "marketFaceElement": None,
                        "replyElement": None,
                        "picElement": None,
                        "pttElement": None,
                        "videoElement": None,
                        "grayTipElement": None,
                        "arkElement": {
                            "bytesData": '{"app":"com.tencent.contact.lua","desc":"","view":"contact","bizsrc":"cardshare.cardshare","ver":"0.0.0.1","prompt":"推荐联系人：暗世现","appID":"","sourceName":"","actionData":"","actionData_A":"","sourceUrl":"","meta":{"contact":{"avatar":"http:\\/\\/thirdqq.qlogo.cn\\/g?b=oidb&k=c9w219ezS31icWibibypWcpicg&kti=aHIhgxHhVOI&s=140","nickname":"暗世现","contact":"账号：1049509241","tag":"推荐好友","tagIcon":null,"jumpUrl":"mqqapi:\\/\\/card\\/show_pslcard?src_type=internal&source=sharecard&version=1&uin=1049509241"}},"config":{"autosize":0,"collect":1,"ctime":1752310147,"forward":0,"height":225,"reply":1,"round":1,"token":"16c68e531a06192938603845d0051884","type":"normal","width":526},"text":"","extraApps":[],"sourceAd":"","extra":""}',
                            "linkInfo": None,
                            "subElementType": None,
                            "buildMultiMsgReqInfo": None,
                        },
                        "fileElement": None,
                        "liveGiftElement": None,
                        "markdownElement": None,
                        "structLongMsgElement": None,
                        "multiForwardMsgElement": None,
                        "giphyElement": None,
                        "walletElement": None,
                        "inlineKeyboardElement": None,
                        "textGiftElement": None,
                        "calendarElement": None,
                        "yoloGameResultElement": None,
                        "avRecordElement": None,
                        "structMsgElement": None,
                        "faceBubbleElement": None,
                        "shareLocationElement": None,
                        "tofuRecordElement": None,
                        "taskTopMsgElement": None,
                        "recommendedMsgElement": None,
                        "actionBarElement": None,
                        "prologueMsgElement": None,
                        "forwardMsgElement": None,
                    }
                ],
                "records": [],
                "emojiLikesList": [],
                "commentCnt": "0",
                "directMsgFlag": 0,
                "directMsgMembers": [],
                "peerName": "",
                "freqLimitInfo": None,
                "editable": False,
                "avatarMeta": "",
                "avatarPendant": "",
                "feedId": "",
                "roleId": "0",
                "timeStamp": "0",
                "clientIdentityInfo": None,
                "isImportMsg": False,
                "atType": 0,
                "roleType": 0,
                "fromChannelRoleInfo": {"roleId": "0", "name": "", "color": 0},
                "fromGuildRoleInfo": {"roleId": "0", "name": "", "color": 0},
                "levelRoleInfo": {"roleId": "0", "name": "", "color": 0},
                "recallTime": "0",
                "isOnlineMsg": False,
                "generalFlags": {},
                "clientSeq": "30294",
                "fileGroupSize": None,
                "foldingInfo": None,
                "multiTransInfo": None,
                "senderUin": "663748426",
                "peerUin": "663748426",
                "msgAttrs": {},
                "anonymousExtInfo": None,
                "nameType": 0,
                "avatarFlag": 0,
                "extInfoForUI": None,
                "personalMedal": None,
                "categoryManage": 0,
                "msgEventInfo": None,
                "sourceType": 0,
            }
        ],
        "emojiLikesList": [],
        "commentCnt": "0",
        "directMsgFlag": 0,
        "directMsgMembers": [],
        "peerName": "",
        "freqLimitInfo": None,
        "editable": False,
        "avatarMeta": "",
        "avatarPendant": "",
        "feedId": "",
        "roleId": "0",
        "timeStamp": "0",
        "clientIdentityInfo": None,
        "isImportMsg": False,
        "atType": 0,
        "roleType": 0,
        "fromChannelRoleInfo": {"roleId": "0", "name": "", "color": 0},
        "fromGuildRoleInfo": {"roleId": "0", "name": "", "color": 0},
        "levelRoleInfo": {"roleId": "0", "name": "", "color": 0},
        "recallTime": "0",
        "isOnlineMsg": True,
        "generalFlags": {},
        "clientSeq": "39213",
        "fileGroupSize": None,
        "foldingInfo": None,
        "multiTransInfo": None,
        "senderUin": "663748426",
        "peerUin": "663748426",
        "msgAttrs": {},
        "anonymousExtInfo": None,
        "nameType": 0,
        "avatarFlag": 0,
        "extInfoForUI": None,
        "personalMedal": None,
        "categoryManage": 0,
        "msgEventInfo": None,
        "sourceType": 1,
        "id": 1018006251,
    },
}
```