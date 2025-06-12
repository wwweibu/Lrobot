Atlas os 配置指南
1. 确保你有两台电脑，不建议配置常用的电脑，本方法需要一个 U 盘，且电脑必须要两个 USB 口
2. 访问 [win11 规格要求](https://www.microsoft.com/zh-cn/windows/windows-11-specifications#table1) 确保能使用 win11 
3. 访问 [Atlas 配置指南页](https://docs.atlasos.net/getting-started/installation/#__tabbed_1_1)，点击 Down load Windows 11 24H2，选择 Chinese Simplified，点击下载
4. 下载最新版本的 [ventoy](https://github.com/ventoy/Ventoy/releases/)，点击 download now，选择 windows.zip 下载
5. 运行 Ventoy2Disk.exe，插入 U 盘并选择，安装
6. 将下载的 iso 文件复制进 U 盘
7. 要安装的电脑断网，插入 U 盘，windows 更新-高级选项-恢复-高级启动（或者其他进入 bios 的方式）
8. 选择使用设备，使用 U 盘，回车，Boot in normal mode，回车
9. 进入安装界面（不知道为什么没有鼠标），两次回车，按下下，选中以前版本的更新程序，回车，选择下一页（必须要外接鼠标，应该是触摸板被禁用了），选择现在安装，选择我没有产品密钥，选择 windows11 专业版，接受下一步，自定义安装
10. 删掉所有分区（建议详细查看配置指南再进行操作），选择驱动器 0 未分配的空间，选择下一页，等待安装
11. 安装完成后选择国家，选择输入法，按下 shift+F10，输入 start ms-cxh:localonly 然后回车，配置账号密码以及安全问题，关闭所有隐私设置选择接受，选择下一步
12. 联网，打开设置并更新 windows，此时可以拔掉 U 盘，多次更新重启到全部更新完毕
13. 访问[官网](https://atlasos.net/)(建议用非重装的电脑访问)点击 get started now，选择 I'm following the guide，下载 AME Wizard 和 AtlasPlaybook
14. 打开 wizard，拖入 playbook，选择 run action,open windows security,然后全关了，选择 next-next-I agree-select options-next-next-next-next-next-选谷歌-next
15. 其他设置：Atlas 文件夹里面 Search Indexing，关闭搜索索引，sleep 禁用休眠，system restore 禁用系统还原
16. 最好下载 directx,driver booster 更新驱动
