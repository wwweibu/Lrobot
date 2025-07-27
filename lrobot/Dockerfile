FROM python:3.11

WORKDIR /app

# .代表/app目录
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装 LibreOffice 和其他依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    unoconv \
    fonts-noto-cjk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 MySQL 客户端
RUN apt update && apt install -y default-mysql-client

# 安装 MongoDB dump 工具
RUN apt install -y wget gnupg \
 && wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - \
 && echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" > /etc/apt/sources.list.d/mongodb-org-6.0.list \
 && apt update && apt install -y mongodb-database-tools

# 仅拷贝主控文件
COPY main.py .
# msg 模块
COPY ./message ./message
# web 模块的 FastAPI 部分
COPY ./web/backend ./web/backend

# logic, storage 会通过挂载方式加载
CMD ["python", "main.py"]
