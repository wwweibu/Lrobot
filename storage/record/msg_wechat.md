#### 小视频消息??

#### 订阅

```
<xml>
  <ToUserName><![CDATA[gh_a0180524f340]]></ToUserName>
  <FromUserName><![CDATA[orHObs5yKLdX9tm-LjVWnuZ7u3ZM]]></FromUserName>
  <CreateTime>1752579658</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[subscribe]]></Event>
  <EventKey/>
</xml>
```

#### 取消订阅

```
<xml>
  <ToUserName><![CDATA[gh_a0180524f340]]></ToUserName>
  <FromUserName><![CDATA[orHObs-DIFeivAtfPdwgiYbiJ2i0]]></FromUserName>
  <CreateTime>1752566676</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[unsubscribe]]></Event>
  <EventKey/>
</xml>
```

#### 菜单点击

```
<xml>
  <ToUserName><![CDATA[gh_a0180524f340]]></ToUserName>
  <FromUserName><![CDATA[orHObs_grgOaE_a8zmmYJy9csQTc]]></FromUserName>
  <CreateTime>1752729357</CreateTime>
  <MsgType><![CDATA[event]]></MsgType>
  <Event><![CDATA[VIEW]]></Event>
  <EventKey><![CDATA[http://mp.weixin.qq.com/mp/homepage?__biz=MzAxMzMwOTM1Ng==&hid=2&sn=37326ce04a1207274b057a687f87341d&scene=18#wechat_redirect]]></EventKey>
  <MenuId>426732850</MenuId>
</xml>
```

# 显示机制

- 手机中无法正常显示及触发 \u2008,\u2009 换行符；手机及电脑中都无法解析换行符 \n,\r
- 