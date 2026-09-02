# LRobot OOM 与海龟汤排查报告

日期：2026-09-03（Asia/Shanghai）

## 结论

网站不可访问的直接原因是 LRobot 容器内 Python 进程被 Linux OOM Killer 杀死，而容器当时没有重启策略，nginx 随即失去 `127.0.0.1:5922` 上游并返回 502。

这不是“海龟汤题库太大”造成的单点故障，而是 2 GiB 主机长期资源超配与多个无界生命周期叠加的结果：

1. `FutureManager` 会永久保留已完成、超时或无人等待的回执对象，是 LRobot 长期增长最明确的代码泄漏。
2. 日志队列、消息队列以及逐消息 `create_task` 没有硬上限，在外部服务变慢时会继续积压。
3. AI 海龟汤实际通过 Codex Bridge 的 `/v1/soup` 使用 `gpt-5.3-codex-spark`；bridge 的常驻 app-server、无界串行 Promise 队列和未统一回收的 RPC/turn Map 会额外占用内存。
4. MongoDB 的日志查询索引共约 2.76 GB，其中全文索引约 2.31 GB；当前日志查询页面未使用，因此这些二级索引只有磁盘和缓存成本。
5. LRobot 容器的 Docker JSON 日志约 798 MB，运行中的旧容器没有应用仓库里已有的轮转配置。

海龟汤是最近新增且高频调用 Codex 的触发因素，但 2026-09-02 被杀的进程仍是已经增长到约 1.23 GiB 的 LRobot Python；应同时修复 LRobot 与 bridge，不能把两次 OOM 混为一次。

## 证据时间线

| 时间 | 证据 | 判断 |
| --- | --- | --- |
| 2026-08-31 15:59 | 内核杀死 bridge 内 Codex 进程，匿名 RSS 约 451.7 MiB；systemd 记录服务峰值内存 488.0 MiB、swap 387.3 MiB | AI 海龟汤链路自身可形成显著内存压力 |
| 2026-09-02 17:30 后 | bridge 日志持续出现 Codex token 过期并约每 3 分钟重试 | 登录失效时旧 bridge 没有快速断路和退出 |
| 2026-09-02 19:00 | 内核杀死 LRobot Python，匿名 RSS 约 1.23 GiB、swap 约 143 MiB | 网站 502 的直接故障进程 |
| 故障期 | MySQL 约 369 MiB RSS/442 MiB swap，MongoDB 约 122 MiB RSS/437 MiB swap，宿主机 swap 长期 94%—99% | 2 GiB 宿主机整体余量不足 |
| 2026-09-03 排查 | Mongo `system_log` 2,922,088 条、逻辑数据约 6.00 GB、二级索引约 2.70 GiB | 大型日志库和索引进一步挤压磁盘/页缓存 |

历史日志没有 Python 堆快照，因此无法给每个对象精确分摊 1.23 GiB；上述根因级别按代码生命周期、OOM 时间线和重启后状态恢复共同判断。

## 本轮治理

### 1. Future 生命周期

- 正在等待的 Future 与“结果先到”的短期结果分开存放。
- 成功、异常、超时和取消后都从等待表移除。
- 早到结果设置 60 秒 TTL 和 1,000 条上限，超过上限按最旧项回收。
- 支持从其他线程安全地把结果交回主事件循环。
- 关机时统一取消等待项并清空缓存。

### 2. 队列与后台任务

- Mongo 日志队列默认上限 2,000；低级日志在满载时丢弃，警告/错误可替换最旧项。
- 单条数据库日志默认最多 65,536 字符，避免异常对象把队列放大。
- 消息接收队列和发送/适配器回调队列各默认 500，分别由 16 和 8 个固定 worker 消费。
- 两类队列分开，避免所有消息 worker 同时等待排在自己后面的发送回调而死锁。
- 持久消息池默认上限 20,000；后台任务默认上限 1,000，并统一跟踪异常及关机取消。
- 每 5 分钟记录一次不包含消息正文的资源边界指标。

### 3. AI 海龟汤

- 保留用户选择的方案 B：Codex `gpt-5.3-codex-spark` 仍为首选，DeepSeek 兼容接口只在 bridge 失败时兜底。
- LRobot 侧最多同时执行 2 个 AI 判断、最多等待 8 个请求；单问题 2,000 字符。
- 单局历史最多 20 轮/12,000 字符，全局最多 100 局，闲置 6 小时过期。
- 每局加串行锁，等待期间和 LLM 返回后都会复核缓存身份，防止旧局回答写入新局。
- 新开经典题、AI 猜中或手动结束时回收对话状态和 bridge session。
- 经典题随机选择改为数据库 `ORDER BY RAND() LIMIT 1`，不再把整张题库读入 Python。

### 4. Codex Bridge

- 知识问答和海龟汤分别设置 16/8 的排队上限。
- Codex CLI 输出按行解析，不再把完整 stdout 全部保存在内存；stderr 只留最后 64 KiB。
- 外部进程和单轮调用均有硬超时，超时后先 TERM、再 KILL。
- RPC、turn waiter、答案和完成状态均有数量上限与过期清理。
- 登录过期、用量耗尽和网络错误会打开带冷却期的断路器，并停止 app-server，避免定时重试常驻。
- 无请求 2 分钟后停止 app-server；systemd 同时设置 `MemoryHigh=256M`、`MemoryMax=384M` 和 `TasksMax=64`。

### 5. MongoDB 与 Docker

- 应用启动时不再创建日志查询二级索引。
- 删除前把完整索引定义保存在任务审计目录；需要恢复日志查询时可运行配套恢复脚本。
- LRobot 及其他 Compose 服务采用 `json-file` 轮转：单文件 10 MB、最多 3 个文件。
- LRobot 使用 `restart: unless-stopped` 并增加 HTTP healthcheck。

## 验证

- Python 修改文件编译通过；bridge 通过 `node --check`。
- Future 单元测试 8 项通过；AI 海龟汤单元测试 4 项通过。
- 100,000 个早到 Future 结果压测后只保留 1,000 个，等待表为 0。
- 消息队列压测中接收/回调队列均固定在 500；额外各 100 条被拒绝并计数，消息池固定为 1,000。
- bridge 的无 Codex 可执行文件冒烟测试快速返回 503、打开断路器并清空所有 RPC/turn 状态。

线上部署、真实登录、索引删除、日志轮转和持续观察结果在完成后补入本节。

## 运维观察

运行日志中的 `[资源边界]` 行可直接观察：

- `future.pending` 与 `future.early`
- `log_queue` / `log_queue_max`
- `message_queue`、`control_queue` 及其最大值
- `background_tasks` / `background_task_max`
- 各类 rejected/dropped/evicted 累计值

如果 `future.pending`、消息队列或后台任务长期接近上限，应优先检查对应外部平台的响应时间，而不是直接提高上限。若恢复 `/hjd/logs` 的高频复杂查询，应先按真实查询模式重建最少量索引，避免一次性恢复全部历史索引。

## 恢复入口

- Git 中保留本轮修改前的任务起点引用和服务器导出 bundle。
- 服务器原镜像在部署前保留回滚标签；原 bridge 与 systemd 单元已导出。
- MongoDB 二级索引可由审计目录中的 `restore_mongo_indexes.js` 重建。
- 完整操作、校验值和恢复命令见本任务审计目录的 `operations.md`。
