# LR5921 消息格式

---
# 消息接收
## meta_event 事件

## message 事件
#### 私聊临时 
```
{
    "self_id": 3502644244,
    "user_id": 2973907990,
    "time": 1742288608,
    "message_id": 684841211,
    "message_seq": 684841211,
    "real_id": 684841211,
    "message_type": "private",
    "sender": {"user_id": 2973907990, "nickname": "临时会话", "card": ""},
    "raw_message": "123",
    "font": 14,
    "sub_type": "group",
    "message": [{"type": "text", "data": {"text": "123"}}],
    "message_format": "array",
    "post_type": "message",
    "group_id": 736368697,
    "temp_source": 736368697,
    "target_id": 2973907990,
}
```

#### 私聊图片 
```
{
    "self_id": 3502644244,
    "user_id": 2973907990,
    "time": 1742288632,
    "message_id": 124840880,
    "message_seq": 124840880,
    "real_id": 124840880,
    "message_type": "private",
    "sender": {"user_id": 2973907990, "nickname": "临时会话", "card": ""},
    "raw_message": "[CQ:image,file=F22633C1A85FA6D6CACC65062B6E9802.jpg,sub_type=0,url=https://multimedia.nt.qq.com.cn/download?appid=1406&amp;fileid=EhQhmXWjubqCMGIWXCUiICYse3pikxit-AIg_gooypXo96KTjAMyBHByb2RQgLsvWhBym1liJNJjV1Uq1nhAZh4r&amp;rkey=CAQSKAB6JWENi5LMvyxtRnp4-uPI-a8INjp3xXZMbOleZkOU5Z--9rE42bA,file_size=48173]",
    "font": 14,
    "sub_type": "group",
    "message": [
        {
            "type": "image",
            "data": {
                "summary": "",
                "file": "F22633C1A85FA6D6CACC65062B6E9802.jpg",
                "sub_type": 0,
                "url": "https://multimedia.nt.qq.com.cn/download?appid=1406&fileid=EhQhmXWjubqCMGIWXCUiICYse3pikxit-AIg_gooypXo96KTjAMyBHByb2RQgLsvWhBym1liJNJjV1Uq1nhAZh4r&rkey=CAQSKAB6JWENi5LMvyxtRnp4-uPI-a8INjp3xXZMbOleZkOU5Z--9rE42bA",
                "file_size": "48173",
            },
        }
    ],
    "message_format": "array",
    "post_type": "message",
    "group_id": 736368697,
    "temp_source": 736368697,
    "target_id": 2973907990,
}
```

#### 群聊表情图片 
```
{
    "self_id": 3502644244,
    "user_id": 663748426,
    "time": 1742288684,
    "message_id": 1393408316,
    "message_seq": 1393408316,
    "real_id": 1393408316,
    "message_type": "group",
    "sender": {
        "user_id": 663748426,
        "nickname": "令狐二中",
        "card": "",
        "role": "owner",
    },
    "raw_message": "[CQ:image,summary=&#91;动画表情&#93;,file=085047EFEE35DA8488A735A030BE67A2.jpg,sub_type=1,url=https://multimedia.nt.qq.com.cn/download?appid=1407&amp;fileid=EhTJ94LuHbTlAJ3zaGQzDBUUlNX3Uxihvhwg_woo3OLfkKOTjAMyBHByb2RQgL2jAVoQDPp6maLxH4zyhjmJUcgE8Q&amp;rkey=CAMSKMa3OFokB_TlUslq4eQOUsmPFWzuapCwv8nELPPkYNU9i13AKVfkjoc,file_size=466721]&#91;棒&#93;🔥123",
    "font": 14,
    "sub_type": "normal",
    "message": [
        {
            "type": "image",
            "data": {
                "summary": "[动画表情]",
                "file": "085047EFEE35DA8488A735A030BE67A2.jpg",
                "sub_type": 1,
                "url": "https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=EhTJ94LuHbTlAJ3zaGQzDBUUlNX3Uxihvhwg_woo3OLfkKOTjAMyBHByb2RQgL2jAVoQDPp6maLxH4zyhjmJUcgE8Q&rkey=CAMSKMa3OFokB_TlUslq4eQOUsmPFWzuapCwv8nELPPkYNU9i13AKVfkjoc",
                "file_size": "466721",
            },
        },
        {"type": "text", "data": {"text": "[棒]"}},
        {"type": "text", "data": {"text": "🔥123"}},
    ],
    "message_format": "array",
    "post_type": "message",
    "group_id": 736368697,
}
```

