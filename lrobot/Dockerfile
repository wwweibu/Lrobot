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

# 仅拷贝主控文件
COPY main.py .
# 除 adapter 外的 msg 模块
COPY ./message/handler ./message/handler
# web 模块的 FastAPI 部分
COPY ./web/backend ./web/backend

# logic, adapter, storage 会通过挂载方式加载
CMD ["python", "main.py"]
