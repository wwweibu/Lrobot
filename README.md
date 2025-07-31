# LRobot

<img src="storage/file/firefly/firefly.png" alt="Firefly takes over the world" width="100"/>

---

## ***LR232*** & ***LR5921***

<div style="display: flex; justify-content: flex-start; align-items: flex-start;">
    <img src="storage/file/firefly/L.png" alt="LR232" width="100">
    <img src="storage/file/firefly/R.gif" alt="LR5921" width="100">
    <img src="storage/file/firefly/app1.jpg" alt="QQAPP" width="100">
</div>

[![版本](https://badgen.net/badge/version/7.2.1/ffb3c2)](#)
[![Python](https://badgen.net/badge/language/Python/blue)](#)
[![Python 版本](https://badgen.net/badge/python/3.11/ffb3c2)](#)
[![Docker](https://badgen.net/badge/platform/Docker/2496ed)](#)

**鸣谢:**   
>![AI](https://badgen.net/badge/icon/🤖?label=AI) &nbsp; ![相关项目](https://badgen.net/badge/icon/🔗?label=相关项目) &nbsp; ![小马](https://badgen.net/badge/icon/🎨?label=小马) &nbsp; ![内阁](https://badgen.net/badge/icon/🏛?label=内阁) &nbsp; ![推协](https://badgen.net/badge/icon/🕵?label=推协) &nbsp; ![微部](https://badgen.net/badge/icon/🎭?label=微部) &nbsp;

---

**本项目仅作为学习研究使用，切勿用于非法用途**
[项目文档](https://wwweibu.github.io/Lrobot/)

---

## 写在前面

- “天下文章一大抄”，接触了越来越多的项目后，愈发感到他人项目的复杂性及个人精力的有限
- 所以非常感谢提供代码的各位大佬
- 以及，“天下代码一大包”，所谓的多平台，就是把每种不同的标准包起来，丢掉不需要的。如果包一层不行，就再包一层
- 本代码致力于为多平台聊天机器人提供一种解决思路，同时也是见证自己学习成长的过程
- 刚接触代码的人可以从*快速开始*开始，在部署中逐渐了解相关知识；
- 代码大佬也可以根据此教程以及代码中的注释，从详细的架构说明、功能描述、页面前后端中选择自己需要的部分引用；
- 以及，由于本人没有 AI 厉害，所以**本项目中所有的前端代码均由 AI 生成，内容仅供参考，请仔细甄别**
- 主要想为大家省去读文档、调接口的时间，希望能一起进步。~另外，官方的文档回复真的很慢；逆向的大佬们真的很强~

## 项目简介

- LRobot 是一款基于 Python 开发的辅助聊天工具，主要服务于社团管理。项目围绕各消息平台构建消息处理和管理系统，涵盖QQ、微信、B站、QQ 小程序、网页五个平台的界面和指令功能
- 依据快速开始中的步骤选择需要的平台部署项目，筛选并修改需要的指令，设计对应的页面，开发新的功能
- 项目有各步骤详细的说明及教学，虽然涉及到账号申请、部署、添加数据等内容比较麻烦，但完成后可以发挥想象，设计更多更有趣的功能；同时给有一定经验的开发者做一个参考
- 项目将持续更新……
- ~*可以猜猜为什么叫这个名*~
- 项目文档地址 https://wwweibu.github.io/Lrobot

---

## 快速开始
#### 基础知识
1. 项目采用 docker 运行，即项目可以屏蔽环境差异，在任何环境下快速部署
2. 本项目目的为集成各平台消息服务,实现自定义功能。目前搭载 QQ、Napcat、微信公众平台、B 站、QQ 小程序五个平台的机器人
3. 以下均用 LR232(qqbot),LR5921(Napcat),WECHAT(wechat),BILI(bilibili),QQAPP(qqapp) 代替各平台

#### 准备工作
1. 安装好 docker 环境，参考[docker 配置教程](../相关教程/docker配置#安装方法)
2. 关于各平台的功能简介、注册方法跳转[平台配置教程](../相关教程/平台配置#平台配置指南)，其中的回调地址验证可以在配置完服务器后进行
3. 将 storage/yml 中含 copy 后缀的文件重命名并去掉 copy(其中 secret.yaml 需要根据文件中的配置提示配置各平台参数，并配置服务器和域名)
4. 在服务器上配置 nginx，将 storage/nginx.conf 推送到服务器上作为 nginx 配置文件，参考[服务器配置教程](../相关教程/服务器配置#配置服务器)

#### 项目运行
1. 下载项目 `git clone https://github.com/wwweibu/Lrobot.git`
2. 建议浏览一遍[平台配置教程](../相关教程/平台配置)和[服务器配置教程](../相关教程/服务器配置)来了解本项目，项目文件架构可以[参考](./文件架构)
3. 为了省钱，本项目采用`本地运行+服务器+域名的模式`，使用最低配置的服务器，其他模式也可以通过调整配置来实现
4. 在 secret.yaml 中填写 SERVER_IP、SERVER_USERNAME，并放置服务器密钥于 storage/lrobot.pem 处
5. 填写平台相关信息（ID、SECRET）即代表启用该平台服务，留空（注意不是整条注释掉）则不启用
6. 将 secret_copy.py 更名成 secret.py，并编写路径替换函数 secret 替换掉默认 secret，用于保护你的平台路径（防止从域名/LR232路径处直接截取你的流量）
7. 进入项目目录`cd Lrobot`（注意里面还有一个 lrobot 文件夹，进入的是外面的）
8. `docker compose up --build -d napcat` 启动 napcat 服务（linux 需要加 sudo，下同）
  - 扫码登录(如果 docker 里的二维码扫描不了打开 storage/napcat/cache 或访问[网址](http://127.0.0.1:6099/webui?token=napcat))
  - 访问 http://127.0.0.1:6099/webui?token=napcat 进行配置
  - 配置 HTTP 服务器，`启用-开启Debug-port:5921`
  - 配置 HTTP 客户端，`启用-开启 Debug-URL：http://lrobot:5922/LR5921/` （LR5921 如果配置了 secret 记得改成加密后的路径）-上报自身消息
  - 并在其他配置-登录配置里填写当前 QQ 以便快速登录
9. `docker compose up --build -d command` 启动服务器连接与转发
  - `docker exec -it command sh`进入容器
  - `chmod 600 /app/storage/lrobot.pem`
  - `ssh -i /app/storage/lrobot.pem username@ip` 连接服务器
  - 输入 yes，随后重启容器
10. 启动数据库服务
  - `docker compose up --build -d mysql`
  - `docker compose up --build -d mongodb` 
11. `docker compose up --build lrobot` 启动 lrobot 主服务，由于安装了 libreoffice，需要 5 分钟左右
12. 可以使用 `docker logs xx` 或者 Docker Desktop 查看容器内部日志

---

## 功能展示
[功能](https://wwweibu.github.io/Lrobot/docs/项目介绍/功能展示)

---

## 常见问题
#### Q:如何联系上开发者？
#### A:建议直接添加 QQ:3502644244，发消息或者邮箱都行。配置环境时的相关问题都会整理到这里。
#### Q:可以参与开发吗？
#### A:由于是个人项目，有什么其他功能想法或者优雅的代码书写方式都建议直接教我。当然，欢迎 PR
#### Q:为什么要开发这个项目？
#### A:由于协会传统萌发了开发机器人的想法，之后先后找到了 MYQQ、qqbot 和 LLOnebot、Napcat。官方 QQ 机器人框架限制过多，审核过程繁琐且一个月只能发四条主动消息，消息回复只能有五条，无法获取到消息发送者的 QQ （*就离谱*），获取群成员等群聊相关 API 还在等开发；个人 Napcat 启动器的缺点是发送消息太多可能被屏蔽，且不能输入''/''快速调出指令并 @ 机器人，每次查询指令比较繁琐。然后没有官方机器人 dau 达到500后的被动 markdown 功能，所以可以各取所长，以官方 QQ 机器人为主， NapCat 为辅搭建一个LRobot系统。首先是统一二者API，使用自定义的消息类以及自定义的消息发送逻辑实现。接着是逻辑处理，官方 QQ 机器人负责主要指令调用与回复，NapCat 负责信息查询（成员发言时间获取），群聊转私聊，发送额外消息。两个机器人通过群消息二合一来“激活”用户，同时通过数据库记录“状态”实现单用户多消息、多用户多消息的互通。之后又有了开发更多平台的机器人的想法，于是就有了目前的项目。

---

## 许可证

本项目采用混合许可证，包含：

- 自定义有限使用许可，仅限非商业及内部学习使用；
- 部分代码采用 MIT 许可证；
- 部分内容遵循 Creative Commons Attribution-NonCommercial 4.0 国际许可协议（禁止商业用途）；
- 项目依赖的 NapCat 服务采用其自定义有限再发布许可。

详细许可证请参见项目根目录 LICENSE 文件。

--

## ……

- [x] **QQ 机器人审核通过**
- [x] **信管局审核网址通过**
- [x] **小程序快点审核过**
- [x] **QQ 机器人指令审核快一点**
- [x] **设计两个谁都解不出来的头像**
- [x] **~~申请特例开启被动markdown消息失败~~**
- [x] **~~微信公众号申请个人认证失败~~**
- [x] **删除 msg_xxx 中的敏感信息**
- [x] **考虑给消息加一个结果 id，或者加在消息池里面，便于 future 获取结果**
- [x] **数据库分多个库，新增数据库连接池，添加失败回滚机制**
- [x] **增加审核模式应对 qq 平台审核，在功能判断时增加身份组**
- [x] **动态更新用单例类懒加载+watchdog 监听文件变更**
- [x] **审核和运行模式在 config 里配置**
- [x] **防止常见的 ddos 攻击**
- [x] **~~流量通过 cloudflare 代理并且将静态资源托管~~**
- [x] **项目正常运行后，删除环境并重新配置**
- [x] **把小米球的命令也做成函数，写明白配置方法**
- [x] **napcat 检测输入状态**
- [x] **采用一种方法能在主机上测试新功能（测试接口√）**
- [x] **项目许可证**
- [x] **~~每个适配器创建连接池~~**
- [x] **在发送消息的获取、每日打卡统计等地方引入 future 模式，用一个函数完成解析 ws 接收的 echo 的功能**
- [x] **~~使用 Prometheus 和 Grafana 和 windows_exporter 和 loki 和 sql 监测性能、输出日志~~**
- [x] **~~服务器用于验证二级服务，域名用于搭建监控以及社团网站~~**
- [x] **~~向微信小程序迁移，调用蓝牙、NFC等接口。失败，无法使用QQ账号实现~~**
- [x] **数据库快照/天**
- [x] **~~统一的消息适配器，自动解析 json 格式~~**
- [x] **功能函数加载使用字典映射，在配置消息后自动重载字典，不用每次消息处理时加载模块**
- [x] **~~使用LR232_receive_module.LR232_receive()来重载各平台消息接收~~没必要**
- [x] **数据库优化**
- [x] **数据库读写和分库比较（结果：不如mysql），future和队列比较（结果：单文件队列，多文件future），日志存储与备份容灾（√）**
- [x] **~~网络异常处理：一个平台异常调用其他可用平台发送消息~~**
- [x] **重建gitee仓库**
- [x] **~~用路径来配置运行机的git动态更新~~**
- [x] **测试删除 storage 后的执行效果**
- [x] **日志使用装饰器，~~消息使用工厂模式~~**
- [x] **测试 LR5921 在消息发送失败后的日志**
- [x] **指令统一:"/+xxx"**
- [x] **详细解析系统各任务的处理方式与消息的处理顺序**
- [x] **公有平台的聚合；消息模块同异步的关系，消息方式；域名转发逻辑**、
- [x] **考虑表情放在内容中统一处理**
- [x] **测试各平台消息中的回车是否能正确处理**
- [x] **~~使用 Redis 存热数据~~**
- [x] **用装饰器来代替重复的 if 和日志输出**
- [ ] **更新 bili 和 wechat 的多种消息处理**
- [ ] **重新解析lr5921的消息返回值（200不一定成功）**
- [ ] **LR232使用发送1、2、3的机制来回复同一消息**
- [ ] **消息池添加keep字段**
- [ ] **LR232不能直接上传文件了，只能文件分享**
- [ ] **等到 Agent 完成重新编辑 model.md 部分**
- [ ] **检查 B 站 cookie 是否要刷新以及刷新（如果频繁掉线的话）**
- [ ] **concurrent.futures.ProcessPoolExecutor能突破GIL限制，突破GIL锁和单线程限制，配置更高级的python运行环境**
- [ ] **p = psutil.Process(os.getpid()) p.cpu_affinity([0, 1]) p.nice(psutil.HIGH_PRIORITY_CLASS)**
- [ ] **Flask 查询时图片读取的优化（集体读取？）**
- [ ] **蓝绿部署？**
- [ ] **微信消息处理在下一个请求到来前可以成功回复消息（<5s)，然后一般会发送两个请求（有时三个），可以实现14s内的无延迟通话**
- [ ] **第一次内测顺利**
- [ ] **刷DAU拿到被动markdown消息**
- [ ] **在@5921后面直接跟上表情包会被识别成text但处理后跟mface类型相同**
- [ ] **msg_get 返回消息段数组，需要更改函数**
- [ ] **看看 Dify**
- [ ] **小程序发送消息数组，但消息内容必须是str**
- [ ] **内存管理优化**
- [ ] **内存映射加速**
- [ ] **python 分配多核**