#### 群聊文件 
```
{
    "self_id": 3502644244,
    "user_id": 663748426,
    "time": 1742288726,
    "message_id": 1926650443,
    "message_seq": 1926650443,
    "real_id": 1926650443,
    "message_type": "group",
    "sender": {
        "user_id": 663748426,
        "nickname": "令狐二中",
        "card": "",
        "role": "owner",
    },
    "raw_message": "[CQ:file,file=1.txt,file_id=/be2a7132-8e06-4aab-b3b6-e063d2f98230,file_size=3]",
    "font": 14,
    "sub_type": "normal",
    "message": [
        {
            "type": "file",
            "data": {
                "file": "1.txt",
                "file_id": "/be2a7132-8e06-4aab-b3b6-e063d2f98230",
                "file_size": "3",
            },
        }
    ],
    "message_format": "array",
    "post_type": "message",
    "group_id": 736368697,
}
```

#### 群聊消息回复 
```
{
    "self_id": 3502644244,
    "user_id": 1715912741,
    "time": 1742289880,
    "message_id": 657667707,
    "message_seq": 657667707,
    "real_id": 657667707,
    "message_type": "group",
    "sender": {
        "user_id": xxx,
        "nickname": "xxx",
        "card": "xxx",
        "role": "admin",
    },
    "raw_message": "[CQ:reply,id=1849933061]可以在群里搜“《”，出来的一般都是剧本杀。剧本杀人满很快，你现在搜到的肯定都满了；下次看到书名号的时候不要再一眼当侦探小说了哦",
    "font": 14,
    "sub_type": "normal",
    "message": [
        {"type": "reply", "data": {"id": "1849933061"}},
        {
            "type": "text",
            "data": {
                "text": "可以在群里搜“《”，出来的一般都是剧本杀。剧本杀人满很快，你现在搜到的肯定都满了；下次看到书名号的时候不要再一眼当侦探小说了哦"
            },
        },
    ],
    "message_format": "array",
    "post_type": "message",
    "group_id": 920712228,
}
```

#### 转发消息 
```
{
    "self_id": 3502644244,
    "user_id": 663748426,
    "time": 1742291905,
    "message_id": 348979412,
    "message_seq": 348979412,
    "real_id": 348979412,
    "message_type": "private",
    "sender": {"user_id": 663748426, "nickname": "令狐二中", "card": ""},
    "raw_message": "[CQ:forward,id=7483086758390235084]",
    "font": 14,
    "sub_type": "friend",
    "message": [{"type": "forward", "data": {"id": "7483086758390235084"}}],
    "message_format": "array",
    "post_type": "message",
    "target_id": 663748426,
}
```

## message_sent 事件
#### 私聊临时发送 
```
{
    "self_id": 3502644244,
    "user_id": 3502644244,
    "time": 1742290331,
    "message_id": 21246471,
    "message_seq": 21246471,
    "real_id": 21246471,
    "message_type": "private",
    "sender": {"user_id": 3502644244, "nickname": "临时会话", "card": ""},
    "raw_message": "111",
    "font": 14,
    "sub_type": "group",
    "message": [{"type": "text", "data": {"text": "111"}}],
    "message_format": "array",
    "post_type": "message_sent",
    "message_sent_type": "self",
    "group_id": 284840486,
    "temp_source": 284840486,
    "target_id": 2973907990,
}
```

