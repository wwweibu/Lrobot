#### 目录

- [规范](#规范)
- [消息](#消息)
- [系统配置](#系统配置)
- [系统日志](#系统日志)
- [数据库](#数据库)
- [系统环境](#系统环境)
- [系统运行](#系统运行)
- [功能](#功能)

#### 规范

~~强迫症必看~~

###### 命名规范

- 文件夹: 小写+单数
- 文件名: 小写+下划线+单数
- 模块引用: config<msg<adapter=data<command=app=msg_send<msg_process<msg_pool<main
- 文件内: 使用 """""" 来说明文件
- 导入顺序: 非项目在前，项目在后，按照长短排序
- 常量: 大写，下划线；导入语句下方
- 变量: 小写，下划线；全局变量放在常量下方，初始化变量放在最下方
- 类: 大写+驼峰，
- 函数: 小写+下划线，使用名、名、名、动的形式，统一将文件名放在最前面
- 函数内: 定义不写返回值，每个函数用""""""写注释
- yaml 中的值均加引号用 str(键默认 str)
- 使用 # TODO 来标注
- 使用 Black 处理代码

###### 日志规范

- 见日志

###### 文档规范

- git 提交规范

|    类型	    |        描述        |
|:---------:|:----------------:|
|   feat	   |       新功能        |
|   fix	    |      修复 bug      |
|   docs	   |       文档变更       |
|  style	   |      代码格式修改      |
| refactor	 | 重构（非新增功能或修复 bug） |
|   perf    |      	性能优化       |
|   test    |    	添加或修改测试代码    |
|   build   |     	构建相关的变更     |
|    ci     |   	CI 配置、脚本变更    |
|   chore   |     	其他杂项变更      |
|  revert   |     	回滚某次提交      |

- markdown 文件格式

|   类型    |                                   格式                                    |
|:-------:|:-----------------------------------------------------------------------:|
|   标题    |                                  #  ##                                  |
|   加粗    |                                  ** **                                  |
|   斜体    |                                  *  *                                   |
|   列表    |                            无序 -   <br/>有序 1.                            |
|   链接    |                               \[ \]\( \)                                |
|   图片    |                              \!\[ \]\( \)                               |
|   引用    |                                    >                                    |
|   代码块   |                              \`\`\` \`\`\`                              |
|   表格    |                   \| &nbsp;&nbsp;  \| <br/>\|:---:\|                    |   
|  任务列表   |                             - [x]<br/>- [ ]                             |
|   高亮    |                                  \` \`                                  |
| 图片自定义尺寸 |                           ![ ](url =200*100)                            |
|  html   |                                                                         | 
|   折叠    | \<details><br/>\<summary><br/>标题<br/>\</summary><br/>内容<br/>\</details> |

#### 消息

###### 消息类型

- 消息类型列表，其中 /n 代表 xx=None

| 消息类型/平台 |                               参数说明                               | LR232 群聊 | LR232 私聊 |  LR5921 群聊  | LR5921 私聊 | BILI | WECHAT |
|:-------:|:----------------------------------------------------------------:|:--------:|:--------:|:-----------:|:---------:|:----:|:------:|
|   接收    |                                无                                 |    √     |    √     |      √      |     √     |  √   |   √    |
|   添加    |                                无                                 |    x     |    x     |      x      |     √     |  x   |   x    |
|   撤回    |                          xx 撤回了 xx 的消息                           |    x     |    x     |      √      |     √     |  x   |   x    |
|   管理    |                          xx 增加/减少管理 xx                           |    x     |    x     |    可检测自身    |     x     |  x   |   x    |
|   禁言    |                            开启/关闭(接收)                             |    x     |    x     |      √      |     x     |  x   |   x    |      
|   减少    |                       (xx 将) xx 退出/踢出群 xx                        |    x     |    x     |      √      |     x     |  x   |   x    |
|   增加    |                        xx 邀请/同意 xx 加入群 xx                        |    x     |    x     |      √      |     x     |  x   |   x    |
|   回应    |                             \[表情:xx]                             |    x     |    x     |      √      |     x     |  x   |   x    |
|   设精    |                         xx 给 xx 的消息设置了精华                         |    x     |    x     |      √      |     x     |  x   |   x    |
|   戳戳    |                          xx x了x xx 的xx                           |    x     |    x     |      √      |     √     |  x   |   x    |
|   点赞    |                             xx 给你点赞了                             |    x     |    x     |      x      |     √     |  x   |   x    |
|   头衔    |                           xx 被设置头衔为 xx                           |    x     |    x     |      √      |     x     |  x   |   x    |
|   发送    |   dispatch(content,kind/n,user/n,group/n,num/n,seq/n，order/n)    |    x     |    x     |      √      |     √     |  x   |   √    |
|   下载    |                        download(media_id)                        |    x     |    x     |      x      |     x     |  x   |   √    |                 
|   上传    |                      file_upload(type,path)                      |    x     |    x     |      x      |     x     |  x   |   √    |      
|   签到    |                          sign_in(group)                          |    x     |    x     | 无论成功与否都是 ok |     x     |  x   |   x    |
|   戳戳    |                        poke(user,group/n)                        |    x     |    x     | 无论成功与否都是 ok |   测试失败    |  x   |   x    |
|   分享    |                    share(num,user/n,group/n)                     |    x     |    x     |      √      |     √     |  x   |   x    | 
|  状态设置   |        status(status, ext_status, battery_status,id,word)        |    x     |    x     | 无论成功与否都是 ok |     x     |  x   |   x    |
|   回应    |                         echo(seq,emoji)                          |    x     |    x     |      √      |     x     |  x   |   x    |
|   签名    |                         signature(sign)                          |    x     |    x     |      x      |     √     |  √   |   x    |
|  消息获取   |                    msg_get(seq,num/n, user/)                     |    x     |    x     |      x      |     √     |  x   |   x    |
|  状态获取   |                       status_get(num,user)                       |    x     |    x     |      x      |     √     |  x   |   x    |
|   转发    | forward(group, nickname, content, news, prompt, summary, source) |    x     |    x     |      √      |     x     |  x   |   x    |
|  转发单条   |                forward_single(id,user/n,group/n)                 |    x     |    x     |      √      |     √     |  x   |   x    |
|   撤回    |                   withdraw(seq,user/n,kind/n)                    |    x     |    x     |      √      |     √     |  x   |   x    |
|   精华    |                      essence(id,content/n)                       |    x     |    x     |      √      |     x     |  x   |   x    |
|   头衔    |                     title(user,group,title)                      |    x     |    x     |      √      |     x     |  x   |   x    |
|   列表    |                         list(num,group)                          |    x     |    x     |      √      |     x     |  x   |   x    |
|  消息已读   |                          msg_read(user)                          |    x     |    x     |      x      |     x     |  √   |   x    |
|  回应查看   |                           reply_check                            |    x     |    x     |      x      |     x     |  x   |   √    |

| 系统消息 |

- LR5921:
    - 精华:有时是管理员但无法设置精华
    - 群成员名片更新:无法检测
    - 发送消息:若别人主动开启临时会话即可发送
    - 戳戳消息:榴莲、平底锅等无法解析
    - 添加好友:开启了任何人都能添加好友则不会收到对应 request
    - 设置已读:不需要
    - 临时消息:取消处理,原处理方法如下:
  ```
  sender = data.get("sender")
  nickname = sender.get("nickname", "")
  if nickname == "临时会话":
      kind += "临时"
  ```
    - 英译中: /translate_en2zh 测试失败
    - 获取点赞列表: /get_profile_like 测试失败
    - 获取群聊表情回应列表: 测试失败
    - 发送音乐卡片:测试失败，id 不知道
    - 点赞他人: 感觉不需要
    - 获取收藏表情:感觉不需要

###### 消息字段类型

- 其中加粗的为匹配字段

| 类型/数据类型 |    格式     |  text  |      id       |   qq   |    result    | summary |   file   | url  |                   other                   |
|:-------:|:---------:|:------:|:-------------:|:------:|:------------:|:-------:|:--------:|:----:|:-----------------------------------------:|
|  text   |    文本     | **文本** |               |        |              |         |          |      |                                           |
|  face   |  [表情:xx]  |        |  **表情**(转换)   |        |              |         |          |      |                                           |
|   at    |  [at:xx]  |        |               | **qq** |              |         |          |      |                                           |
|   rps   |  [猜拳:xx]  |        |               |        | **1布2剪刀3石头** |         |          |      |                                           |
|  dice   |  [骰子:xx]  |        |               |        |    **点数**    |         |          |      |                                           |
|  reply  |  [回复:xx]  |        |   **消息 id**   |        |              |         |          |      |                                           |
| forward |  [转发:xx]  |        | **消息 id**(发送) |        |              |         |          |      |         **content.message 是消息列表**         |
|  poke   |   [戳戳]    |        |    **种类**     |        |              |         |          |      |                   type                    |     
|  mface  | [动画表情:xx] |        |               |        |              | **概括**  |          |      |       key,emoji_id,emoji_package_id       |
|  image  | [动画表情:xx] |        |               |        |              | **概括**  |   文件名    | 下载链接 |       key,emoji_id,emoji_package_id       |
|  image  | [动画表情:xx] |        |               |        |              | **概括**  |   文件名    | 下载链接 |            sub_type,file_size             |
|  image  |  [图片:xx]  |        |               |        |              |   概括    | **文件名**  | 下载链接 |            sub_type,file_size             |
| record  |  [语音:xx]  |        |               |        |              |         | **文件名**  | 下载链接 |              path,file_size               |
|  video  |  [视频:xx]  |        |               |        |              |         | **文件名**  | 下载链接 |                 file_size                 |
|  file   |  [文件:xx]  |        |               |        |              |         | **文件路径** |      |      file_id,file_size,**name**(发送)       |
|  json   |  [卡片:xx]  |        |               |        |              |         |          |      | data(ver,**prompt**,app,view,config,meta) |  
|  node   |  [节点:xx]  |        |               |        |              |         |          |      |               content 是消息列表               |

- 发送时，反解析：
  - mface: summary|key|emoji_id|emoji_package_id
  - image: file|summary
  - video: file|title|description
  - file: file|name
  - json: 微信-音乐|title|description|url
  - json: 微信-图文|title|description|picurl|url
- 优先级:卡片>文件>视频>语音>其他，会覆盖掉其他的
- 骰子和猜拳只能单独发，否则只有缩略图
- img,record,video,file 发送时只需要 file 字段(file 可加 name 字段，效果是重命名)
- 其中 mface 是去除了 file 和 url 的商城表情，无法接收
- img 均有 summary,file,url 字段
- 其中动画表情和纯图片包含 sub_type 和 file_size 字段，且 summary 一个是动画表情一个是空，sub_type 一个是 1 一个是 0；
- 商城表情包含 key,emoji_id,emoji_package_id 字段
- contact,字段:type,id,由于只在获取推荐卡片的接口使用，不会收到此类消息，故不解析
- music 字段:type,id，只在发送音乐卡片（测试失败）和自定义音乐卡片时使用，不会收到此类消息，故不解析
- json 字段接收时 data.data 的值包含双引号需要 json.loads 解析；发送时是否包含双引号没有影响
- forward 字段不能直接发送，node 字段不能直接发送，把 forward 和 node 写进消息发送里一并解析
- node 字段分层嵌套，每一层有一个转发者和昵称，以及消息列表；消息列表中的每个消息也是一层（node 字段），包含发送者、昵称和原消息（文字、图片、转发等）
- 转发接收的形式为\[转发:\[图片:xxx.jpg]\[图片:xx.jpg]]，发送的形式为\[转发:id]
- 节点接收(解析发送)的形式为 \[节点:\[节点:12345]\[节点:\[图片:storage/file/firefly/logo.png]]\[节点:\[节点:\[节点:
  12345]\[节点:12344]]]]
- 节点发送的形式为 \[节点:123|张三|\[节点:1234|李四|12345]\[节点:12345|王五|\[图片:storage/file/firefly/logo.png]]
  \[节点:122|赵六|\[节点:123444|王二|\[节点:221|张一|12345]\[节点:442|张三|12344]]]]
- 接收时，微信图片包含 url,file(media_id) 字段，语音、视频包含 file(media_id) 字段，位置转换为 json，data 中包含
  prompt，location_x，location_y，scale 字段，链接转换为 json,data 中包含 prompt，description,url 字段
- 发送时，微信视频的格式为\[视频:path|标题|描述]
- 接收时，B 站图片包含 file(imageType),url,original,size,width,height 字段，B 站系统通知包含 prompt(text),type(系统通知),
  ,title,jump_text,jump_uri,modules 等字段,B 站分享包括 type(新增),author,headline,id,source,thumb,title,bvid 字段
- B 站图片分享包括 prompt(title),type(图片分享),picurl,jumpurl 字段;直播分享包括 prompt(title),type(直播分享)
  ,author,cover,desc,source,url 字段
- 待测试:B 站如果接收\[ \[表情:xx\]的消息会不会报错；B 站如果接收\[表情:xx]的文字消息会不会和表情消息字段一样
- B站的机制为:如果\[xx]能被识别成表情，则会发送表情，如果不能则不会发送
- `parts = re.split(r"(\[[^\[\]]+])", content)` 会自动捕获最里面的\[]以及最近匹配的\[，所以如果文字里有单独的\[或者\[表情]，会自动解析出最里面的表情
- 如果某人要以\[xx]的文字形式发送没有的表情，那么主观上他需要发送表情，客观上我们需要接收表情且不在文字识别的程序中，所以我们可以解析成表情。这样也可以避免使用表情列表时，一些新表情添加、旧表情删除的问题

- 指令匹配时，文字消息都是 'in'，即 123\[图片:xx]123\[图片:xx]1234 会与包含 12\[图片:any]12\[图片:any]1 相匹配
- 指令匹配时，匹配指令不出现转发、节点字段

###### 消息池
- 消息队列负责逐一处理消息，消息池负责存储消息（获取）
- 消息池中消息存储在 storage.yaml 中，且每天清理

###### 消息处理
- 消息处理时，先根据 msg.event 将消息分为发送和处理逻辑
- 处理时，对 command.yaml 中的指令（指令页面配置）逐一检索条件
- 分别检索消息平台、消息种类，均为列表，即消息属性在列表中即通过
- 随后根据群聊消息和私聊消息分别检索
  - 群聊消息需要在 groups 列表中才能通过（若列表为空代表通过）
  - groups 列表是群名，群名在 user.yaml 中（用户配置页面配置），一般一个群名下分为 LR5921 获取的群号以及 LR232 获取的 group_id
  - 私聊消息需要用户身份在 users 列表中才能通过（若列表为空代表通过）
  - 用户身份在 user.yaml 中配置，一般一个用户组里有多个用户，用户有多个用户组即有多个身份；若用户在用户组中，即获得“内阁”身份
  - 除此之外，user_test 表中有“测试员”身份
- 随后根据 "contain" 包含与 "equal" 相等来匹配指令
  - 匹配指令为指令列表，即包含/相等的词是一个列表，以下检测方式是对指令列表中的每个匹配指令生效的：
  - 包含时，会在消息段中以动态窗口的形式检测匹配指令，其中\[xx:any]代表匹配所有指令
  - 且对于文本类指令，包含匹配其他类型指令中间的文本，即\[图片:xx]1234\[图片:xx]能够被匹配指令\[图片:xx]123\[图片:xx]匹配
  - 且对于文本指令，" " 代表 any
  - 相等时，会检测消息段与匹配指令是否全等
  - 当匹配指令为\[xx:any]时代表相等

###### 消息发送
- 参考消息字段类型中的消息

###### 消息格式

- ~~字符测试：手机中文25，英文35，窄屏手机24，英文33；电脑中文50英文八十；等号一行24~~

###### 表情识别逻辑

- 存在于表情商城里的表情会被 qqbot 识别成faceType=4，即使添加在收藏里；不存在于表情商城理的表情即使添加在收藏里也会被识别成图片

###### 消息种类及处理逻辑

- **回复消息：1.存在回复以及@机器人即被视作回复消息:因为回复时可以在@前面加入文字并且也可以@其他人；2.@LR5921视为回复，@LR232不做处理：LR232无法识别回复消息（可以做但无法获取消息id且消息id不统一）；3.回复消息优先级比文件消息、图文消息、文字消息均要高，
  *回复时无法执行这几种消息的逻辑***
- 消息形式: 序号，平台名（LR232，Weibo，WeChart），内容，触发事件（配对，处理，发送），种类（群聊/私聊/资讯），文件名,下载链接,来源（群）,来源（QQ，公众号名，发送者）,消息
  ID,匹配的消息序号
- 多图文消息创建多个消息进行处理
- LR232收到同一图片不同消息时，url不一样

###### 消息处理监控

- 使用装饰器的形式来监控消息的处理数据
- 消息由 adapter 适配器或者 command 指令中产生，在 adapter 中进行了预处理，在 command 中产生后即被投入消息池
- 故消息处理监控要分为预处理和处理两阶段
- 预处理由消息的路由函数 xxx_receive 转到 xxx_msg_deal，在 deal 函数中添加消息监控装饰器，名称为对应平台
- 处理由在消息的指令函数上添加消息监控装饰器实现，监控从消息传入处理函数到创建新消息（若有）的时间等数据，名称为指令页面上显示的功能名称
- 监控指标包括消息总数、成功数、失败数、总时间
- 消息处理监控装饰器中不处理消息中产生的错误，捕获后传递给对应的调用方

#### 系统配置

###### 配置读写
- SafeDict 实现了字典的安全读写，config\['a'\]\['b'\]的时候，如果 config 没有 a 键则会报错，使用 SafeDict 可以只返回空值而不报错
- AutoConfig 实现了配置的载入与自动写入，载入时跳过 "_copy.yaml" 文件，并把文件中的键都载入 config 中，记录每个键的来源文件与每个文件的哈希值
- 自动写入通过修改写入方法实现，当配置更改时，通过读取该键的来源文件，将修改后的值添加并写入到来源文件中
- AutoConfigHandler 实现了配置的自动更新，在 config_watcher 函数中实例化。通过监听 yml
  文件夹中对应文件的变化，若文件哈希值改变则重新加载配置，达到配置更新的效果
- AutoConfig 和 AutoConfigHandler 没有写成一个类，是为了兼容不配置自动更新的、或者不需要异步事件循环的文件，config.py
  中的配置可以挂载到任意容器中，并且直接引用`from config import config`
- 由于保存机制（待研究），按 ctrl+s 后会触发两次 watchdog，所以需要文件哈希来减少读写次数
- 当多个 yaml 存在相同的键值时，后面的会覆盖前面的

###### 数据保存
- 当系统停止运行时，未处理完的消息、未实现的验证码等，都将失效，同时也无法获取到之前的撤回消息
- 将此类数据实时写入数据库/yaml 文件都比较麻烦
- 所以在 AutoConfig 中实现 load 和 save 操作
  - 初始化时加载 storage.yaml 中的数据，并绑定对象至 config[xx] 中
  - 结束

###### 全局路径
- 相对路径和绝对路径：绝对路径就是本机上的绝对路径，受到不同电脑环境因素影响大；但相对路径也不好用，在 python
  里面主路径为执行的文件的路径，如果要测试某模块，使用相对路径可能会造成路径错误；在某些包里面，相对路径可能也不是执行文件的路径，而是调用包的文件的路径
- 所以采用一个绝对的相对路径来解决以上所有问题，定义变量 path，项目里的所有路径都引用这个路径，就一定不会出现问题
- path 路径在 docker 中为 /app，在 python 程序中为主文件夹(如 /lrobot，main.py 的上一级)
- 除包自动更新模块外，其他都尽量用`from config import path`来搭建路径

###### 代理连接

- LR232、WECHAT 此类需要配置白名单的平台需要使用代理连接
- command 容器中将 0.0.0.0:5923 端口使用 sock5 转发到服务器上，故代理连接需要连接至 command:5923 来实现转发
- 使用 connect(True) 即可实现代理，正常使用 connect；由于 request 是阻塞的，所以返回 httpx 对象
- 使用示例:

```
client = connect(True)
    response = await client.get(url, headers=headers)
    if response.status_code == 200:
    else:
```

- 其中 get 方法传入的是 params，post 方法传入的是 json

###### future 变量
- 存在进程间通信的情况，即:消息 A 收到 "Hello"，但需等到消息 B 收到 "World" 后才能拼接成完整内容，由于消息 B 到达时间不确定，必须有机制让 A 等待或监听 B 的结果
- 一般分为三种处理方式:while True 循环检查；queue.get() 等待队列中的数据；future 协程变量
- 方法 1 占用内存高；方法 2 不适合处理多个 B 发送的情况（假设 A1 要等待 B1，A2 要等待 B2……）
- future 机制为：在事件循环中，某个协程使用 await future 后，线程变为挂起状态；当 set future 后，协程变为就绪状态，在事件循环进行到该协程时执行协程
- 项目使用一个 future 管理器来简化 future 的创建与设值过程
- 创建
- ```
  try:
        _future = future.get(seq)
        response = await asyncio.wait_for(_future, timeout=20)
    except asyncio.TimeoutError:
        raise Exception(f"消息超时 | 消息: {xml_data}")
  ```
- 设值       
  `future.set(seq, response)`
- future 无法通知对应协程的解决办法说明: 
  - 若在一些独立运行的线程中设置future（如 flask 中自带的 werkzeug 日志记录器），由于不和主事件循环处于同一线程，无法通知循环中协程的 future 更新
  - 可以参考[future.py](abandoned/future.py)里面的例子
  - 上半部分中，只调用 a、b 函数的情况下，由于 flask 是在另一个线程中执行的，future(a) 的值被设置后不会通知 b（但值已经变了）
  - 上半部分如果再调用 c 函数，由于 c 会频繁检查 future(a) 的值，则会触发 future(a) 的更新机制，通知 b 函数
  - 下半部分是除了频繁检查外的另一种解决办法，使用 loop.call_soon_threadsafe 通知其他的线程

###### 定时任务

- 误以为 APScheduler 会引发一些 bug，故自己编写了一个代替品
- 支持添加函数，设置时间间隔和固定时间，设置次数
- 同时可以传入对应参数，如 add_scheduler(clean_messages,86400,interval=86400)
- 需要在新协程中执行，否则会阻塞（其实是挂起）当前任务，asyncio.create_task(add_scheduler())
- 会在任务中自行处理异常
- 固定时间只能处理每天的固定时间，若想固定每小时 xx 分执行需要自行修改函数

###### 路径加密

- 在 secret.py 中配置 secret() 函数给 fastapi 的路径进行加密，防止消息原字段、后台信息被截取
- 加密后各平台配置的路径都需要改成对应路径

###### (废弃)yaml和数据库加解密操作

- 项目中途考虑过 yaml 的加解密操作，即：项目启动时需要添加一行 ```secret=xxx```，未添加时，yaml
  和数据库中的所有数据都会进行加密，但在读取时会自动解密，其他用户可以在不影响正常使用的情况下无法看到我的 yaml 文件中的密码
- 但后面考虑到实用性不足，别人需要配置自己的密码，且数据库信息在网站页面也可以浏览到，放弃了这一想法
- 相关实现可以看 [secret.py](abandoned/secret.py)
- A为所有者，B为使用者
- A调用decrypt_files(密码)，无论是否加密，成功解密，yaml和数据库复原，可直接查看
- B调用decrypt_files()，无论是否加密，成功加密，yaml和数据库上锁，不可直接查看，但不影响使用
- 采用 AESGCM 加密 yaml 文件，采用 sqlite 自带的加密数据库

#### 系统日志

- 系统采用统一的日志记录格式
- 日志配置通过 config 读取 log.yaml 中获得，分为:
    1. formatters: 日志输出的文本格式与时间格式
    2. handlers: 日志处理器，定义日志的输出方式，可绑定对应的 formatters 和日志等级
    3. loggers: 日志记录器，定义日志的入口配置，指定日志的最低等级与处理器
- 当配置重载调用 load_config() 函数时，会调用 reset_log 清除所有的日志设置，然后通过 dictConfig() 加载 config
  中的日志配置项，并为日志添加过滤器
- 日志记录器分为一个个 logger，当日志产生后，logger 会调用它所分配的 handler，handler 中会将日志格式化成指定的
  formatter，并调用对应的 filter，最后输出
- 日志记录器设置 propagate: no 阻止日志向上传播，防止重复记录
- 日志的记录时需主动添加 event
  字段: `loggers["system"].error(f"yaml 文件 {config_file.name} 格式错误 -> {e}", extra={"event": "配置读取"},)`

###### 日志处理器

- 设置了控制台日志处理器与数据库日志处理器
- 二者格式均为`%(asctime)s|%(levelname)s|%(name)s|%(event)s|%(message)s`
- 二者均根据 SOURCE_DICT 中配置的内容将日志记录器的 source 字段转换为对应的字段（统一 7 个字符，不够加空格，控制台输出好看）
- 转换后如三个 uvicorn 处理器都变成了 website，达到合并日志的效果
- 控制台日志处理器去除原日志中的颜色，并按照 debug:灰 info:黑 error:红 的颜色输出到控制台
- 数据库日志处理器将 level、name、event、message 字段插入写入队列，写入队列再写入 Mongodb
  数据库中（直接写入会遇到连接数据库的日志、初始化的日志等写入错误的情况，故需要一个队列）

###### 日志过滤方式

- uvicorn 拥有三个日志记录器: uvicorn,uvicorn.access,uvicorn.error
- 在 set_log() 中覆盖其日志记录器，添加日志格式与处理器，在处理器中添加过滤器 UvicornFilter
- 过滤器判断日志中是否存在 args
  参数，如果存在则是路径访问的日志如 `INFO:  127.0.0.1:5161 - "GET / HTTP/1.1" 404 Not Found`
- 过滤器提取其中的 ip:127.0.0.1:5161,method:GET,path:/,http_version:1.1,status_code:404
- 并将 status 通过 http.yaml 配置转换成中文，作为 event 参数写入日志
- 并设置 event 字段为'运行日志'
- 其他四个字段处理成如下格式存入 message 参数:\[ip\]method path -> HTTP/http_version
- ssh 连接会产生空行，故添加过滤器 ServerFilter 来消除空行，将等级均设置成 debug，顺便将 `debug1:` 的调试日志前缀去除
- （未使用）napcat 的过滤器 LR5921Filter 中同样清除了空行，并根据观察将原来是 debug 等级的日志更改为 debug（从控制台中读取的全部都是
  info）
- LR5921Filter 从消息中提取了 level 和 info 信息作为 level 和 message 字段
- 在 [service.md](service.md) 中可以找到除 napcat 外 xiaomiqiu、Prometheus
  系软件的日志情况及处理结果，在 [service.py](abandoned/service.py) 里可以找到 LOG_FORMATS 为这些日志字段的正则匹配方法

###### 日志格式

- level 字段分为 debug,info,error;source 字段为 7 位英文;event 字段为四个字
- `[数据库连接失败] Mongodb 异常: e` 及 `[日志写入失败] Mongodb 异常: e`
  三条日志存在反复写入的问题，故不用日志记录器改用 print
- 以下为日志所有的 source、event 与 message 格式

| source  | event |         message          |
|:-------:|:-----:|:------------------------:|
| system  | 配置读取  |   yaml 文件 xx 格式错误 -> e   |
| system  | 配置读取  |          配置数据更新          |
| system  | 配置读取  |      yaml 文件 xx 更新       |
| system  | 定时任务  |     定时任务 xx 异常 -> e      |
| system  | 错误堆栈  |            xx            |
| system  | 运行日志  |        xx 数据库连接成功        |
| system  | 运行日志  |      任务 xx 异常 -> e       |
| system  | 模块加载  |            xx            |
| system  | 模块加载  |       失败: xx -> e        |
| server  | 运行日志  |         ssh 相关输出         |
| server  | 运行日志  |    检测到连接关闭，正在重新启动...     |
| website | 运行日志  |            xx            |
| website | 管理操作  |          \[] xx          |
| website | 超频访问  |     IP xx 被封禁 10 分钟      |
| website | 运行日志  | IP: xx \| 请求路径: xx -> xx | 
| adapter | 令牌刷新  |      ⌈xx⌋ 令牌有效期 xx       |
| adapter | 令牌刷新  |     ⌈xx⌋ 令牌刷新失败 -> e     |
| adapter | 消息接收  |       ⌈xx⌋ 回调配置成功        |
| adapter | 消息接收  |       ⌈xx⌋ xx(数据)        |
| adapter | 消息接收  |       ⌈xx⌋ xx -> e       |
| adapter | 消息发送  |      ⌈xx⌋ xx -> xx       |
| message | 消息存储  |     ⌈xx⌋xx: xx-> xx      |
| message | 消息清理  |        共清理 xx 条消息        |
| message | 消息处理  |   ⌈xx⌋出错: 'xx' -> {e}    |
| message | 消息处理  |      ⌈xx⌋: xx -> xx      |
| message | 消息发送  |      ⌈xx⌋: xx -> xx      |

- ⌈⌋两个括号自取⌊⌉

###### 其他

- 日志的 record 属性中包含 levelname,name,msg,args,pathname,lineno,funcName,created,exc_info 字段
- 如果在 yml 中定义了文件日志处理器，则不管被不被引用，都会创建一个 .log 文件

#### 数据库

- 由于在知识库更新时同时 100 条数据写入超时，且日志数据较多每次前端读取慢，故使用 Mysql 记录数据，Mongodb 记录日志
- 所有库都以 id 为主键，且所有字段不许为非空，可设置唯一键。因为数据库页面的插入行的设定为：给所有的插入空值，mysql 允许唯一键为空值

###### 数据库设计

- docker 采用 mongo:4.4(机器搭载不了最新的) 与 mysql:8.0 镜像
- Mongodb 和 Mysql 均挂载备份文件；Mysql 挂载初始化文件来创建表以维持系统基础运行
- 数据库采用 mongo_init 和 mysql_init 进行连接
- config 中自动初始化 Mongodb 连接，Mysql 连接需要自行调用

###### Mysql 提交处理

- 在 Mysql 连接时设置 autocommit=False 来控制数据库提交时的失败回滚
- 但在设置泡泡页面广播时出现异常: A 页面更新某泡泡位置提交到后端后，反复刷新页面，数据库查询的结果会在原位置和新位置反复调到
- 使用 pycharm 连接 Mysql 数据库可以看到数据正常提交，没有出现任何变化
- 理由为:
- database_update 执行了显示提交 conn.commit()，更新操作是持久化的；而 database_query
  中只是执行了查询，没有提交事务，因此这个连接的事务实际上没有结束（即使查询已完成）
- 当 database_query 的连接被释放回连接池，被另一个请求再次获取时，这个连接上可能存在一个未提交的事务（一个没有写操作的空事务）
- 所以这个连接再次被用于 GET 请求，执行新的查询时，由于 REPEATABLE READ 的隔离级别，它可能会继续使用之前建立的快照（旧数据），而看不到其他连接提交的更新
- 解决办法: 在 database_query 执行前加上一句 await conn.commit()

###### (废弃)旧版数据库的比较方式

- 在使用 sqlite 数据库时对多种连接方式进行了比较，现在要改回 sqlite 数据库需要把 Mysql 语句中的 %s 改成 ?
- 异步队列在调用数据库时会由于读写锁导致延迟
- 在直接读写（靠锁来自行分配）、分五个库（同步多操作）、建立连接池（减少建立连接时间）、使用批量提交（一次性提交）中，批量提交的方法效率最高且接近极限效率
- 假设：建立连接：5ms，提交事务：1ms/10ms(批量)，执行事务：1ms，错误日志：0.1ms

| 方案          | 	连接方式	  | 连接耗时           | 	事务提交耗时          | 	事务执行耗时               | 	错误重试耗时      | 	总时间     |
|-------------|---------|----------------|------------------|-----------------------|--------------|----------|
| 直接读取	       | 每次新建连接  | 	10000 * 5ms   | 	10000 * 1ms	    | 10000 * 1ms           | 	100 * 0.1ms | 	70.01 秒 |
| 拆分 5 个数据库	  | 每库 1 连接 | 	2000 * 5ms	   | 2000 * 1ms	      | 2000 * 1ms            | 	100 * 0.1ms | 	14.01 秒 |
| 连接池（5 连接）	  | 复用连接    | 	5 * 5ms	      | 2000 * 1ms       | 	2000 * 1ms	          | 100 * 0.1ms  | 	4.035 秒 |
| 批量提交（100/批） | 	每次新建连接 | 	2 * 100 * 5ms | 	2 * 100 * 10 ms | 	100 * (100+99) * 1ms | 	100 * 0.1ms | 	22.91 秒 |

- 可以发现，批量提交并没有达到极致效率。拆分和连接池主要是提高并行效率（5倍），同时增加cpu使用率（5倍），拆分相比连接池差在增加了连接耗时
- 同时可以比较批量提交+单连接复用与连接池，可以发现，在忽略连接时间时，由于错误处理，前者事务提交耗时翻倍，即使事务执行耗时变成了0.1，也是原来的1.05倍时间，后者则只是原来的0.2倍时间
- 使用 condition 会出现同时唤醒所有正在等待的协程的情况
- 测试用例在[db.py](abandoned/db.py),可以运行查看数据的处理顺序

#### 系统环境

- 项目整体分为三个部分:宿主机(主服务运行处),服务器(拥有公网 ip，负责转发),域名(服务对外端口)
  -![项目架构图](img/readme_1.png)
- 宿主机上配置 docker 环境
- 为使项目能够在 linux 上运行，采用 docker 技术
- 为防止测试时频繁重启导致 QQNT 产生异常，将 Napcat 与主服务分离
- 为减少安全风险 Napcat 采用 docker 形式
- 为减少频繁连接服务器导致的 ssh 进程未关闭/多 ssh 进程占用服务器的问题，将 command 服务（连接到服务器）与主服务分离
- 为提高数据库的写入速率将日志与常规数据分离，采用 Mysql 与 Mongodb 代替 sqlite 数据库，同时为了这两个服务不用本地安装、配置环境，采用
  docker 的形式

###### 宿主机容器配置

- lrobot 服务是消息处理中枢，将各路径的消息汇总并处理成统一格式，进入消息队列进行不同的指令处理，然后调用各路径的发送 API
  进行消息反馈
- command 服务提供部分消息的转发(网站消息、LR232 消息、WECHAT 消息)
- 通过运行命令行指令:`ssh -i pem_path -C -v -N -D 0.0.0.0:5923 -R 10000:lrobot:5922 username@ip`
- 将远程服务的 10000 端口消息转发到 lrobot 服务的 5922 端口上(lrobot 部署 fastapi 的端口)
- 同时将容器内的 5923 端口(command:5923)通过 socks5 转发至服务器上，将消息从宿主机转发至服务器，lrobot 通过代理 command:5923 来调用三个平台的发送 API
- napcat 服务提供 LR5921 的运行环境，并将消息上报至 lrobot 服务的 5922 端口上(lrobot:5922)，在容器内的 5921 端口提供消息发送 API，lrobot 通过发送至 napcat:5921 来调用 LR5921 的发送 API
- mysql 和 mongodb 数据库分别在容器内的 3306 和 27017 端口提供服务
- 所有容器的时区都是上海正常时区，以便日志时间正常记录

###### 宿主机容器环境

- 项目包通过 requirements.in 和 requirements.txt 构建
- config.py 的依赖包在主目录下的 requirements.in 里，生成的对应 requirements.txt 在 command 目录下
- lrobot 对应的 requirements.in 由 config 的依赖包+lrobot 里的依赖包合并而成
- 进入 lrobot
  文件夹，使用命令 `docker run -it --rm -v %cd%:/app -w /app python:3.11 bash -c "python -m pip install --upgrade pip && pip install -r requirements.in && pip freeze > requirements.txt"`
  生成对应的 requirements.txt
- 其他方法
    - 使用 `pip-compile requirements.in` 会依赖当前 windows 环境生成包，可能不符合 linux 上的要求
    - 使用 pipreqs 会生成重复包、或者生成遗漏包
    - 如果要在不配置好环境的情况下生成包，只有不断运行并往 requirements.in 添加需要的包

###### 宿主机调试配置

- docker desktop 上有各容器的日志可调试（网页管理端同样有日志）
- lrobot 将 5922 端口暴露到本地，方便 vue 调试以及本地直接登录网址测试，在不启动 command 的情况下可以反复调试修改前后端
- vue 调试使用自带的 5173 端口，调试环境为本地，通过访问本地的 5922 端口来与后端通信(在 api.js 与 vite.config.js 中配置);打包后为静态文件挂载在 fastapi 下
- napcat 将 6099 端口暴露到本地，可访问 http://127.0.0.1:6099/webui?token=napcat 进行相关配置
- mongodb 和 mysql 分别将 5924 和 5925 端口暴露到本地，方便查看数据（如使用 pycharm 连接到数据库）

###### 服务器 nginx 配置
- 配置 http 自动跳转到 https(80 跳转到 443)
- https 配置中使用 HSTS(强制 HTTPS)
- 配置默认的错误页面(需要根据路径自行在服务器上配置)
- 配置反向代理到本地的 10000 端口
- 配置禁止通过服务器 ip 访问，只能通过指定域名访问(防止恶意域名如 whumystery.xxx.cn)
- nginx 配置在请求头处携带 ip，供后端分析原 ip

#### 系统运行

###### 模块调用

main中调用config_watcher,log_writer,scheduler,  ***TODO***

###### 异常抛出与捕获

- 异常的 traceback.format_exc() 只会打印出行号，而不会携带对应传入的参数，故在 database_query 和 database_update 里的错误加入了参数
- msg_process 中捕获 msg 产生后的错误
- app 中捕获 fastapi 产生的错误
- scheduler_add 中捕获定时任务中产生的错误
- config=AutoConfig() 自行处理异常，其中 setitem 由对应模块接收异常
- future 理论上不会产生异常（除非主循环关闭）
- mongo_init 自行处理异常
- refresh_tokens 自行处理异常
  ***TODO***
- main里面无法捕获异常和使用finally的原因：await asyncio.Event().wait()、while True、queue.get()、asyncio.sleep()都无法响应取消

#### 功能

###### 执行命令行代码
- command 容器中使用 subprocess.Popen 来执行命令行内容
- 命令行内容除了 ssh 命令，还测试过 xiaomiqiu,napcat,grafana,loki,promtail,windows-exporter,prometheus
- 一共有 `subprocess.check_output(xxx, stderr=subprocess.STDOUT)` 和 `subprocess.run(xxx,stdout=subprocess.PIPE,stderr=subprocess.PIPE)` 和 `subprocess.Popen(xxx,stdout=subprocess.PIPE,stderr=subprocess.PIPE)` 和 `subprocess.Popen(xxx,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)` 四种方法
- 其中只有最后一种将 err 管道重定向到 out 管道的才能兼容所有的命令行日志输出，原因可能为 loki 采用的 go 语言中的日志输出流不太一样，其他方式无法捕获
- 使用 `async for line` 代替 `while True:line = await process.stdout.readline()`，让函数内调用自身（重新执行命令行）也不会阻塞输出
- 在主程序退出时，主循环退出，各任务结束。在 try-finally 中，只有使用 process.communicate() 才能捕获命令行任务退出时的输出，无论是使用 signal 模拟 Ctrl+C 信号还是使用 process.wait() 都无法捕获
- 如果采用写入文件的形式会输出不及时，且程序退出时需要额外的等待代码来确保日志文件写完
- ssh 由于自身调用自身无法消除环境影响，所以采用连接失败直接退出 `sys.exit(1)` + 容器 `restart: always` 来重新启动
- xiaomiqiu 需要添加 -log stdout 参数，不然默认没有命令行输出只有文件输出
- 命令行命令中加上 ```@echo off```可以不捕获命令本身，加上 ```chcp 65001``` 可以防止一些使用 gbk 编码的文件乱码（统一使用 UTF-8)
- 此方法可以捕获 Napcat 中的调试代码（不会在正常控制台执行时出现

###### 导入

- 内部导入(如函数内导入)主要是为了防止循环引用
- 内部函数主要是为了好看，当逻辑可能多次被调用时，内部函数会被编译多次，效率低
- 错误：”软件包外部的相对导入“，在没有 __init__.py 的文件夹（非包文件夹）中不能用"."来使用相对路径

###### 异步连接

- 在 http/2 中，同一域名多个路径会复用同一连接
- 但在同一服务下建立连接池/单个连接复用的代价太大，需要考虑到某一连接超时影响所有连接的情况
- 几乎不会出现连接占用所有端口的情况，除了本地的 napcat 连接外，其他所有的连接都使用 command:5923 端口转发,占用的是服务器的端口数

###### ip 相关

- 配置封禁 ip，针对 10 秒内 5 次异常访问的，封禁 10 分钟
- 发现网上的很多扫描行为:
    - 端口有： /，/form.html,/upl.php,/t4,/geoip,/1.php,/password,/TQSd,/nXVA,/aab8,
      /jquery-3.3.1.slim.min.js,/aab9,/jquery-3.3.2.slim.min.js
    - 使用 `ssl_reject_handshake on` 可以避免 Censys 识别服务器 ip ~~（真的吗？）~~
    - 使用 Censys 发现服务器 ip 已经泄漏了
    - 禁止直接访问服务器 ip 可以避免在 Censys 上挂名

###### 消息队列(msg_pool)

- 虽然 DS 极力推荐我使用 RabbitMQ、Redis Streams、Kafka，但可以自行实现崩溃优化
- 消息队列主要起到使逻辑清晰的作用

###### 消息处理(msg_process)

- 在 msg_process 中，消息通过判断各属性是否匹配来调用功能

- 动态更新最初采用 update 函数来更新模块，即修改 yaml 文件后修改判断条件和引入函数，但函数模块在导入后就不可修改了，是伪动态更新
- 之后动态更新每次引用函数前手动卸载模块然后重载，实现修改文件的动态更新效果
- 然后修改 yaml 文件的部分移动到了 config 里

#### 消息适配器(adapter)

###### QQAPP

###### WECHAT

- 微信文章字符乱码:在使用json时没有自动转换为中文

### 逻辑功能(logic)

#### ai 对话(chat)

###### 知识库提取(kb)

*安装 Tesseract OCR*

- Windows 安装步骤：
- 下载 Tesseract 安装包（推荐官方发布）：
- 地址：https://github.com/tesseract-ocr/tesseract/releases
- 下载文件如：tesseract-ocr-w64-setup-5.3.1.20230401.exe
- 安装时注意勾选 Add to PATH，或者记住安装目录（比如 C:\Program Files\Tesseract-OCR）。
- 如果你没勾选添加 PATH，需手动添加：
- 打开「系统环境变量」 → 「系统变量」 → 找到 Path → 编辑 → 添加： `C:\Program Files\Tesseract-OCR`
  *安装 poppler-utils*
- pdftotext 是 poppler-utils 包的一部分，因此你需要确保已安装 poppler-utils 或相关工具。
- Windows 用户可以使用以下方式安装：
- 访问 poppler for Windows 下载并解压。
- 将解压后的 bin 目录（包含 pdftotext.exe）添加到系统的 PATH 环境变量中。
- 检查 pdftotext 是否正确安装：
- 打开命令提示符或 PowerShell，输入 pdftotext，看看是否能识别并执行该命令。

###### 知识库查询(kb)

- 不使用 faiss 而使用 sql，每次重复构建 pkl 费时

#### 指令功能(command)

###### 每日发言记录

- 通过get_group_member_info来刷新qq最新发言时间的缓存，之后通过get_group_member_list来获取最近发言时间，使用时间戳进行比较

#### 基础功能(infra)

###### 资讯获取

- 爬虫
- WeWeRss，，用微信读书接口进入，定期更新订阅公众号的文章
- [爬取公众号文章](https://blog.csdn.net/kuailebuzhidao/article/details/136490529)
- 豆瓣apikey

###### 表情包添加文字

- 使用pillow制作

### 界面(web)

#### 后端(backend)

###### 后端对比

- Uvicorn:采用 uvloop（一个高效的事件循环库）和 httptools（一个高性能的 HTTP 解析库），因此在 IO 密集型 的应用中性能非常出色。
  更专注于 高性能异步，尤其是 单节点应用。
- Hypercorn:可以使用 asyncio、trio 或 curio 作为其事件循环库，允许开发者根据需要选择不同的异步实现。
  相对来说更加灵活，适合需要 支持不同异步模式 的场景，如 trio 用户。
  多协议支持（包括 HTTP/2、HTTP/3 和 WebSocket）使其适合需要多协议支持的应用。
- 性能
- Uvicorn:基于 uvloop 和 httptools，优化了网络 I/O 操作，通常在 性能和响应速度 上稍占优势，尤其是在低延迟和高并发的场景下。
  是目前 最快 的异步 Web 服务器之一，特别适用于需要大量并发连接的应用。
- Hypercorn:虽然性能不错，但由于支持更多协议（如 HTTP/2、HTTP/3 等），它的性能通常略低于 uvicorn，尤其是在非常高并发的负载下。
  适合需要灵活性和多协议支持的应用，但如果对性能要求极高，uvicorn 会更具优势
- **flask配置静态资源一定要使用绝对路径**
- flask的调试模式会跟asyncio冲突
- 禁用fastapi的api显示、文档说明等

#### 前端

###### 文件预览

- 安装 [LibreOffice](https://www.libreoffice.org/donate/dl/win-x86_64/25.2.3/zh-CN/LibreOffice_25.2.3_Win_x86-64.msi)
- 添加`C:\Program Files\LibreOffice\program`进环境变量 path

### 小程序开发(qqapp)

- 小程序用户验证[参考文档](https://q.qq.com/wiki/develop/miniprogram/API/open_port/port_userinfo.html)
- 小程序管理员认证在 connect.qq.com 申请获取用户 unionid ，使得管理员认证唯一，取代了之前使用用户昵称的方式
- 小程序页面跳转使用 navigateBack 代替 To 来避免10个页面的上限，并且修改/删除后还能回到原光标处,现在程序运行非常快

#### 小程序图片压缩

- 参考代码：
- 压缩到50kb不影响缩略图观看
- 参考chatgpt的两个对话

### 相关知识

###### 接收ws信息的冲突

- 如果在发送消息后自动接收信息，在整个 ws 连接中即 napcat 连接函数下面：A 接收{B 发送，等待 C，接收 C},D 接收，则 B 发送的消息会被
  C 接收到；而在其他地方使用 msg_send：1.A 接收，D 接收；2.B 发送，等待 C，接收 C，C 本来要接收的消息会被 D 捕获

###### 快速开始脚本

- 使用 pytest 在开启 flask 或者其他长时间运行程序时，会出现 test 完成但主程序没有停止的情况，直接关闭命令行不会释放资源导致程序卡死
- pytest 的自带日志太多了，所以不采用 test

###### 后端启动相关

- flask 的 app.run(debug=True)会启动 werkzeug 的重载模式，设置信号量 signal.signal，而 python 无法在主线程之外使用信号量，故不能用
  debug

###### 任务退出逻辑

- 任务退出时，main 里面 gather 的各子任务收到退出信号取消，不触发 except 模块，直接执行 finally 逻辑；同时，各子任务创建的 n
  级子任务会先于一级子任务取消
- 每个任务取消前都会执行其 finally 逻辑

###### 异常捕获机制（退出时）

- main 里面会 print 之前捕获的异常
- main 里面创建的所有 task 的异常都会被捕获
- 但 task 自己使用 create_task 创建的子任务不受 main 管理
- 故取消时可能产生错误
- 如 init_app 里 create_task(server_serve())开启了 uvicorn 服务器，但这个任务的异常没有被处理，需要在创建的新任务上覆盖一个异常捕获器来处理
  KeyboardInterrupt 异常

```
async def init_serve():
    try:
        await server.serve()
    except KeyboardInterrupt:
        backend_logger.debug(f"后台服务停止", extra={"event": "运行日志"})
serve_task = asyncio.create_task(init_serve())
```

###### anaconda 环境和pycharm环境

- 在 pycharm 中，未命名的环境名为路径名
- 在 anaconda 中，未命名的环境会以路径显示且无名字，只能以路径调用，conda env list

###### 异步性能提升

- asyncio
- 所有（包括flask，一些常规的函数）都使用异步，防止多个调用同一函数互相阻塞
- ws连接的on_message，多条之间会互相阻塞
- 调用异步计时器防止阻塞
- time.sleep(n)改成asyncio.sleep(n)
- requests.get()
- 进程、线程和协程：进程绕过全局解释器锁（GIL）实现真正的并行，线程通过通过操作系统调度实现并发，协程需要通过await来进行调度。如协程里写while
  true pass会卡死整个程序，而线程和进程不会
- 对于高并发类型的io处理使用协程（数据库读取，future变量等待，request请求），对于cpu密集型使用线程（ai处理运算）
- 协程在await执行结束后，会到协程队列末尾重新执行
- asyncio.gather当某个任务抛出异常后，如果没有try模块，则会终止一个任务，其他任务继续执行；若有，则会终止所有任务；当某个任务阻塞后，会阻塞所有任务的执行
- while True :await asyncio.sleep(1)这个是为了维持任务存在，但存在更好的方式来代替，如condition；像看门狗使用Event参数一直挂起，则在协程中不占用时间，而在observer线程中进行管理

###### grafana监控(已废弃)

- grafana 系列的配置[教程](service.md)

###### 事件驱动架构

- EDA

###### 电脑关屏自动重启

- 出现日志: Background Intelligent Transfer Service 服务的启动类型从 自动启动 更改为 按需启动。
- 搜索服务，Background Intelligent Transfer Service- 属性-启动类型-禁用
- 出现日志: 安装成功: Windows 成功安装了下列更新: Microsoft Defender Antivirus 的安全智能更新 - KB2267602（版本 1.433.10.0）- 当前频道（广泛）
- 可能是开启了火绒，Microsoft Defender Antivirus 更新失败，win+r 输入 gpedit.msc,计算机配置 > 管理模板 > Windows 组件 > Microsoft Defender 防病毒程序，选择关闭 Microsoft Defender 防病毒程序

###### 新闻相关

- b 站: https://socialsisteryi.github.io/bilibili-API-collect/docs/dynamic/nav.html#%E8%8E%B7%E5%8F%96%E5%AF%BC%E8%88%AA%E6%A0%8F%E5%8A%A8%E6%80%81%E5%88%97%E8%A1%A8
- b 站up空间: https://socialsisteryi.github.io/bilibili-API-collect/docs/dynamic/space.html
- b 站动态: https://socialsisteryi.github.io/bilibili-API-collect/docs/dynamic/all.html#%E8%8E%B7%E5%8F%96%E5%85%A8%E9%83%A8%E5%8A%A8%E6%80%81%E5%88%97%E8%A1%A8
- b 站搜索: https://socialsisteryi.github.io/bilibili-API-collect/docs/search/search_request.html#%E5%88%86%E7%B1%BB%E6%90%9C%E7%B4%A2-web%E7%AB%AF 
- b 站搜索:https://socialsisteryi.github.io/bilibili-API-collect/docs/search/search_response.html
- 视频短链 https://b23.tv/av80433022
- bv 转 av https://socialsisteryi.github.io/bilibili-API-collect/docs/misc/bvid_desc.html#python