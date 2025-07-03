FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 拷贝主控文件
COPY command.py .

CMD ["python", "command.py"]