#### 群聊回复发送 
```
{
    "self_id": 3502644244,
    "user_id": 3502644244,
    "time": 1742290368,
    "message_id": 196158329,
    "message_seq": 196158329,
    "real_id": 196158329,
    "message_type": "group",
    "sender": {
        "user_id": 3502644244,
        "nickname": "LR5921",
        "card": "",
        "role": "member",
    },
    "raw_message": "[CQ:reply,id=466720770][CQ:at,qq=663748426] qqw",
    "font": 14,
    "sub_type": "normal",
    "message": [
        {"type": "reply", "data": {"id": "466720770"}},
        {"type": "at", "data": {"qq": "663748426"}},
        {"type": "text", "data": {"text": " qqw"}},
    ],
    "message_format": "array",
    "post_type": "message_sent",
    "message_sent_type": "self",
    "group_id": 736368697,
    "target_id": 736368697,
}
```

## request 事件


## notice 事件
#### 好友添加 
```
{
    "time": 1742290684,
    "self_id": 3502644244,
    "post_type": "notice",
    "notice_type": "friend_add",
    "user_id": 2973907990,
}
```

#### 私聊消息撤回 
```
{
    "time": 1742290548,
    "self_id": 3502644244,
    "post_type": "notice",
    "notice_type": "friend_recall",
    "user_id": 663748426,
    "message_id": 1800796867,
}
```

#### 群管理员增加 
```
{
    "time": 1742291060,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 2973907990,
    "notice_type": "group_admin",
    "sub_type": "set",
}
```

#### 群管理员减少 
```
{
    "time": 1742291076,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 2973907990,
    "notice_type": "group_admin",
    "sub_type": "unset",
}
```

#### 群聊禁言 
```
{
    "time": 1742291099,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 0,
    "notice_type": "group_ban",
    "operator_id": 663748426,
    "duration": -1,
    "sub_type": "ban",
}
```

#### 群聊解除禁言 
```
{
    "time": 1742291109,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 0,
    "notice_type": "group_ban",
    "operator_id": 663748426,
    "duration": 0,
    "sub_type": "lift_ban",
}
```

#### 群成员减少 
```
{
    "time": 1742291239,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 2973907990,
    "notice_type": "group_decrease",
    "sub_type": "kick",/"leave"
    "operator_id": 0,
}
```

#### 群成员邀请 
```
{
    "time": 1742291292,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 2973907990,
    "notice_type": "group_increase",
    "operator_id": 663748426,
    "sub_type": "invite",/approve
}
```

#### 群消息撤回 （自己撤回和管理员撤回）
```
{
    "time": 1742291573,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 2973907990,
    "notice_type": "group_recall",
    "operator_id": 2973907990,
    "message_id": 91436376,
}
```

#### 群聊文件提醒 
```
{
    "time": 1742288726,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 663748426,
    "notice_type": "group_upload",
    "file": {
        "id": "202cb962ac59075b964b07152d234b70",
        "name": "1.txt",
        "size": 3,
        "busid": 102,
    },
}
```

#### 群聊表情点赞 
```
{
    "time": 1742288784,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 663748426,
    "notice_type": "group_msg_emoji_like",
    "likes": [{"emoji_id": "277", "count": 1}],
}
```

#### 群消息设精
```
{
    "time": 1742291691,
    "self_id": 3502644244,
    "post_type": "notice",
    "group_id": 736368697,
    "user_id": 663748426,
    "notice_type": "essence",
    "message_id": 1793170822,
    "sender_id": 663748426,
    "operator_id": 663748426,
    "sub_type": "add",
}
```

#### 群内戳一戳 （无raw）
```
{
    "time": 1742291345,
    "self_id": 3502644244,
    "post_type": "notice",
    "notice_type": "notify",
    "sub_type": "poke",
    "target_id": 1663273034,
    "user_id": 1945805744,
    "group_id": 580111434,
    "raw_info": [
        {"col": "1", "nm": "", "type": "qq", "uid": "u_pmbRUnEwvB12XKPkr0Fcpw"},
        {
            "jp": "https://zb.vip.qq.com/v2/pages/nudgeMall?_wv=2&actionId=1",
            "src": "http://tianquan.gtimg.cn/nudgeaction/item/1/expression.jpg",
            "type": "img",
        },
        {"txt": "拍了拍", "type": "nor"},
        {
            "col": "1",
            "nm": "",
            "tp": "0",
            "type": "qq",
            "uid": "u_k6dghbZrpnXslv8OD9Ky6w",
        },
        {"txt": "的手说是闲得慌", "type": "nor"},
    ],
}
```

