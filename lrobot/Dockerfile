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

# 启用 UTF-8 中文环境，解决 soffice 中文路径问题
RUN apt-get update && apt-get install -y --no-install-recommends locales && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8

# 配置 MongoDB 4.4 源并安装工具
RUN mkdir -p /etc/apt/keyrings && \
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc \
        | gpg --dearmor -o /etc/apt/keyrings/mongodb-org-4.4.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/mongodb-org-4.4.gpg arch=amd64] \
        https://repo.mongodb.org/apt/debian bullseye/mongodb-org/4.4 main" \
        > /etc/apt/sources.list.d/mongodb-org-4.4.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends mongodb-database-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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
