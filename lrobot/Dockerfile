FROM python:3.11-slim

WORKDIR /app

# 覆盖写入清华源
RUN echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware' > /etc/apt/sources.list && \
    echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \
    echo 'deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware' >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libreoffice \
        unoconv \
        fonts-noto-cjk \
        default-mysql-client \
        ffmpeg \
        wget \
        gnupg

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
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝主控文件
COPY main.py .
# msg 模块
COPY ./message ./message
# web 模块的 FastAPI 部分
COPY ./web/backend ./web/backend

# logic, storage 会通过挂载方式加载
CMD ["python", "main.py"]
