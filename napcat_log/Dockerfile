FROM docker.m.daocloud.io/library/python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        --timeout 120 --retries 10 \
        -r requirements.txt \

COPY log.py .
CMD ["python", "log.py"]