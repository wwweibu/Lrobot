FROM docker.m.daocloud.io/library/python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --timeout 120 --retries 10 \
    -r requirements.txt \
    || \
    pip install --no-cache-dir \
    -i https://pypi.douban.com/simple/ \
    --timeout 120 --retries 10 \
    -r requirements.txt

COPY log.py .
CMD ["python", "log.py"]