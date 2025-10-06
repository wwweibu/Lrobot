FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝主控文件
COPY command.py .

# 复制密钥
COPY lrobot.pem /app/storage/lrobot.pem
RUN chmod 600 /app/storage/lrobot.pem


CMD ["python", "command.py"]