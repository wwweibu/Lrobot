FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

# 多源配置
RUN set -eux; \
    echo "配置多源列表..." > /etc/apt/sources.list && \
    cat > /etc/apt/sources.list <<'EOF'
deb https://mirrors.ustc.edu.cn/debian/ trixie main contrib non-free non-free-firmware
deb https://mirrors.ustc.edu.cn/debian/ trixie-updates main contrib non-free non-free-firmware
deb https://mirrors.ustc.edu.cn/debian-security/ trixie-security main contrib non-free non-free-firmware

deb https://mirrors.aliyun.com/debian/ trixie main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ trixie-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security/ trixie-security main contrib non-free non-free-firmware

deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie-updates main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ trixie-security main contrib non-free non-free-firmware
EOF


# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libreoffice \
        fonts-noto-cjk \
        default-mysql-client \
        ffmpeg \
        wget \
        gnupg

# 1. 安装基础工具 (wget, tar, ca-certificates)
# 确保你的基础源 (debian trixie) 是正常的，这一步通常没问题，因为你用了国内镜像
RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates tar gnupg && \
    rm -rf /var/lib/apt/lists/*

# 2. 定义版本号 (建议使用最新稳定版)
ENV TOOLS_VERSION=100.9.5

# 3. 直接下载 MongoDB Database Tools 二进制包
# 注意：虽然你的系统是 Trixie (Debian 13)，但 MongoDB 官方可能还没有发布专门的 "debian13" 包。
# 通常 "debian12" (bookworm) 或 "ubuntu2204" 的包在 Trixie 上也能完美运行。
# 这里我们优先尝试 debian12，如果不行可以换成 ubuntu2204。
RUN set -eux; \
    # 尝试下载 Debian 12 版本 (通常兼容 13)
    url="https://fastdl.mongodb.org/tools/db/mongodb-database-tools-debian12-x86_64-${TOOLS_VERSION}.tgz"; \
    if ! wget --timeout=30 -O /tmp/tools.tgz "$url"; then \
      # 如果 debian12 失败，降级尝试 ubuntu2204 (通用性强)
      url="https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2204-x86_64-${TOOLS_VERSION}.tgz"; \
      wget --timeout=30 -O /tmp/tools.tgz "$url"; \
    fi && \
    # 解压
    tar -zxvf /tmp/tools.tgz -C /tmp/ && \
    # 提取目录名 (自动适配版本号)
    dir_name=$(ls -d /tmp/mongodb-database-tools-* | head -n1) && \
    # 复制二进制文件到系统路径
    cp ${dir_name}/bin/* /usr/local/bin/ && \
    # 清理临时文件
    rm -rf /tmp/tools.tgz ${dir_name} && \
    # 验证安装
    mongodump --version

COPY requirements.txt .
RUN pip config set global.timeout 120; \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt \
    || pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt \
    || pip install --no-cache-dir -i https://pypi.douban.com/simple/ -r requirements.txt \
    || pip install --no-cache-dir -i https://pypi.org/simple/ -r requirements.txt

# 拷贝主控文件
COPY main.py .
# msg 模块
COPY ./message ./message
# web 模块的 FastAPI 部分
COPY ./web/backend ./web/backend

# logic, storage 会通过挂载方式加载
CMD ["python", "main.py"]