#### 输入状态 
```
{
    "time": 1742290672,
    "self_id": 3502644244,
    "post_type": "notice",
    "notice_type": "notify",
    "sub_type": "input_status",
    "status_text": "",
    "event_type": 2,
    "user_id": 663748426,
    "group_id": 0,
}
```

#### 点赞 
```
{
    "time": 1742291836,
    "self_id": 3502644244,
    "post_type": "notice",
    "notice_type": "notify",
    "sub_type": "profile_like",
    "operator_id": 663748426,
    "operator_nick": "21－策划副会－微步",
    "times": 1,
}
```

## 其他
- QQ 电话消息：无
- 动态点赞：无
- 对他人消息表态：无
- 私聊临时会话撤回：无
- 好友删除：无
- 编辑群介绍：无
- 群消息撤回事件（只能管理员）
- 移出群精华
- 群消息表情表态无法获取具体消息

---
# 消息发送
#### 分享名片
```
{
    "status": "ok",
    "retcode": 0,
    "data": {
        "errCode": 0,
        "errMsg": "",
        "arkJson": '{"app":"com.tencent.troopsharecard","config":{"ctime":1742700198,"token":"5f5c746aaf8e041c9a562071c8784355"},"meta":{"contact":{"avatar":"https://p.qlogo.cn/gh/736368697/736368697/100","contact":"111","jumpUrl":"http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=XYXhoRKn4IhFFGp5Wl0qXTy3WxL974UK&authKey=mo%2BduCg%2F0zCeu%2BPsZR%2BQPM4RdRmYsYrr7XQsT%2Bb4eEr5Bn9w%2BV4jx9gsH9TkkkKg&noverify=0&group_code=736368697","nickname":"LR26710测试","tag":"推荐群聊","tagIcon":"https://p.qlogo.cn/gh/736368697/736368697/100"}},"prompt":"推荐群聊: LR26710测试","ver":"1.0.0.30","view":"contact"}\n',
    },
    "message": "",
    "wording": "",
    "echo": null,
}
```

---
# 其他
消息中的 raw(由于太长上面不展示) = {
        "msgId": "7483072596801338485",
        "msgRandom": "533587330",
        "msgSeq": "107",
        "cntSeq": "0",
        "chatType": 100,
        "msgType": 2,
        "subMsgType": 1,
        "sendType": 0,
        "senderUid": "u_0-TtmirQ_XxwlApzkRAvXg",
        "peerUid": "u_0-TtmirQ_XxwlApzkRAvXg",
        "channelId": "",
        "guildId": "",
        "guildCode": "0",
        "fromUid": "0",
        "fromAppid": "0",
        "msgTime": "1742288608",
        "msgMeta": {},
        "sendStatus": 2,
        "sendRemarkName": "",
        "sendMemberName": "",
        "sendNickName": "",
        "guildName": "",
        "channelName": "",
        "elements": [
            {
                "elementType": 1,
                "elementId": "7483072596801338484",
                "elementGroupId": 0,
                "extBufForUI": {},
                "textElement": {
                    "content": "123",
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
        "isOnlineMsg": True,
        "generalFlags": {},
        "clientSeq": "23567",
        "fileGroupSize": None,
        "foldingInfo": None,
        "multiTransInfo": None,
        "senderUin": "2973907990",
        "peerUin": "2973907990",
        "msgAttrs": {},
        "anonymousExtInfo": None,
        "nameType": 0,
        "avatarFlag": 0,
        "extInfoForUI": None,
        "personalMedal": None,
        "categoryManage": 0,
        "msgEventInfo": None,
        "sourceType": 1,
        "id": 684841211,
    },
