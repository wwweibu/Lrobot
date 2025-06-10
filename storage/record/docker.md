#### 相关知识
Docker: Docker 是一个开源的应用容器引擎，采用容器化技术，比虚拟机占用更少资源
Image: 只读的容器模板，包含代码、运行时、库文件、环境变量和配置文件，主要由 Dockerfile 文件定义，也可以从镜像仓库拉取
Registry: 存储和分发镜像的仓库，用于存储镜像
Container: 镜像的实例，由 Image 创建，一个镜像可创建多个容器。容器可以被创建、启动、停止、删除、暂停
Dockerfile: 一个文本文件，包含创建镜像的所有指令
Compose: 定义和运行多容器的工具
命令: 
- `docker run` 运行容器 
- `docker build` 构建镜像
- `docker pull` 拉取镜像
- `docker ps` 查看容器状态
- `dokcer exec` 在运行容器中执行命令
- `docker images` 列出本地主机上的镜像
- `-d` 后台运行容器

#### 安装方法
- Linux:
```
# 下载并执行Docker官方安装脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker服务
sudo systemctl start docker

# 下载 Docker Compose 当前稳定版本
sudo curl -L "https://github.com/docker/compose/releases/download/v2.2.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
- Windows
下载[Docker Desktop]( https://docs.docker.com/desktop/install/windows-install/)
如果卡在 'verifying packages' 则需要切换网络环境
选择启用 WSL 2 和 Hyper-V，跳过登录 Docker Hub 账户